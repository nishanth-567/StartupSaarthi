"""
Index builder for FAISS and BM25.
"""

from typing import List, Dict, Any
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from rank_bm25 import BM25Okapi
import json
from pathlib import Path
import uuid

from backend.config import settings

logger = logging.getLogger(__name__)


class IndexBuilder:
    """Build and manage FAISS and BM25 indices."""
    
    def __init__(self):
        """Initialize index builder."""
        self.embedding_model = None
        self.chunk_metadata = []
    
    def load_embedding_model(self):
        """Load embedding model."""
        if self.embedding_model is None:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            self.embedding_model = SentenceTransformer(settings.embedding_model)
    
    async def build_indices(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build FAISS and BM25 indices from chunks.
        
        Args:
            chunks: List of chunks with content and metadata
        
        Returns:
            Dictionary with build statistics
        """
        if not chunks:
            logger.warning("No chunks provided for indexing")
            return {"faiss_vectors": 0, "bm25_documents": 0}
        
        self.load_embedding_model()
        
        # Add unique chunk IDs
        for i, chunk in enumerate(chunks):
            if "chunk_id" not in chunk:
                chunk["chunk_id"] = str(uuid.uuid4())
        
        # Build FAISS index
        faiss_stats = await self._build_faiss_index(chunks)
        
        # Build BM25 index
        bm25_stats = await self._build_bm25_index(chunks)
        
        # Save chunk metadata
        self.chunk_metadata = chunks
        
        return {
            "faiss_vectors": faiss_stats["vectors"],
            "bm25_documents": bm25_stats["documents"]
        }
    
    async def _build_faiss_index(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build FAISS index."""
        try:
            logger.info("Building FAISS index...")
            
            # Extract texts
            texts = [chunk["content"] for chunk in chunks]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = self.embedding_model.encode(
                texts,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype('float32'))
            
            # Save index
            settings.faiss_index_path.mkdir(parents=True, exist_ok=True)
            faiss.write_index(index, str(settings.faiss_index_path / "index.faiss"))
            
            # Save metadata
            with open(settings.faiss_index_path / "metadata.pkl", "wb") as f:
                pickle.dump(chunks, f)
            
            logger.info(f"FAISS index built: {index.ntotal} vectors")
            
            return {"vectors": index.ntotal}
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {e}", exc_info=True)
            return {"vectors": 0}
    
    async def _build_bm25_index(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build BM25 index."""
        try:
            logger.info("Building BM25 index...")
            
            # Tokenize documents (simple whitespace tokenization)
            tokenized_docs = [chunk["content"].lower().split() for chunk in chunks]
            
            # Create BM25 index
            bm25 = BM25Okapi(tokenized_docs)
            
            # Save index
            settings.bm25_index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(settings.bm25_index_path, "wb") as f:
                pickle.dump({"index": bm25}, f)
            
            logger.info(f"BM25 index built: {len(tokenized_docs)} documents")
            
            return {"documents": len(tokenized_docs)}
            
        except Exception as e:
            logger.error(f"Error building BM25 index: {e}", exc_info=True)
            return {"documents": 0}
    
    async def add_chunks_to_indices(self, new_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add new chunks to existing indices (incremental update).
        
        Args:
            new_chunks: New chunks to add
        
        Returns:
            Update statistics
        """
        # For simplicity, rebuild indices
        # In production, implement true incremental updates
        logger.info("Rebuilding indices with new chunks...")
        
        # Load existing chunks
        existing_chunks = []
        metadata_file = settings.faiss_index_path / "metadata.pkl"
        if metadata_file.exists():
            with open(metadata_file, "rb") as f:
                existing_chunks = pickle.load(f)
        
        # Combine and rebuild
        all_chunks = existing_chunks + new_chunks
        return await self.build_indices(all_chunks)
