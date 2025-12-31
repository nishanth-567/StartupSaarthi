
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from backend.graph.query_graph import execute_query_graph
from backend.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_restriction():
    print("🔒 Verifying Domain Restriction...")
    
    # Check if indices exist (needed for pipeline to run without error)
    if not settings.faiss_index_path.exists():
        print("⚠️  faiss_index not found. Pipeline might return empty context (which is good for this test).")

    # Test General Knowledge Query
    query = "What is the capital of France?"
    print(f"\n❓ Asking prohibited question: '{query}'")
    
    try:
        result = await execute_query_graph(query=query)
        answer = result["answer"]
        print(f"\n🤖 Answer:\n{answer}\n")
        
        # Check for refusal
        refusals = [
            "I don't have enough information", 
            "sufficient", 
            "context",
            "cannot answer",
            "not found"
        ]
        
        if any(r.lower() in answer.lower() for r in refusals):
            print("✅ RESTRICTION WORKING: System refused to answer.")
        elif "Paris" in answer:
            print("❌ RESTRICTION FAILED: System answered 'Paris'.")
        else:
            print("⚠️  Unclear result. Please check answer manually.")

    except Exception as e:
        print(f"❌ Error during verification: {e}")

if __name__ == "__main__":
    asyncio.run(verify_restriction())
