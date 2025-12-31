"""
Configuration management for StartupSaarthi.
Loads environment variables and provides typed configuration access.
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Gemini LLM Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", env="GEMINI_MODEL")
    
    # Embedding Model
    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        env="EMBEDDING_MODEL"
    )
    
    # Storage Paths
    storage_path: Path = Field(default=Path("./storage"), env="STORAGE_PATH")
    faiss_index_path: Path = Field(default=Path("./storage/faiss_index"), env="FAISS_INDEX_PATH")
    bm25_index_path: Path = Field(default=Path("./storage/bm25_index.pkl"), env="BM25_INDEX_PATH")
    documents_path: Path = Field(default=Path("./storage/documents"), env="DOCUMENTS_PATH")
    
    # Retrieval Configuration
    top_k_retrieval: int = Field(default=20, env="TOP_K_RETRIEVAL")
    top_k_rerank: int = Field(default=5, env="TOP_K_RERANK")
    rrf_k: int = Field(default=60, env="RRF_K")
    
    # LLM Configuration
    llm_temperature_deterministic: float = Field(default=0.0, env="LLM_TEMPERATURE_DETERMINISTIC")
    llm_temperature_explanatory: float = Field(default=0.2, env="LLM_TEMPERATURE_EXPLANATORY")
    llm_max_tokens: int = Field(default=1000, env="LLM_MAX_TOKENS")
    llm_timeout_seconds: int = Field(default=30, env="LLM_TIMEOUT_SECONDS")
    
    # Translation
    enable_translation: bool = Field(default=False, env="ENABLE_TRANSLATION")
    translation_api_key: str = Field(default="", env="TRANSLATION_API_KEY")
    
    # API Configuration
    api_host: str = Field(default="127.0.0.1", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    cors_origins: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS"
    )
    
    # Admin Authentication
    admin_api_key: str = Field(..., env="ADMIN_API_KEY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure storage directories exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.documents_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
