"""
Gemini and Groq LLM client for answer generation.
Supports auto-switching based on API key format.
"""

from typing import Dict, List, Any, Optional
import logging
import os
import google.generativeai as genai
from groq import Groq
from backend.config import settings
from backend.llm.prompt_templates import build_system_prompt, build_user_prompt

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified Client for Google Gemini and Groq API.
    """
    
    def __init__(self):
        """Initialize LLM client."""
        self.model = None
        self.client = None
        self.provider = "gemini"  # default
        self.configured = False
    
    def configure(self):
        """Configure API based on Key."""
        api_key = settings.gemini_api_key.strip()
        
        try:
            if api_key.startswith("gsk_"):
                # GROQ PROVIDER
                self.provider = "groq"
                self.client = Groq(api_key=api_key)
                
                # Use Llama 3 70B if user hasn't specified a specific model
                # or if the config still says 'gemini-...'
                if "gemini" in settings.gemini_model.lower():
                    # Default to Llama 3.3 70B (Versatile) as verified working
                    self.model_name = "llama-3.3-70b-versatile"
                else:
                    self.model_name = settings.gemini_model
                    
                logger.info(f"Groq provider configured with model: {self.model_name}")
                
            else:
                # GEMINI PROVIDER
                self.provider = "gemini"
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
                logger.info(f"Gemini provider configured with model: {settings.gemini_model}")
            
            self.configured = True
            
        except Exception as e:
            logger.error(f"Error configuring LLM provider: {e}", exc_info=True)
            raise
    
    async def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        language: str = "en",
        deterministic: bool = False
    ) -> str:
        """
        Generate answer using configured provider.
        """
        if not self.configured:
            self.configure()
        
        try:
            # Build prompts
            system_prompt = build_system_prompt(language)
            user_prompt = build_user_prompt(query, context_chunks)
            
            # Combine prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Set temperature
            temperature = (
                settings.llm_temperature_deterministic if deterministic
                else settings.llm_temperature_explanatory
            )
            
            logger.info(f"Generating answer via {self.provider} (temp={temperature}, lang={language})")
            
            if self.provider == "groq":
                # GROQ GENERATION
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=self.model_name,
                    temperature=temperature,
                    max_tokens=settings.llm_max_tokens,
                )
                answer = chat_completion.choices[0].message.content
                
            else:
                # GEMINI GENERATION
                # Auto-healing logic for Gemini models
                primary_model = settings.gemini_model
                models_to_try = [primary_model]
                
                # Add fallbacks if primary is a known problematic one or just standard practice
                defaults = ["gemini-2.0-flash-exp", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
                for m in defaults:
                    if m != primary_model:
                        models_to_try.append(m)
                
                last_error = None
                
                for model_name in models_to_try:
                    try:
                        if model_name != primary_model:
                            logger.info(f"Falling back to model: {model_name}")
                            model_instance = genai.GenerativeModel(model_name)
                        else:
                            model_instance = self.model

                        response = model_instance.generate_content(
                            full_prompt,
                            generation_config=genai.GenerationConfig(
                                temperature=temperature,
                                max_output_tokens=settings.llm_max_tokens,
                            )
                        )
                        answer = response.text
                        break # Success
                    except Exception as e:
                        logger.warning(f"Model {model_name} failed: {e}")
                        last_error = e
                        continue
                else:
                    # If loop finishes without break
                    raise last_error

            logger.info(f"Answer generated: {len(answer)} characters")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}", exc_info=True)
            raise


# Global client instance
_client_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = LLMClient()
        _client_instance.configure()
    return _client_instance
