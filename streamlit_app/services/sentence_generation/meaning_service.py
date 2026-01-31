# Meaning Service for Sentence Generation
# Handles word meaning generation and caching

import logging
import time
import warnings
from typing import Optional

# Suppress FutureWarnings (including google.generativeai deprecation)
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai

# Import cache manager and error recovery
from streamlit_app.shared_utils import cached_api_call, retry_with_exponential_backoff, with_fallback, get_gemini_model

logger = logging.getLogger(__name__)


class MeaningService:
    """
    Service for generating word meanings using Gemini API.
    Provides English meanings with brief explanations for language learning.
    """

    def __init__(self):
        pass

    @cached_api_call("gemini_meaning", ttl_seconds=86400)  # Cache for 24 hours
    @retry_with_exponential_backoff(max_retries=3)
    @with_fallback(fallback_value=lambda word, **kwargs: word)  # Fallback to word itself
    def generate_word_meaning(
        self,
        word: str,
        language: str,
        gemini_api_key: str = None,
    ) -> str:
        """
        Generate English meaning and brief explanation for a word.

        Args:
            word: Target language word
            language: Language name (e.g., "Spanish", "Hindi")
            gemini_api_key: Gemini API key

        Returns:
            String with meaning and brief explanation (e.g., "he (male pronoun, used as subject)")
        """
        if not gemini_api_key:
            raise ValueError("Gemini API key required")

        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(get_gemini_model())

        prompt = f"""Provide a brief English meaning for the {language} word \"{word}\".

Format: Return ONLY a single line with the meaning and a brief explanation in parentheses.
Example: \"house (a building where people live)\" or \"he (male pronoun, used as subject)\"

IMPORTANT: Return ONLY the meaning line, nothing else. No markdown, no explanation, no JSON."""

        generation_config = genai.types.GenerationConfig(
            temperature=0.3,  # Lower temperature for consistency
            max_output_tokens=100,
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        # --- API USAGE TRACKING ---
        try:
            import streamlit as st
            if "gemini_api_calls" not in st.session_state:
                st.session_state.gemini_api_calls = 0
            if "gemini_tokens_used" not in st.session_state:
                st.session_state.gemini_tokens_used = 0
            st.session_state.gemini_api_calls += 1
            # Estimate tokens used (prompt+completion)
            st.session_state.gemini_tokens_used += 100  # rough estimate, adjust if needed
        except Exception:
            pass
        # -------------------------

        meaning = response.text.strip()

        # Clean up any quotes
        meaning = meaning.strip('"\'')
        logger.info(f"Generated meaning for '{word}': {meaning}")

        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)

        return meaning if meaning else word