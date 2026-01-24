# config/defaults.py - Default settings for generation parameters
"""
Default configuration values for deck generation, audio, and other app settings.
Centralized defaults to ensure consistency across the application.
"""

from typing import Dict, Any

# ============================================================================
# DECK GENERATION DEFAULTS
# ============================================================================

DECK_GENERATION_DEFAULTS = {
    'sentences_per_word': {
        'min': 1,
        'max': 20,
        'default': 10,
        'description': 'Number of example sentences to generate per word'
    },
    'sentence_length': {
        'min_length': {
            'min': 3,
            'max': 10,
            'default': 5,
            'description': 'Minimum words per sentence'
        },
        'max_length': {
            'min': 10,
            'max': 30,
            'default': 20,
            'description': 'Maximum words per sentence'
        }
    },
    'difficulty_levels': ['beginner', 'intermediate', 'advanced'],
    'default_difficulty': 'intermediate',
    'audio_speed': {
        'min': 0.5,
        'max': 2.0,
        'default': 0.8,
        'description': 'Audio playback speed multiplier'
    },
    'max_words_per_deck': 50,
    'max_sentences_per_deck': 500,
}

# ============================================================================
# AUDIO GENERATION DEFAULTS
# ============================================================================

AUDIO_DEFAULTS = {
    'voice': {
        'default': 'auto',
        'description': 'Default voice selection (auto-detect based on language)'
    },
    'format': 'mp3',
    'quality': 'high',
    'max_concurrent_generations': 3,
    'timeout_seconds': 30,
}

# ============================================================================
# IMAGE GENERATION DEFAULTS
# ============================================================================

IMAGE_DEFAULTS = {
    'max_images_per_word': 3,
    'image_size': 'medium',
    'safe_search': True,
    'max_concurrent_downloads': 5,
    'timeout_seconds': 15,
}

# ============================================================================
# CACHE AND PERFORMANCE DEFAULTS
# ============================================================================

CACHE_DEFAULTS = {
    'sentence_cache_ttl': 3600 * 24 * 7,  # 7 days
    'image_cache_ttl': 3600 * 24 * 30,    # 30 days
    'audio_cache_ttl': 3600 * 24 * 30,    # 30 days
    'max_cache_size_mb': 500,
    'cleanup_interval_hours': 24,
}

# ============================================================================
# UI AND DISPLAY DEFAULTS
# ============================================================================

UI_DEFAULTS = {
    'max_display_words': 10,
    'max_display_sentences': 5,
    'progress_update_interval': 0.5,  # seconds
    'log_display_lines': 100,
    'sidebar_collapsed': False,
}

# ============================================================================
# VALIDATION AND LIMITS
# ============================================================================

VALIDATION_LIMITS = {
    'word': {
        'min_length': 1,
        'max_length': 50,
    },
    'sentence': {
        'min_length': 3,
        'max_length': 200,
    },
    'api_call': {
        'max_retries': 3,
        'retry_delay': 1.0,
        'timeout': 30.0,
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_default_sentences_per_word() -> int:
    """Get default number of sentences per word."""
    return DECK_GENERATION_DEFAULTS['sentences_per_word']['default']

def get_default_sentence_length_range() -> tuple:
    """Get default sentence length range as (min, max)."""
    min_len = DECK_GENERATION_DEFAULTS['sentence_length']['min_length']['default']
    max_len = DECK_GENERATION_DEFAULTS['sentence_length']['max_length']['default']
    return (min_len, max_len)

def get_default_difficulty() -> str:
    """Get default difficulty level."""
    return DECK_GENERATION_DEFAULTS['default_difficulty']

def get_default_audio_speed() -> float:
    """Get default audio speed."""
    return DECK_GENERATION_DEFAULTS['audio_speed']['default']

def get_difficulty_levels() -> list:
    """Get list of available difficulty levels."""
    return DECK_GENERATION_DEFAULTS['difficulty_levels']

def validate_generation_params(sentences_per_word: int = None,
                             min_length: int = None,
                             max_length: int = None,
                             difficulty: str = None) -> Dict[str, Any]:
    """
    Validate and normalize generation parameters.

    Returns dict with validated parameters and any warnings.
    """
    warnings = []
    params = {}

    # Sentences per word
    if sentences_per_word is None:
        params['sentences_per_word'] = get_default_sentences_per_word()
    else:
        min_val = DECK_GENERATION_DEFAULTS['sentences_per_word']['min']
        max_val = DECK_GENERATION_DEFAULTS['sentences_per_word']['max']
        if sentences_per_word < min_val:
            params['sentences_per_word'] = min_val
            warnings.append(f"Sentences per word increased to minimum: {min_val}")
        elif sentences_per_word > max_val:
            params['sentences_per_word'] = max_val
            warnings.append(f"Sentences per word decreased to maximum: {max_val}")
        else:
            params['sentences_per_word'] = sentences_per_word

    # Sentence length range
    default_min, default_max = get_default_sentence_length_range()
    params['min_length'] = min_length if min_length is not None else default_min
    params['max_length'] = max_length if max_length is not None else default_max

    if params['min_length'] >= params['max_length']:
        params['min_length'] = default_min
        params['max_length'] = default_max
        warnings.append("Invalid sentence length range, using defaults")

    # Difficulty
    if difficulty is None:
        params['difficulty'] = get_default_difficulty()
    elif difficulty not in get_difficulty_levels():
        params['difficulty'] = get_default_difficulty()
        warnings.append(f"Invalid difficulty '{difficulty}', using default")
    else:
        params['difficulty'] = difficulty

    return {
        'params': params,
        'warnings': warnings,
        'valid': len(warnings) == 0
    }