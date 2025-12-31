
import os

env_template = """# StartupSaarthi Environment Configuration

# Gemini LLM Configuration
GEMINI_API_KEY={GEMINI_KEY}
GEMINI_MODEL=gemini-pro

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# Storage Paths
STORAGE_PATH=./storage
FAISS_INDEX_PATH=./storage/faiss_index
BM25_INDEX_PATH=./storage/bm25_index.pkl
DOCUMENTS_PATH=./storage/documents

# Retrieval Configuration
TOP_K_RETRIEVAL=20
TOP_K_RERANK=5
RRF_K=60

# LLM Configuration
LLM_TEMPERATURE_DETERMINISTIC=0.0
LLM_TEMPERATURE_EXPLANATORY=0.2
LLM_MAX_TOKENS=1000
LLM_TIMEOUT_SECONDS=30

# Translation (optional)
ENABLE_TRANSLATION=false
TRANSLATION_API_KEY=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
# Fixed CORS syntax as JSON array
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Admin Authentication
ADMIN_API_KEY={ADMIN_KEY}

# Logging
LOG_LEVEL=INFO
"""

def fix_env():
    # Defaults
    gemini_key = "your_gemini_api_key_here"
    admin_key = "mysecretkey123"

    # 1. Try to read existing keys from .env
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY="):
                        parts = line.split("=", 1)
                        if len(parts) > 1 and parts[1].strip():
                            val = parts[1].strip().strip('"').strip("'")
                            if "your_gemini" not in val: # Keep existing real key
                                gemini_key = val
                    elif line.startswith("ADMIN_API_KEY="):
                        parts = line.split("=", 1)
                        if len(parts) > 1 and parts[1].strip():
                            val = parts[1].strip().strip('"').strip("'")
                            if "your_secure" not in val:
                                admin_key = val
        except Exception as e:
            print(f"Warning reading .env: {e}")

    # 2. Write clean .env
    new_content = env_template.format(
        GEMINI_KEY=gemini_key,
        ADMIN_KEY=admin_key
    )
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ Successfully repaired .env file!")
    print(f"   GEMINI_MODEL set to: gemini-pro")
    print(f"   CORS_ORIGINS fixed.")
    print(f"   GEMINI_API_KEY preserved: {gemini_key[:4]}...{gemini_key[-4:] if len(gemini_key)>8 else ''}")

if __name__ == "__main__":
    fix_env()
