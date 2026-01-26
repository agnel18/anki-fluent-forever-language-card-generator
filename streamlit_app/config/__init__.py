# config/__init__.py - Config package initialization
"""
Configuration package for centralized settings management.
"""

from .models import (
    GEMINI_MODELS,
    get_gemini_model,
    get_gemini_fallback_model,
    get_available_gemini_models,
    is_deprecated_model,
    API_ENDPOINTS,
    get_gemini_endpoint,
    get_tts_endpoint,
    get_service_config,
)

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
    # Models
    'GEMINI_MODELS', 'get_gemini_model', 'get_gemini_fallback_model',
    'get_available_gemini_models', 'is_deprecated_model',
    'API_ENDPOINTS', 'get_gemini_endpoint', 'get_tts_endpoint',
    'get_service_config',

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