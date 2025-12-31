"""
Main ingestion pipeline orchestrating document processing and indexing.
"""

from typing import Dict, Any
import logging
import json
from pathlib import Path
import uuid

from backend.ingestion.document_processor import DocumentProcessor
from backend.ingestion.structured_data_parser import StructuredDataParser
from backend.ingestion.indexer import IndexBuilder
from backend.config import settings

logger = logging.getLogger(__name__)


async def ingest_document(
    file_path: str,
    document_type: str,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Ingest a document into the system.
    
    Args:
        file_path: Path to document
        document_type: Type (pdf, docx, txt, csv, excel)
        metadata: Additional metadata
    
    Returns:
        Ingestion result with statistics
    """
    try:
        logger.info(f"Starting ingestion: {file_path} ({document_type})")
        
        # Process document based on type
        chunks = []
        
        if document_type in ["pdf", "docx", "txt"]:
            processor = DocumentProcessor()
            chunks = processor.process_document(file_path, document_type)
        
        elif document_type in ["csv", "excel"]:
            parser = StructuredDataParser()
            chunks = parser.process_structured_data(file_path, document_type)
        
        else:
            return {
                "success": False,
                "message": f"Unsupported document type: {document_type}",
                "chunks_created": 0
            }
        
        if not chunks:
            return {
                "success": False,
                "message": "No chunks created from document",
                "chunks_created": 0
            }
        
        # Add additional metadata to all chunks
        document_id = str(uuid.uuid4())
        for chunk in chunks:
            chunk["metadata"]["document_id"] = document_id
            if metadata:
                chunk["metadata"].update(metadata)
        
        # Save document metadata
        doc_metadata = {
            "document_id": document_id,
            "file_path": file_path,
            "document_type": document_type,
            "chunks_count": len(chunks),
            "metadata": metadata or {}
        }
        
        settings.documents_path.mkdir(parents=True, exist_ok=True)
        with open(settings.documents_path / f"{document_id}.json", "w") as f:
            json.dump(doc_metadata, f, indent=2)
        
        # Add to indices
        indexer = IndexBuilder()
        index_stats = await indexer.add_chunks_to_indices(chunks)
        
        logger.info(f"Ingestion complete: {len(chunks)} chunks, {index_stats}")
        
        return {
            "success": True,
            "message": "Document ingested successfully",
            "chunks_created": len(chunks),
            "document_id": document_id
        }
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error during ingestion: {str(e)}",
            "chunks_created": 0
        }


async def reindex_all(rebuild_faiss: bool = True, rebuild_bm25: bool = True) -> Dict[str, Any]:
    """
    Rebuild indices from all stored documents.
    
    Args:
        rebuild_faiss: Rebuild FAISS index
        rebuild_bm25: Rebuild BM25 index
    
    Returns:
        Reindex result with statistics
    """
    try:
        logger.info("Starting reindexing...")
        
        # Load all document metadata
        all_chunks = []
        
        if settings.documents_path.exists():
            for doc_file in settings.documents_path.glob("*.json"):
                with open(doc_file, "r") as f:
                    doc_metadata = json.load(f)
                
                # Re-process document
                file_path = doc_metadata["file_path"]
                document_type = doc_metadata["document_type"]
                
                if document_type in ["pdf", "docx", "txt"]:
                    processor = DocumentProcessor()
                    chunks = processor.process_document(file_path, document_type)
                elif document_type in ["csv", "excel"]:
                    parser = StructuredDataParser()
                    chunks = parser.process_structured_data(file_path, document_type)
                else:
                    continue
                
                # Add metadata
                for chunk in chunks:
                    chunk["metadata"]["document_id"] = doc_metadata["document_id"]
                    chunk["metadata"].update(doc_metadata.get("metadata", {}))
                
                all_chunks.extend(chunks)
        
        if not all_chunks:
            return {
                "success": False,
                "message": "No documents found to reindex",
                "faiss_documents": 0,
                "bm25_documents": 0
            }
        
        # Rebuild indices
        indexer = IndexBuilder()
        stats = await indexer.build_indices(all_chunks)
        
        logger.info(f"Reindexing complete: {stats}")
        
        return {
            "success": True,
            "message": "Reindexing completed successfully",
            "faiss_documents": stats["faiss_vectors"],
            "bm25_documents": stats["bm25_documents"]
        }
        
    except Exception as e:
        logger.error(f"Error during reindexing: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error during reindexing: {str(e)}",
            "faiss_documents": 0,
            "bm25_documents": 0
        }
