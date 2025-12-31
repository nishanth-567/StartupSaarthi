
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
logging.basicConfig(level=logging.ERROR) # Only show errors to keep output clean for summary
logger = logging.getLogger(__name__)

async def run_final_verification():
    print("🚀 STARTUPSAARTHI FINAL VERIFICATION")
    print("====================================")
    
    errors = []
    warnings = []
    
    # 1. Environment Check
    print("\n[1/4] Checking Environment...")
    if not os.path.exists(".env"):
        errors.append("❌ .env file missing")
    else:
        print("✅ .env found")
        
    if settings.gemini_api_key == "your_gemini_api_key_here":
         errors.append("❌ GEMINI_API_KEY is still default/placeholder")
    elif not settings.gemini_api_key:
         errors.append("❌ GEMINI_API_KEY is missing")
    else:
        print("✅ GEMINI_API_KEY configured")

    # 2. Index Check
    print("\n[2/4] Checking Search Indices...")
    try:
        retriever = get_retriever()
        if not retriever.loaded:
             errors.append("❌ Retriever indices failed to load")
        else:
            faiss_count = retriever.faiss_index.ntotal if retriever.faiss_index else 0
            bm25_count = len(retriever.bm25_index.doc_freqs) if retriever.bm25_index else 0
            
            print(f"   - FAISS Vectors: {faiss_count}")
            print(f"   - BM25 Documents: {bm25_count}")
            
            if faiss_count == 0:
                warnings.append("⚠️  Index is empty (No documents ingested yet?)")
            else:
                print("✅ Indices loaded and populated")
    except Exception as e:
        errors.append(f"❌ Retriever error: {e}")

    # 3. Functional Tests (RAG)
    print("\n[3/4] Testing RAG Pipeline (Queries)...")
    
    test_cases = [
        {
            "query": "What are the tax exemptions for startups?",
            "type": "valid",
            "expect_keywords": ["tax", "exemption", "80-IAC", "Section"]
        },
        {
            "query": "Explain SIDBI Fund of Funds.",
            "type": "valid",
            "expect_keywords": ["SIDBI", "Fund", "Crore", "Scheme"]
        },
        {
            "query": "Who is the Prime Minister of India?",
            "type": "invalid",
            "expect_refusal": True
        }
    ]

    for case in test_cases:
        query = case["query"]
        print(f"\n   Testing: '{query}'")
        try:
            result = await execute_query_graph(query=query)
            answer = result["answer"]
            sources = result["sources"]
            
            if case.get("expect_refusal"):
                # Check for refusal language
                refusals = ["I don't have enough", "sufficient information", "context", "cannot answer", "refuse"]
                if any(r.lower() in answer.lower() for r in refusals):
                     print("   ✅ Correctly Refused/Restricted")
                else:
                     errors.append(f"❌ FAILED: Should have refused '{query}' but answered: {answer[:50]}...")
            else:
                # Check for valid answer
                if not answer or len(answer) < 10:
                    errors.append(f"❌ FAILED: Empty or short answer for '{query}'")
                elif not sources:
                    warnings.append(f"⚠️  No sources used for '{query}' (Might need more data)")
                else:
                    # Check keywords
                    found_kw = [k for k in case["expect_keywords"] if k.lower() in answer.lower()]
                    if found_kw:
                        print(f"   ✅ Answered (Found keywords: {found_kw})")
                        print(f"   - Citations: {len(sources)}")
                        # print(f"   - Snippet: {answer[:100]}...")
                    else:
                        warnings.append(f"⚠️  Answer valid but missed keywords {case['expect_keywords']} for '{query}'")
                        
        except Exception as e:
            errors.append(f"❌ Exception during query '{query}': {e}")

    # 4. Summary
    print("\n[4/4] Final Report")
    print("==================")
    
    if not errors and not warnings:
        print("\n🎉 SUCCESS: Project is perfectly configured and running!")
    else:
        if warnings:
            print("\n⚠️  Warnings:")
            for w in warnings: print(w)
        if errors:
            print("\n❌ Critical Errors:")
            for e in errors: print(e)
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_final_verification())
