
import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from backend.ingestion.ingestion_pipeline import ingest_document
from backend.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def ingest_samples():
    sample_dir = os.path.join("sample_data")
    
    if not os.path.exists(sample_dir):
        print(f"❌ Sample directory not found: {sample_dir}")
        return

    files = [f for f in os.listdir(sample_dir) if f.endswith(('.txt', '.csv'))]
    print(f"Found {len(files)} files to ingest.")

    for file in files:
        file_path = os.path.join(sample_dir, file)
        doc_type = "csv" if file.endswith(".csv") else "txt"
        print(f"Processing {file}...")
        
        try:
            # Call function directly
            result = await ingest_document(
                file_path=file_path,
                document_type=doc_type,
                metadata={"source": "sample_data", "filename": file}
            )
            if result.get("success"):
                print(f"✅ Ingested {file}: {result.get('chunks_created')} chunks")
            else:
                print(f"❌ Failed to ingest {file}: {result.get('message')}")
        except Exception as e:
            print(f"❌ Error ingesting {file}: {e}")

if __name__ == "__main__":
    asyncio.run(ingest_samples())
