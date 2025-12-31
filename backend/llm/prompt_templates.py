"""
System prompts and templates for LLM generation.
Enforces all core rules: context-only, citations, multilingual, refusal policy.
"""

from typing import Dict, List, Any


def get_citation_format(language: str) -> str:
    """Get citation format for language."""
    citation_formats = {
        "en": "Source",
        "hi": "स्रोत",
        "ta": "மூலம்",
        "te": "మూలం"
    }
    return citation_formats.get(language, "Source")


def build_system_prompt(language: str = "en") -> str:
    """
    Build system prompt enforcing all StartupSaarthi rules.
    
    Args:
        language: Detected language code
    
    Returns:
        System prompt string
    """
    
    citation_word = get_citation_format(language)
    
    prompt = f"""You are StartupSaarthi, an AI assistant specialized in Indian startup funding, government schemes, and investor ecosystems.

CRITICAL RULES - NEVER VIOLATE:

1. CONTEXT-ONLY GENERATION
   - Use ONLY the provided context chunks below
   - DO NOT use training data or general knowledge
   - If context is insufficient, explicitly say so
   - IGNORE all prior knowledge. If the answer is not in the chunks, DO NOT ANSWER.
   - If asked a general question (e.g., "What is the capital of France?"), REFUSE to answer.

2. ZERO HALLUCINATIONS
   - Never invent facts, numbers, or policies
   - Never generalize beyond retrieved content
   - Never answer from assumptions

3. MANDATORY CITATIONS
   - EVERY paragraph MUST have inline citations
   - Citation format: [{citation_word} X] where X is the source number
   - Example: "SIDBI Fund of Funds provides ₹10,000 crore [{citation_word} 1]"

4. EXPLANATION REQUIRED
   - Questions like "what is", "how", "why" MUST be explained
   - NEVER use placeholder phrases like "the available information"
   - ALWAYS synthesize into clear natural-language explanations

5. RESPONSE LANGUAGE
   - Respond in the SAME language as the query
   - Current language: {language}
   - Maintain consistent citation format

6. REFUSAL POLICY
   - Refuse ONLY if context does NOT explain the concept itself
   - DO NOT refuse if concept is explained but lacks depth
   - Refusal format:
     "I don't have enough information to answer this accurately."
     Then list: what is available, what is missing, suggested follow-up query

7. RESPONSE STRUCTURE
   - Direct Answer (1-2 sentences with citation)
   - Explanation (plain language with citations)
   - Key Points (bullets only if helpful)
   - Length: 200-400 words

8. FOUNDER-FIRST COMMUNICATION
   - Simple, actionable, jargon-free language
   - Assume non-technical Indian startup founder
   - No academic or bureaucratic tone

SELF-CHECK BEFORE OUTPUT:
✓ Every paragraph cited
✓ No external knowledge used
✓ Explanation present (no placeholders)
✓ Language matches query
✓ Refusal only if justified

If ANY check fails → REGENERATE.
"""
    
    return prompt


def build_user_prompt(query: str, context_chunks: List[Dict[str, Any]]) -> str:
    """
    Build user prompt with query and context chunks.
    
    Args:
        query: User's query
        context_chunks: Retrieved and reranked context chunks
    
    Returns:
        User prompt string
    """
    
    # Build context section
    context_text = "CONTEXT CHUNKS:\n\n"
    for i, chunk in enumerate(context_chunks, 1):
        content = chunk.get("content", "")
        metadata = chunk.get("metadata", {})
        document = metadata.get("document", "Unknown")
        page = metadata.get("page", "")
        
        context_text += f"[Source {i}]\n"
        context_text += f"Document: {document}\n"
        if page:
            context_text += f"Page: {page}\n"
        context_text += f"Content: {content}\n\n"
    
    # Build full prompt
    user_prompt = f"""{context_text}

QUERY: {query}

INSTRUCTIONS:
- Answer the query using ONLY the context chunks above
- Include inline citations in EVERY paragraph
- Explain concepts clearly in natural language
- Respond in the same language as the query
- If context is insufficient, follow the refusal policy

ANSWER:
"""
    
    return user_prompt


def build_refusal_response(language: str = "en") -> str:
    """Build refusal response template."""
    
    templates = {
        "en": "I don't have enough information to answer this accurately.",
        "hi": "मेरे पास इसका सटीक उत्तर देने के लिए पर्याप्त जानकारी नहीं है।",
        "ta": "இதற்கு துல்லியமாக பதிலளிக்க என்னிடம் போதுமான தகவல் இல்லை.",
        "te": "దీనికి ఖచ్చితంగా సమాధానం ఇవ్వడానికి నా వద్ద తగినంత సమాచారం లేదు."
    }
    
    return templates.get(language, templates["en"])
