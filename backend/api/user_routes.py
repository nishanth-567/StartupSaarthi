"""
User-facing API routes for querying the RAG system.
"""

from fastapi import APIRouter, HTTPException, status
from backend.api.models import QueryRequest, QueryResponse
from backend.graph.query_graph import execute_query_graph
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Main RAG query endpoint.
    
    Processes user queries through the complete pipeline:
    1. Language detection
    2. Optional translation
    3. Query expansion
    4. Hybrid retrieval (FAISS + BM25)
    5. Reciprocal Rank Fusion
    6. Cross-encoder reranking
    7. LLM answer generation
    
    Returns answer with inline citations and source list.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received query: {request.query[:100]}...")
        
        # Execute query through LangGraph pipeline
        result = await execute_query_graph(
            query=request.query,
            deterministic=request.deterministic,
            language_override=request.language
        )
        
        processing_time = time.time() - start_time
        result["processing_time_seconds"] = processing_time
        
        logger.info(f"Query processed successfully in {processing_time:.2f}s")
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages."""
    return {
        "supported_languages": [
            {"code": "en", "name": "English", "citation_format": "Source"},
            {"code": "hi", "name": "Hindi", "citation_format": "स्रोत"},
            {"code": "ta", "name": "Tamil", "citation_format": "மூலம்"},
            {"code": "te", "name": "Telugu", "citation_format": "మూలం"}
        ]
    }
