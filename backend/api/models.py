"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"


class QueryRequest(BaseModel):
    """User query request model."""
    query: str = Field(..., description="User's question in any supported language", min_length=3)
    deterministic: bool = Field(default=False, description="Use deterministic mode (temperature=0)")
    language: Optional[Language] = Field(default=None, description="Override detected language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is SIDBI Fund of Funds?",
                "deterministic": False
            }
        }


class Source(BaseModel):
    """Source citation model."""
    source_id: int = Field(..., description="Source number for citation")
    document: str = Field(..., description="Document name")
    page: Optional[int] = Field(default=None, description="Page number if applicable")
    section: Optional[str] = Field(default=None, description="Section name if applicable")
    content_snippet: str = Field(..., description="Relevant content snippet")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class QueryResponse(BaseModel):
    """Query response model with answer and citations."""
    answer: str = Field(..., description="Generated answer with inline citations")
    sources: List[Source] = Field(..., description="List of source citations")
    detected_language: Language = Field(..., description="Detected query language")
    processing_time_seconds: float = Field(..., description="Total processing time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "SIDBI Fund of Funds is a scheme...[Source 1]",
                "sources": [
                    {
                        "source_id": 1,
                        "document": "SIDBI_Schemes_2024.pdf",
                        "page": 5,
                        "section": "Fund of Funds Scheme",
                        "content_snippet": "The Fund of Funds scheme...",
                        "metadata": {}
                    }
                ],
                "detected_language": "en",
                "processing_time_seconds": 2.34
            }
        }


class IngestRequest(BaseModel):
    """Document ingestion request model."""
    file_path: str = Field(..., description="Path to document file")
    document_type: str = Field(..., description="Type: pdf, docx, txt, csv, excel, web")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/path/to/document.pdf",
                "document_type": "pdf",
                "metadata": {"category": "government_scheme", "year": 2024}
            }
        }


class IngestResponse(BaseModel):
    """Ingestion response model."""
    success: bool = Field(..., description="Whether ingestion succeeded")
    message: str = Field(..., description="Status message")
    chunks_created: int = Field(default=0, description="Number of chunks created")
    document_id: Optional[str] = Field(default=None, description="Unique document ID")


class ReindexRequest(BaseModel):
    """Reindex request model."""
    rebuild_faiss: bool = Field(default=True, description="Rebuild FAISS index")
    rebuild_bm25: bool = Field(default=True, description="Rebuild BM25 index")


class ReindexResponse(BaseModel):
    """Reindex response model."""
    success: bool = Field(..., description="Whether reindexing succeeded")
    message: str = Field(..., description="Status message")
    faiss_documents: int = Field(default=0, description="Documents in FAISS index")
    bm25_documents: int = Field(default=0, description="Documents in BM25 index")


class StatsResponse(BaseModel):
    """System statistics response model."""
    total_documents: int = Field(..., description="Total documents indexed")
    total_chunks: int = Field(..., description="Total chunks indexed")
    faiss_index_size_mb: float = Field(..., description="FAISS index size in MB")
    bm25_index_size_mb: float = Field(..., description="BM25 index size in MB")
    supported_languages: List[str] = Field(..., description="Supported languages")
    embedding_model: str = Field(..., description="Current embedding model")
