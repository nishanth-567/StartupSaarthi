
import asyncio
import os
import sys

# Add current dir to path
sys.path.append(os.getcwd())

async def test_system():
    print("=== STARTUPSAARTHI DIAGNOSTIC ===")
    
    # 1. Check Env
    print("\n1. Checking Environment...")
    if not os.path.exists(".env"):
        print("❌ .env file missing!")
        return
    
    from backend.config import settings
    print(f"✅ Config loaded. Model: {settings.gemini_model}")
    print(f"✅ API Key present: {'Yes' if settings.gemini_api_key else 'No'}")
    
    # 2. Check Retrieval
    print("\n2. Checking Retriever...")
    try:
        from backend.retriever.hybrid_retriever import get_retriever
        retriever = get_retriever()
        print(f"✅ Retriever intialized.")
        
        # Test search
        res = await retriever.retrieve_hybrid("startup", top_k=1)
        print(f"✅ Retrieval Test: Found {len(res['dense_results'])} dense, {len(res['sparse_results'])} sparse")
    except Exception as e:
        print(f"❌ Retriever Failed: {e}")
        
    # 3. Check LLM
    print("\n3. Checking LLM API...")
    try:
        from backend.llm.llm_client import get_llm_client
        client = get_llm_client()
        
        # Simple generation
        answer = await client.generate_answer(
            query="Hello, are you working?",
            context_chunks=[],
            language="en"
        )
        print(f"✅ LLM Response: {answer[:100]}...")
    except Exception as e:
        print(f"❌ LLM Failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test_system())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
