
import asyncio
import os
import sys
import logging

# Add project root to path
sys.path.append(os.getcwd())

from backend.graph.query_graph import execute_query_graph
from backend.config import settings
from backend.retriever.hybrid_retriever import get_retriever

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

async def run_final_verification():
    print("🚀 STARTUPSAARTHI FINAL VERIFICATION (ROBUST)")
    print("=============================================")
    
    # 1. Environment Check
    print("\n[1/4] Checking Environment...")
    if not os.path.exists(".env"):
        print("❌ .env file missing")
        return
    
    if not settings.gemini_api_key or "your_gemini" in settings.gemini_api_key:
         print("❌ GEMINI_API_KEY is missing or default")
         return
    print("✅ Environment OK")

    # 2. Index Check
    print("\n[2/4] Checking Indices...")
    retriever = get_retriever()
    if not retriever.loaded:
         print("❌ Retriever failed to load")
         return
    print(f"✅ Indices loaded (FAISS: {retriever.faiss_index.ntotal if retriever.faiss_index else 0})")

    # 3. Functional Tests (Running one by one)
    print("\n[3/4] Testing RAG Pipeline...")
    
    # Test 1: Valid Query 1
    q1 = "What are the tax exemptions for startups?"
    print(f"\n   Testing: '{q1}'")
    try:
        r1 = await execute_query_graph(q1)
        if len(r1["answer"]) > 20: 
            print("   ✅ Answered successfully") 
        else: 
            print("   ❌ Failed to answer")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: Invalid Query (Restriction)
    q2 = "Who is the Prime Minister of India?"
    print(f"\n   Testing Restriction: '{q2}'")
    try:
        r2 = await execute_query_graph(q2)
        ans = r2["answer"].lower()
        if "refuse" in ans or "don't have" in ans or "cannot" in ans or "context" in ans:
             print("   ✅ Correctly Refused")
        else:
             print(f"   ❌ FAILED: Answered '{r2['answer'][:50]}...'")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n[4/4] Verification Complete.")

if __name__ == "__main__":
    try:
        asyncio.run(run_final_verification())
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\nCritical Error: {e}")
