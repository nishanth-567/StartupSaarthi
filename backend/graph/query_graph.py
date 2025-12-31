"""
LangGraph-based query execution pipeline.
Orchestrates: Language Detection → Translation → Retrieval → RRF → Reranking → LLM
"""

from typing import Dict, Any, Optional, TypedDict
import logging
from langgraph.graph import StateGraph, END

from backend.utils.language_utils import detect_language
from backend.utils.translation_pipeline import get_translation_pipeline
from backend.retriever.hybrid_retriever import get_retriever
from backend.retriever.rrf import reciprocal_rank_fusion
from backend.retriever.reranker import get_reranker
from backend.llm.llm_client import get_llm_client
from backend.config import settings

logger = logging.getLogger(__name__)


class QueryState(TypedDict):
    """State for query processing graph."""
    query: str
    original_query: str
    detected_language: str
    language_override: Optional[str]
    deterministic: bool
    translated_query: Optional[str]
    dense_results: list
    sparse_results: list
    fused_results: list
    reranked_results: list
    answer: str
    sources: list
    error: Optional[str]


async def detect_language_node(state: QueryState) -> QueryState:
    """Detect query language."""
    try:
        if state.get("language_override"):
            detected = state["language_override"]
            logger.info(f"Using language override: {detected}")
        else:
            detected = detect_language(state["query"])
        
        state["detected_language"] = detected
        state["original_query"] = state["query"]
        
        logger.info(f"Language detected: {detected}")
        
    except Exception as e:
        logger.error(f"Error in language detection: {e}")
        state["detected_language"] = "en"
    
    return state


async def translate_node(state: QueryState) -> QueryState:
    """Optionally translate query to English."""
    try:
        translation_pipeline = get_translation_pipeline()
        
        if translation_pipeline.enabled:
            translated = await translation_pipeline.translate_query(
                state["query"],
                state["detected_language"]
            )
            
            if translated:
                state["translated_query"] = translated
                state["query"] = translated  # Use translated query for retrieval
                logger.info("Using translated query for retrieval")
        
    except Exception as e:
        logger.error(f"Error in translation: {e}")
    
    return state


async def retrieve_node(state: QueryState) -> QueryState:
    """Hybrid retrieval (FAISS + BM25)."""
    try:
        retriever = get_retriever()
        
        results = await retriever.retrieve_hybrid(
            query=state["query"],
            top_k=settings.top_k_retrieval
        )
        
        state["dense_results"] = results["dense_results"]
        state["sparse_results"] = results["sparse_results"]
        
        logger.info(f"Retrieved: {len(state['dense_results'])} dense, {len(state['sparse_results'])} sparse")
        
    except Exception as e:
        logger.error(f"Error in retrieval: {e}")
        state["error"] = str(e)
        state["dense_results"] = []
        state["sparse_results"] = []
    
    return state


async def fusion_node(state: QueryState) -> QueryState:
    """Reciprocal Rank Fusion."""
    try:
        fused = reciprocal_rank_fusion(
            retrieval_results=[state["dense_results"], state["sparse_results"]],
            k=settings.rrf_k
        )
        
        state["fused_results"] = fused
        
        logger.info(f"Fused results: {len(fused)}")
        
    except Exception as e:
        logger.error(f"Error in fusion: {e}")
        state["error"] = str(e)
        state["fused_results"] = []
    
    return state


async def rerank_node(state: QueryState) -> QueryState:
    """Cross-encoder reranking."""
    try:
        reranker = get_reranker()
        
        # Use original query for reranking (not translated)
        reranked = await reranker.rerank(
            query=state["original_query"],
            results=state["fused_results"],
            top_k=settings.top_k_rerank
        )
        
        state["reranked_results"] = reranked
        
        logger.info(f"Reranked to top {len(reranked)}")
        
    except Exception as e:
        logger.error(f"Error in reranking: {e}")
        state["error"] = str(e)
        # Fallback: use fused results
        state["reranked_results"] = state["fused_results"][:settings.top_k_rerank]
    
    return state


async def generate_node(state: QueryState) -> QueryState:
    """Generate answer using LLM."""
    try:
        llm_client = get_llm_client()
        
        # Validate context
        if not state["reranked_results"]:
            logger.warning("No context available for generation")
            state["answer"] = "I don't have enough information to answer this accurately based on the available documents."
            state["sources"] = []
            return state

        answer = await llm_client.generate_answer(
            query=state["original_query"],
            context_chunks=state["reranked_results"],
            language=state["detected_language"],
            deterministic=state["deterministic"]
        )
        
        state["answer"] = answer
        
        # Build sources list
        sources = []
        for i, chunk in enumerate(state["reranked_results"], 1):
            metadata = chunk.get("metadata", {})
            sources.append({
                "source_id": i,
                "document": metadata.get("document", "Unknown"),
                "page": metadata.get("page"),
                "section": metadata.get("section"),
                "content_snippet": chunk.get("content", "")[:200],
                "metadata": metadata
            })
        
        state["sources"] = sources
        
        logger.info("Answer generated successfully")
        
    except Exception as e:
        logger.error(f"Error in generation: {e}")
        state["error"] = str(e)
        state["answer"] = "Error generating answer. Please try again."
        state["sources"] = []
    
    return state


# Build LangGraph
def build_query_graph():
    """Build query processing graph."""
    
    workflow = StateGraph(QueryState)
    
    # Add nodes
    workflow.add_node("detect_language", detect_language_node)
    workflow.add_node("translate", translate_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("fusion", fusion_node)
    workflow.add_node("rerank", rerank_node)
    workflow.add_node("generate", generate_node)
    
    # Add edges
    workflow.set_entry_point("detect_language")
    workflow.add_edge("detect_language", "translate")
    workflow.add_edge("translate", "retrieve")
    workflow.add_edge("retrieve", "fusion")
    workflow.add_edge("fusion", "rerank")
    workflow.add_edge("rerank", "generate")
    workflow.add_edge("generate", END)
    
    return workflow.compile()


# Global graph instance
_graph = None


async def execute_query_graph(
    query: str,
    deterministic: bool = False,
    language_override: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute query through LangGraph pipeline.
    
    Args:
        query: User query
        deterministic: Use deterministic mode
        language_override: Override detected language
    
    Returns:
        Dictionary with answer, sources, detected_language
    """
    global _graph
    if _graph is None:
        _graph = build_query_graph()
    
    # Initialize state
    initial_state: QueryState = {
        "query": query,
        "original_query": query,
        "detected_language": "en",
        "language_override": language_override,
        "deterministic": deterministic,
        "translated_query": None,
        "dense_results": [],
        "sparse_results": [],
        "fused_results": [],
        "reranked_results": [],
        "answer": "",
        "sources": [],
        "error": None
    }
    
    # Execute graph
    final_state = await _graph.ainvoke(initial_state)
    
    return {
        "answer": final_state["answer"],
        "sources": final_state["sources"],
        "detected_language": final_state["detected_language"]
    }
