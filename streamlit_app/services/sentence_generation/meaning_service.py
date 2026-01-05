# Meaning Service for Sentence Generation
# Handles word meaning generation and caching

import logging
import time
from typing import Optional
from groq import Groq

# Import cache manager and error recovery
from cache_manager import cached_api_call
from error_recovery import resilient_groq_call, with_fallback

logger = logging.getLogger(__name__)


class MeaningService:
    """
    Service for generating word meanings using Groq API.
    Provides English meanings with brief explanations for language learning.
    """

    def __init__(self):
        pass

    @cached_api_call("groq_meaning", ttl_seconds=86400)  # Cache for 24 hours
    @resilient_groq_call(max_retries=3)
    @with_fallback(fallback_value=lambda word, **kwargs: word)  # Fallback to word itself
    def generate_word_meaning(
        self,
        word: str,
        language: str,
        groq_api_key: str = None,
    ) -> str:
        """
        Generate English meaning and brief explanation for a word.

        Args:
            word: Target language word
            language: Language name (e.g., "Spanish", "Hindi")
            groq_api_key: Groq API key

        Returns:
            String with meaning and brief explanation (e.g., "he (male pronoun, used as subject)")
        """
        if not groq_api_key:
            raise ValueError("Groq API key required")

        client = Groq(api_key=groq_api_key)

        prompt = f"""Provide a brief English meaning for the {language} word \"{word}\".

Format: Return ONLY a single line with the meaning and a brief explanation in parentheses.
Example: \"house (a building where people live)\" or \"he (male pronoun, used as subject)\"

IMPORTANT: Return ONLY the meaning line, nothing else. No markdown, no explanation, no JSON."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for consistency
            max_tokens=100,
        )

        # --- API USAGE TRACKING ---
        try:
            import streamlit as st
            if "groq_api_calls" not in st.session_state:
                st.session_state.groq_api_calls = 0
            if "groq_tokens_used" not in st.session_state:
                st.session_state.groq_tokens_used = 0
            st.session_state.groq_api_calls += 1
            # Estimate tokens used (prompt+completion)
            st.session_state.groq_tokens_used += 100  # rough estimate, adjust if needed
        except Exception:
            pass
        # -------------------------

        meaning = response.choices[0].message.content.strip()

        # Clean up any quotes
        meaning = meaning.strip('"\'')
        logger.info(f"Generated meaning for '{word}': {meaning}")

        # Rate limiting: wait 5 seconds between API calls to respect per-minute limits
        time.sleep(5)

        return meaning if meaning else word