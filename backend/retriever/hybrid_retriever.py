"""
Hybrid retriever combining FAISS (dense) and BM25 (sparse) retrieval.
"""

from typing import List, Dict, Any, Optional
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from rank_bm25 import BM25Okapi

from backend.config import settings

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid retriever using both dense (FAISS) and sparse (BM25) retrieval.
    """
    
    def __init__(self):
        """Initialize retriever with embedding model and indices."""
        self.embedding_model = None
        self.faiss_index = None
        self.bm25_index = None
        self.chunk_metadata = []  # Stores metadata for each chunk
        self.loaded = False
    
    def load_indices(self):
        """Load FAISS and BM25 indices from storage."""
        try:
            # Load embedding model
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            
            # Load FAISS index
            if settings.faiss_index_path.exists():
                faiss_index_file = settings.faiss_index_path / "index.faiss"
                metadata_file = settings.faiss_index_path / "metadata.pkl"
                
                if faiss_index_file.exists() and metadata_file.exists():
                    self.faiss_index = faiss.read_index(str(faiss_index_file))
                    with open(metadata_file, "rb") as f:
                        self.chunk_metadata = pickle.load(f)
                    logger.info(f"Loaded FAISS index with {self.faiss_index.ntotal} vectors")
                else:
                    logger.warning(f"FAISS index files not found at {settings.faiss_index_path}")
            else:
                 logger.warning(f"FAISS index directory not found: {settings.faiss_index_path}")
            
            # Load BM25 index
            if settings.bm25_index_path.exists():
                with open(settings.bm25_index_path, "rb") as f:
                    bm25_data = pickle.load(f)
                    self.bm25_index = bm25_data["index"]
                    # BM25 should use same metadata as FAISS
                logger.info(f"Loaded BM25 index with {len(self.bm25_index.doc_freqs)} documents")
            
            self.loaded = True
            logger.info("Hybrid retriever loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading indices: {e}", exc_info=True)
            raise
    
    async def retrieve_dense(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Dense retrieval using FAISS vector search.
        
        Args:
            query: Query string
            top_k: Number of results to retrieve
        
        Returns:
            List of retrieval results with chunk_id, content, metadata, and score
        """
        if not self.loaded or self.faiss_index is None:
            logger.warning("FAISS index not loaded, returning empty results")
            return []
        
        try:
            # Encode query
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            
            # Search FAISS index
            distances, indices = self.faiss_index.search(query_embedding, top_k)
            
            # Build results
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.chunk_metadata):
                    metadata = self.chunk_metadata[idx]
                    results.append({
                        "chunk_id": metadata["chunk_id"],
                        "content": metadata["content"],
                        "metadata": metadata.get("metadata", {}),
                        "dense_score": float(distance)
                    })
            
            logger.info(f"Dense retrieval: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in dense retrieval: {e}", exc_info=True)
            return []
    
    async def retrieve_sparse(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """
        Sparse retrieval using BM25 keyword matching.
        
        Args:
            query: Query string
            top_k: Number of results to retrieve
        
        Returns:
            List of retrieval results with chunk_id, content, metadata, and score
        """
        if not self.loaded or self.bm25_index is None:
            logger.warning("BM25 index not loaded, returning empty results")
            return []
        
        try:
            # Tokenize query (simple whitespace tokenization)
            query_tokens = query.lower().split()
            
            # Get BM25 scores
            scores = self.bm25_index.get_scores(query_tokens)
            
            # Get top-k indices
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            # Build results
            results = []
            for idx in top_indices:
                if idx < len(self.chunk_metadata):
                    metadata = self.chunk_metadata[idx]
                    results.append({
                        "chunk_id": metadata["chunk_id"],
                        "content": metadata["content"],
                        "metadata": metadata.get("metadata", {}),
                        "sparse_score": float(scores[idx])
                    })
            
            logger.info(f"Sparse retrieval: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in sparse retrieval: {e}", exc_info=True)
            return []
    
    async def retrieve_hybrid(self, query: str, top_k: int = 20) -> Dict[str, Any]:
        """
        Perform hybrid retrieval (both dense and sparse).
        
        Args:
            query: Query string
            top_k: Number of results to retrieve from each method
        
        Returns:
            Dictionary with dense_results and sparse_results lists
        """
        if not self.loaded:
            self.load_indices()
        
        # Retrieve from both methods
        dense_results = await self.retrieve_dense(query, top_k)
        sparse_results = await self.retrieve_sparse(query, top_k)
        
        return {
            "dense_results": dense_results,
            "sparse_results": sparse_results
        }


# Global retriever instance
_retriever_instance: Optional[HybridRetriever] = None


def get_retriever() -> HybridRetriever:
    """Get or create global retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = HybridRetriever()
        _retriever_instance.load_indices()
    return _retriever_instance
