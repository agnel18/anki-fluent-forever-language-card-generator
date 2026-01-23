# API Client Service for Sentence Generation
# Handles all Gemini API communication with error recovery and rate limiting

import logging
import time
from typing import Optional, Dict, Any
import google.generativeai as genai

from streamlit_app.error_recovery import retry_with_exponential_backoff

logger = logging.getLogger(__name__)


class APIClient:
    """
    Service for handling all Gemini API communication.
    Provides unified interface for different types of API calls with error recovery.
    """

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    @retry_with_exponential_backoff(max_retries=3)
    def call_completion(self, prompt: str, temperature: float = 0.3,
                       max_tokens: int = 2000) -> str:
        """
        Make a chat completion API call with error recovery.

        Args:
            prompt: The prompt to send to the API
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            The API response text

        Raises:
            Exception: If all retry attempts fail
        """
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )

        response_text = response.text.strip()
        logger.info(f"API call successful: {len(response_text)} characters")
        return response_text

    def call_with_rate_limit(self, prompt: str, temperature: float = 0.3,
                           max_tokens: int = 2000, delay_seconds: int = 5) -> str:
        """
        Make an API call with built-in rate limiting delay.

        Args:
            prompt: The prompt to send to the API
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            delay_seconds: Seconds to wait after successful call

        Returns:
            The API response text
        """
        response_text = self.call_completion(prompt, temperature, max_tokens)

        if delay_seconds > 0:
            logger.debug(f"Rate limiting: waiting {delay_seconds} seconds")
            time.sleep(delay_seconds)

        return response_text