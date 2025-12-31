
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from backend.ingestion.ingestion_pipeline import ingest_document
from backend.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def ingest_scraped_data():
    base_dir = Path("scraped_data")
    
    if not base_dir.exists():
        print(f"❌ Directory not found: {base_dir}")
        return

    print(f"📂 Scanning {base_dir}...")
    
    files_to_process = []
    
    # Recursively find files
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_path = Path(root) / file
            # Simple extension check
            if file.endswith(('.txt', '.csv', '.pdf', '.docx', '.xlsx')):
                files_to_process.append(file_path)

    print(f"found {len(files_to_process)} files to ingest.")

    for i, file_path in enumerate(files_to_process, 1):
        print(f"[{i}/{len(files_to_process)}] Processing {file_path.name}...")
        
        # Determine type
        ext = file_path.suffix.lower().lstrip('.')
        if ext == 'xlsx': ext = 'excel'
        
        try:
            # Determine category from parent folder
            category = file_path.parent.name
            
            result = await ingest_document(
                file_path=str(file_path),
                document_type=ext,
                metadata={
                    "source": "scraped_data", 
                    "filename": file_path.name,
                    "category": category
                }
            )
            
            if result.get("success"):
                print(f"  ✅ Success: {result.get('chunks_created')} chunks")
            else:
                print(f"  ❌ Failed: {result.get('message')}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(ingest_scraped_data())
