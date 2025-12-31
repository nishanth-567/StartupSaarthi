"""
Cross-encoder reranker for final result ranking.
"""

from typing import List, Dict, Any
import logging
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class Reranker:
    """
    Cross-encoder reranker for improving retrieval quality.
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize reranker with cross-encoder model.
        
        Args:
            model_name: HuggingFace model name for cross-encoder
        """
        self.model_name = model_name
        self.model = None
        self.loaded = False
    
    def load_model(self):
        """Load cross-encoder model."""
        try:
            logger.info(f"Loading cross-encoder model: {self.model_name}")
            self.model = CrossEncoder(self.model_name)
            self.loaded = True
            logger.info("Cross-encoder loaded successfully")
        except Exception as e:
            logger.error(f"Error loading cross-encoder: {e}", exc_info=True)
            raise
    
    async def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank results using cross-encoder.
        
        Args:
            query: Original query string
            results: List of retrieval results to rerank
            top_k: Number of top results to return
        
        Returns:
            Reranked results with rerank_score added
        """
        if not results:
            return []
        
        if not self.loaded:
            self.load_model()
        
        try:
            # Prepare query-document pairs for cross-encoder
            pairs = [[query, result["content"]] for result in results]
            
            # Get cross-encoder scores (batch inference)
            scores = self.model.predict(pairs, show_progress_bar=False)
            
            # Add scores to results
            for result, score in zip(results, scores):
                result["rerank_score"] = float(score)
            
            # Sort by rerank score descending
            reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
            
            # Return top-k
            top_results = reranked[:top_k]
            
            logger.info(f"Reranked {len(results)} results → top {len(top_results)}")
            
            return top_results
            
        except Exception as e:
            logger.error(f"Error during reranking: {e}", exc_info=True)
            # Fallback: return original results
            return results[:top_k]


# Global reranker instance
_reranker_instance = None


def get_reranker() -> Reranker:
    """Get or create global reranker instance."""
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = Reranker()
        _reranker_instance.load_model()
    return _reranker_instance
