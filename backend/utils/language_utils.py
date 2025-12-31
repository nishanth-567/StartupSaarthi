"""
Language detection and multilingual utilities.
"""

from typing import Optional
import logging
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)


# Language code mapping
LANGUAGE_MAP = {
    "en": "en",
    "hi": "hi",
    "ta": "ta",
    "te": "te",
    # Add more mappings as needed
}


# Citation format mapping
CITATION_FORMATS = {
    "en": "Source",
    "hi": "स्रोत",
    "ta": "மூலம்",
    "te": "మూలం"
}


def detect_language(text: str) -> str:
    """
    Detect language of text.
    
    Args:
        text: Input text
    
    Returns:
        Language code (en, hi, ta, te) or 'en' as fallback
    """
    try:
        detected = detect(text)
        
        # Map to supported languages
        if detected in LANGUAGE_MAP:
            logger.info(f"Detected language: {detected}")
            return LANGUAGE_MAP[detected]
        else:
            logger.warning(f"Unsupported language detected: {detected}, defaulting to English")
            return "en"
            
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}, defaulting to English")
        return "en"


def get_citation_format(language: str) -> str:
    """
    Get citation word for language.
    
    Args:
        language: Language code
    
    Returns:
        Citation word (e.g., "Source", "स्रोत")
    """
    return CITATION_FORMATS.get(language, "Source")


def format_citation(source_id: int, language: str) -> str:
    """
    Format citation for language.
    
    Args:
        source_id: Source number
        language: Language code
    
    Returns:
        Formatted citation (e.g., "[Source 1]", "[स्रोत 1]")
    """
    citation_word = get_citation_format(language)
    return f"[{citation_word} {source_id}]"


def is_indic_language(language: str) -> bool:
    """
    Check if language is an Indic language.
    
    Args:
        language: Language code
    
    Returns:
        True if Indic language (hi, ta, te, etc.)
    """
    indic_languages = ["hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa", "or"]
    return language in indic_languages
