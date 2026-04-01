# config/__init__.py - Config package initialization
"""
Configuration package for centralized settings management.
Note: Model configuration lives in shared_utils.py (canonical source).
"""

from .api_keys import (
    get_api_key,
    validate_api_key,
    is_fallback_key,
    get_required_services,
    get_all_services,
    get_service_description,
    check_api_key_availability,
    get_gemini_api_key,
    get_tts_api_key,
)

from .defaults import (
    DECK_GENERATION_DEFAULTS,
    AUDIO_DEFAULTS,
    IMAGE_DEFAULTS,
    CACHE_DEFAULTS,
    UI_DEFAULTS,
    VALIDATION_LIMITS,
    get_default_sentences_per_word,
    get_default_sentence_length_range,
    get_default_difficulty,
    get_default_audio_speed,
    get_difficulty_levels,
    validate_generation_params,
)

__all__ = [
    # API Keys
    'get_api_key', 'validate_api_key', 'is_fallback_key',
    'get_required_services', 'get_all_services', 'get_service_description',
    'check_api_key_availability', 'get_gemini_api_key', 'get_tts_api_key',

    # Defaults
    'DECK_GENERATION_DEFAULTS', 'AUDIO_DEFAULTS', 'IMAGE_DEFAULTS',
    'CACHE_DEFAULTS', 'UI_DEFAULTS', 'VALIDATION_LIMITS',
    'get_default_sentences_per_word', 'get_default_sentence_length_range',
    'get_default_difficulty', 'get_default_audio_speed', 'get_difficulty_levels',
    'validate_generation_params',
]