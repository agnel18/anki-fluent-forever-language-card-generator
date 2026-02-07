# shared_utils.py - Common utilities to break circular import dependencies
"""
Shared utilities that can be imported by both services and main modules
without creating circular dependencies.
"""

import json
import hashlib
import os
import time
import logging
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, Callable, List, TypeVar
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
import random

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION UTILITIES
# ============================================================================

# Gemini model configuration - STRICTLY LIMITED TO APPROVED MODELS ONLY
GEMINI_MODELS = {
    'current': 'gemini-2.5-flash',        # Primary model for complex analysis
    'fallback': 'gemini-3-flash-preview', # Fallback model for simpler tasks
    'deprecated': ['gemini-pro', 'gemini-pro-vision', 'gemini-1.5-flash', 'gemini-2.0-flash-exp']
}

def get_gemini_model() -> str:
    """Get the current Gemini model name."""
    return GEMINI_MODELS['current']

def get_gemini_fallback_model() -> str:
    """Get the fallback Gemini model name."""
    return GEMINI_MODELS['fallback']

def get_available_gemini_models() -> List[str]:
    """Get all available Gemini models including deprecated ones."""
    return [get_gemini_model(), get_gemini_fallback_model()] + GEMINI_MODELS['deprecated']

# ============================================================================
# CACHE MANAGEMENT UTILITIES
# ============================================================================

@dataclass
class CacheEntry:
    """Represents a cached API response."""
    key: str
    data: Any
    timestamp: float
    expires_at: float
    metadata: Dict[str, Any]

class CacheManager:
    """
    Manages API response caching with configurable expiration and persistence.
    """

    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl
        self._cache = {}
        self._load_persistent_cache()

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        # Create a safe filename from the key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.json"

    def _load_persistent_cache(self):
        """Load persistent cache entries from disk."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entry = CacheEntry(**data)
                    if time.time() < entry.expires_at:
                        self._cache[entry.key] = entry
                    else:
                        # Remove expired persistent cache
                        cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to load cache file {cache_file}: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache if it exists and hasn't expired."""
        entry = self._cache.get(key)
        if entry and time.time() < entry.expires_at:
            return entry.data
        elif entry:
            # Remove expired entry
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None):
        """Set a value in cache with optional TTL."""
        expires_at = time.time() + (ttl or self.default_ttl)
        entry = CacheEntry(
            key=key,
            data=value,
            timestamp=time.time(),
            expires_at=expires_at,
            metadata=metadata or {}
        )
        self._cache[key] = entry

        # Persist to disk
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'key': entry.key,
                    'data': entry.data,
                    'timestamp': entry.timestamp,
                    'expires_at': entry.expires_at,
                    'metadata': entry.metadata
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to persist cache entry {key}: {e}")

    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
        # Remove all cache files
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to remove cache file {cache_file}: {e}")

# Global cache manager instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def cached_api_call(cache_key: str, ttl: Optional[int] = None):
    """
    Decorator to cache API call results.

    Args:
        cache_key: Unique key for the cache entry
        ttl: Time to live in seconds (optional)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()

            # Try to get from cache first
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result

            # Call the function
            result = func(*args, **kwargs)

            # Cache the result
            cache_manager.set(cache_key, result, ttl)

            logger.debug(f"Cache miss for {cache_key}, stored result")
            return result

        return wrapper
    return decorator

# ============================================================================
# ERROR RECOVERY UTILITIES
# ============================================================================

T = TypeVar('T')

class APIError(Exception):
    """Base exception for API-related errors."""
    pass

class NetworkError(APIError):
    """Network connectivity or timeout errors."""
    pass

class APIQuotaError(APIError):
    """API quota or rate limit exceeded."""
    pass

class APIAuthError(APIError):
    """API authentication errors."""
    pass

def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True
):
    """
    Decorator that implements exponential backoff retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Factor to multiply delay by on each retry
        jitter: Whether to add random jitter to delay
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}: {e}")
                        raise e

                    delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)  # 0.5 to 1.0 multiplier

                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)

            # This should never be reached, but just in case
            raise last_exception

        return wrapper
    return decorator

def with_fallback(*fallback_funcs: Callable) -> Callable:
    """
    Decorator that provides fallback functions to try if the main function fails.

    Args:
        *fallback_funcs: Fallback functions to try in order
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            # Try main function first
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Main function {func.__name__} failed: {e}")

            # Try fallback functions
            for i, fallback_func in enumerate(fallback_funcs):
                try:
                    logger.info(f"Trying fallback function {i + 1}: {fallback_func.__name__}")
                    return fallback_func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Fallback function {i + 1} {fallback_func.__name__} failed: {e}")

            # All functions failed
            logger.error(f"All functions failed for {func.__name__}")
            raise last_exception

        return wrapper
    return decorator

# ============================================================================
# LANGUAGE CONSTANTS
# ============================================================================

# Language code mappings
LANGUAGE_NAME_TO_CODE = {
    'arabic': 'ar',
    'Arabic': 'ar',
    'Modern Standard Arabic': 'ar',
    'chinese_simplified': 'zh',
    'chinese_traditional': 'zh-tw',
    'chinese (simplified)': 'zh',
    'chinese (traditional)': 'zh-tw',
    'Chinese (Simplified)': 'zh',
    'Chinese (Traditional)': 'zh-tw',
    'Chinese': 'zh',
    'Chinese Simplified': 'zh',
    'Chinese Traditional': 'zh-tw',
    'hindi': 'hi',
    'Hindi': 'hi',
    'spanish': 'es',
    'Spanish': 'es',  # Capitalized version
    'french': 'fr',
    'French': 'fr',  # Capitalized version
    'german': 'de',
    'German': 'de',  # Capitalized version
    'italian': 'it',
    'Italian': 'it',  # Capitalized version
    'portuguese': 'pt',
    'Portuguese': 'pt',
    'russian': 'ru',
    'Russian': 'ru',
    'japanese': 'ja',
    'Japanese': 'ja',
    'korean': 'ko',
    'Korean': 'ko',
    'turkish': 'tr',
    'Turkish': 'tr'
}

LANGUAGE_CODE_TO_NAME = {v: k for k, v in LANGUAGE_NAME_TO_CODE.items()}

# Content generation language name mapping for AI compatibility
CONTENT_LANGUAGE_MAP = {
    "Chinese (Traditional)": "Traditional Chinese",
    "Chinese (Simplified)": "Simplified Chinese",
    "Arabic": "Modern Standard Arabic",
}

# ============================================================================
# CONSTANTS
# ============================================================================

# API Limits
GEMINI_CALL_LIMIT = 1000
GEMINI_TOKEN_LIMIT = 3000000
GOOGLE_SEARCH_CALL_LIMIT = 100

# Default Settings
DEFAULT_BATCH_SIZE = 5
DEFAULT_SENTENCES_PER_WORD = 4
DEFAULT_AUDIO_SPEED = 0.8
DEFAULT_SELECTION_MODE = "range"  # range, manual, search
DEFAULT_DIFFICULTY = "intermediate"  # beginner, intermediate, advanced
DEFAULT_VOICE_DISPLAY = "en-US-Standard-D"
DEFAULT_VOICE = "en-US-Standard-D"
DEFAULT_ENABLE_TOPICS = False  # Whether to enable topic selection by default
DEFAULT_SELECTED_TOPICS = []  # Default selected topics

# Curated Topics List
CURATED_TOPICS = [
    "Daily Life", "Food & Cooking", "Travel", "Work & Business", "Education",
    "Health & Fitness", "Family & Relationships", "Hobbies & Entertainment",
    "Technology", "Nature & Environment", "Sports", "Shopping", "Transportation",
    "Weather", "Emotions & Feelings", "Time & Dates", "Colors", "Numbers & Math",
    "Music", "Art & Creativity", "Science", "History", "Geography", "Politics",
    "Religion", "Culture & Traditions", "Celebrations", "Animals", "Plants",
    "Buildings & Architecture", "Clothing & Fashion", "Money & Finance"
]

# UI Constants
PAGE_SIZE = 25

# Color codes for usage bars
USAGE_BAR_GREEN = "#238636"
USAGE_BAR_YELLOW = "#eab308"
USAGE_BAR_RED = "#ef4444"

# File paths
LANGUAGES_CONFIG_PATH = "languages.yaml"

# Session state keys (for consistency)
SESSION_PAGE = "page"
SESSION_GOOGLE_API_KEY = "google_api_key"
SESSION_CURRENT_BATCH_SIZE = "current_batch_size"
SESSION_LOADED_WORDS = "loaded_words"
SESSION_CURRENT_LANG_WORDS = "current_lang_words"
SESSION_COMPLETED_WORDS = "completed_words"
SESSION_SELECTION_MODE = "selection_mode"
SESSION_SENTENCES_PER_WORD = "sentences_per_word"
SESSION_AUDIO_SPEED = "audio_speed"

# ============================================================================
# GEMINI API WRAPPER WITH FALLBACKS
# ============================================================================

class GeminiAPI:
    """Unified Gemini API wrapper that supports both new and old APIs with fallbacks."""

    def __init__(self):
        self.api_type = None
        self.client = None
        self.genai = None

        # Try new API first
        try:
            from google import genai
            self.api_type = 'new'
            self.genai = genai
            logger.info("Using new Google GenAI API")
        except ImportError:
            logger.warning("No Google GenAI API available - using mock responses")
            self.api_type = 'mock'

    def configure(self, api_key: str):
        """Configure the API with the provided key."""
        if self.api_type == 'new':
            self.client = self.genai.Client(api_key=api_key)
        else:
            logger.warning("Mock API - no real configuration needed")

    def generate_content(self, model: str, contents: str, **kwargs):
        """Generate content using the appropriate API."""
        if self.api_type == 'new':
            return self.client.models.generate_content(
                model=model,
                contents=contents,
                **kwargs
            )
        else:
            # Mock response
            class MockResponse:
                def __init__(self, text):
                    self.text = text
            return MockResponse("Mock response - API not available")

# Global instance
_gemini_api = None

def get_gemini_api() -> GeminiAPI:
    """Get the global Gemini API instance."""
    global _gemini_api
    if _gemini_api is None:
        _gemini_api = GeminiAPI()
    return _gemini_api