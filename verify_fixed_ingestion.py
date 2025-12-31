
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from backend.retriever.hybrid_retriever import get_retriever
from backend.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_indices():
    print("🔍 Verifying Indices and Retrieval...")
    
    # Check if storage exists
    if not settings.storage_path.exists():
        print("❌ Storage directory not found!")
        return
        
    # Initialize retriever
    try:
        retriever = get_retriever()
        if not retriever.loaded:
            print("❌ Retriever failed to load indices.")
            return
            
        print(f"✅ Retriever loaded.")
        if retriever.faiss_index:
             print(f"   - FAISS Index: {retriever.faiss_index.ntotal} docs")
        if retriever.bm25_index:
             print(f"   - BM25 Index: {len(retriever.bm25_index.doc_freqs)} docs")

        # Test Retrieval
        query = "SIDBI"
        print(f"\n🧪 Testing Retrieval for query: '{query}'")
        results = await retriever.retrieve_hybrid(query, top_k=3)
        
        dense_hits = len(results.get("dense_results", []))
        sparse_hits = len(results.get("sparse_results", []))
        
        print(f"   - Dense Hits: {dense_hits}")
        print(f"   - Sparse Hits: {sparse_hits}")
        
        if dense_hits > 0 or sparse_hits > 0:
            print(f"\n✅ Verification SUCCESS: Data provides context for '{query}'!")
        else:
            print(f"\n⚠️ Verification WARNING: No results found for '{query}'.")

        # Test New Data (ESOP)
        query = "ESOP tax benefits"
        print(f"\n🧪 Testing Retrieval for query: '{query}'")
        results = await retriever.retrieve_hybrid(query, top_k=3)
        
        dense_hits = len(results.get("dense_results", []))
        sparse_hits = len(results.get("sparse_results", []))
        
        print(f"   - Dense Hits: {dense_hits}")
        print(f"   - Sparse Hits: {sparse_hits}")

        if dense_hits > 0 or sparse_hits > 0:
            print(f"\n✅ Verification SUCCESS: Data provides context for '{query}'!")
        else:
            print(f"\n⚠️ Verification WARNING: No results found for '{query}'.")

    except Exception as e:
        print(f"❌ Verification FAILED with error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_indices())
