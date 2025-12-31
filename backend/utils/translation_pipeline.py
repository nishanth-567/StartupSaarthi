"""
Optional translation pipeline for improved cross-lingual retrieval.
"""

from typing import Optional
import logging

from backend.config import settings
from backend.utils.language_utils import is_indic_language

logger = logging.getLogger(__name__)


class TranslationPipeline:
    """
    Optional translation pipeline for queries.
    Translates Indic language queries to English for better retrieval.
    """
    
    def __init__(self):
        """Initialize translation pipeline."""
        self.translator = None
        self.enabled = settings.enable_translation
        self.cache = {}  # Simple in-memory cache
    
    def initialize(self):
        """Initialize translator if enabled."""
        if self.enabled:
            try:
                from googletrans import Translator
                self.translator = Translator()
                logger.info("Translation pipeline initialized")
            except Exception as e:
                logger.warning(f"Error initializing translator (features disabled): {e}")
                self.enabled = False
    
    async def translate_query(self, query: str, source_lang: str) -> Optional[str]:
        """
        Translate query to English if needed.
        
        Args:
            query: Original query
            source_lang: Source language code
        
        Returns:
            Translated query or None if translation not needed/failed
        """
        if not self.enabled:
            return None
        
        # Only translate Indic languages to English
        if not is_indic_language(source_lang):
            return None
        
        # Check cache
        cache_key = f"{source_lang}:{query}"
        if cache_key in self.cache:
            logger.info("Using cached translation")
            return self.cache[cache_key]
        
        try:
            if self.translator is None:
                self.initialize()
            
            logger.info(f"Translating query from {source_lang} to English")
            
            result = self.translator.translate(query, src=source_lang, dest='en')
            translated = result.text
            
            # Cache translation
            self.cache[cache_key] = translated
            
            logger.info(f"Translation: {query[:50]}... → {translated[:50]}...")
            
            return translated
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return None


# Global instance
_translation_pipeline: Optional[TranslationPipeline] = None


def get_translation_pipeline() -> TranslationPipeline:
    """Get or create global translation pipeline instance."""
    global _translation_pipeline
    if _translation_pipeline is None:
        _translation_pipeline = TranslationPipeline()
        if _translation_pipeline.enabled:
            _translation_pipeline.initialize()
    return _translation_pipeline
