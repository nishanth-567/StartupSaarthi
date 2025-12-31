"""
Admin-only API routes for ingestion and system management.
"""

from fastapi import APIRouter, HTTPException, status, Header, Depends
from backend.api.models import (
    IngestRequest, IngestResponse,
    ReindexRequest, ReindexResponse,
    StatsResponse
)
from backend.ingestion.ingestion_pipeline import ingest_document, reindex_all
from backend.config import settings
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_admin_key(x_admin_key: str = Header(...)):
    """Verify admin API key from header."""
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key"
        )
    return x_admin_key


@router.post("/ingest", response_model=IngestResponse, dependencies=[Depends(verify_admin_key)])
async def ingest_endpoint(request: IngestRequest):
    """
    Ingest a document into the system.
    
    Supports:
    - PDF, DOCX, TXT (unstructured)
    - CSV, Excel (structured)
    - Web URLs (scraped content)
    
    Requires admin authentication via X-Admin-Key header.
    """
    try:
        logger.info(f"Ingesting document: {request.file_path}")
        
        # Verify file exists (for local files)
        if request.document_type != "web" and not os.path.exists(request.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found: {request.file_path}"
            )
        
        # Execute ingestion pipeline
        result = await ingest_document(
            file_path=request.file_path,
            document_type=request.document_type,
            metadata=request.metadata or {}
        )
        
        logger.info(f"Ingestion successful: {result['chunks_created']} chunks created")
        
        return IngestResponse(**result)
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during ingestion: {str(e)}"
        )


@router.post("/reindex", response_model=ReindexResponse, dependencies=[Depends(verify_admin_key)])
async def reindex_endpoint(request: ReindexRequest):
    """
    Rebuild FAISS and/or BM25 indices from stored documents.
    
    Use this after bulk ingestion or to recover from index corruption.
    Requires admin authentication via X-Admin-Key header.
    """
    try:
        logger.info(f"Reindexing: FAISS={request.rebuild_faiss}, BM25={request.rebuild_bm25}")
        
        result = await reindex_all(
            rebuild_faiss=request.rebuild_faiss,
            rebuild_bm25=request.rebuild_bm25
        )
        
        logger.info("Reindexing completed successfully")
        
        return ReindexResponse(**result)
        
    except Exception as e:
        logger.error(f"Error during reindexing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during reindexing: {str(e)}"
        )


@router.get("/stats", response_model=StatsResponse, dependencies=[Depends(verify_admin_key)])
async def stats_endpoint():
    """
    Get system statistics.
    
    Returns information about indexed documents, index sizes, and configuration.
    Requires admin authentication via X-Admin-Key header.
    """
    try:
        # Calculate index sizes
        faiss_size = 0
        bm25_size = 0
        
        if settings.faiss_index_path.exists():
            faiss_size = sum(f.stat().st_size for f in settings.faiss_index_path.rglob('*') if f.is_file())
            faiss_size = faiss_size / (1024 * 1024)  # Convert to MB
        
        if settings.bm25_index_path.exists():
            bm25_size = settings.bm25_index_path.stat().st_size / (1024 * 1024)
        
        # Count documents
        total_documents = 0
        total_chunks = 0
        if settings.documents_path.exists():
            total_documents = len(list(settings.documents_path.glob("*.json")))
        
        return StatsResponse(
            total_documents=total_documents,
            total_chunks=total_chunks,
            faiss_index_size_mb=round(faiss_size, 2),
            bm25_index_size_mb=round(bm25_size, 2),
            supported_languages=["en", "hi", "ta", "te"],
            embedding_model=settings.embedding_model
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )
