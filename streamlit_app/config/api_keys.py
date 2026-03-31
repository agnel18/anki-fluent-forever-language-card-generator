# config/api_keys.py - Centralized API key management and validation
"""
Centralized API key management, validation, and environment variable handling.
Single source of truth for API key names, validation, and fallback mechanisms.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ============================================================================
# API KEY DEFINITIONS
# ============================================================================

API_KEY_CONFIG = {
    'gemini': {
        'env_var': 'GEMINI_API_KEY',
        'session_key': 'google_api_key',
        'description': 'Google Gemini AI API Key',
        'required': True,
        'validator': lambda key: key and len(key) > 10 and key.startswith(('AIza', 'sk-')),
    },
    'text_to_speech': {
        'env_var': 'GOOGLE_TTS_API_KEY',
        'session_key': 'google_tts_api_key',
        'description': 'Google Text-to-Speech API Key (separate billing project required)',
        'required': True,
        'validator': lambda key: key and len(key) > 10 and key.startswith(('AIza', 'sk-')),
    },
}

# ============================================================================
# API KEY MANAGEMENT FUNCTIONS
# ============================================================================

def get_api_key(service: str, session_state: Optional[Dict] = None) -> Optional[str]:
    """
    Get API key for a service, checking session state first, then environment.

    Args:
        service: Service name (e.g., 'gemini', 'text_to_speech')
        session_state: Streamlit session state dict (optional)

    Returns:
        API key string or None if not found
    """
    if service not in API_KEY_CONFIG:
        logger.warning(f"Unknown service: {service}")
        return None

    config = API_KEY_CONFIG[service]

    # Check session state first
    if session_state and config['session_key'] in session_state:
        key = session_state[config['session_key']]
        if key and not is_fallback_key(key):
            return key

    # Check environment variable
    env_key = os.getenv(config['env_var'])
    if env_key and not is_fallback_key(env_key):
        return env_key

    return None

def validate_api_key(service: str, api_key: str) -> Tuple[bool, str]:
    """
    Validate an API key for a service.

    Args:
        service: Service name
        api_key: API key to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if service not in API_KEY_CONFIG:
        return False, f"Unknown service: {service}"

    config = API_KEY_CONFIG[service]
    validator = config['validator']

    if not api_key:
        return False, "API key is empty"

    if is_fallback_key(api_key):
        return False, "Fallback/test key detected - please provide a real API key"

    try:
        if validator(api_key):
            return True, "Valid"
        else:
            return False, "Invalid API key format"
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def is_fallback_key(api_key: str) -> bool:
    """Check if an API key is a fallback/test key."""
    if not api_key:
        return True
    return api_key.startswith(('sk-fallback', 'test-', 'fallback-'))

def get_required_services() -> List[str]:
    """Get list of services that require API keys."""
    return [service for service, config in API_KEY_CONFIG.items() if config['required']]

def get_all_services() -> List[str]:
    """Get list of all configured services."""
    return list(API_KEY_CONFIG.keys())

def get_service_description(service: str) -> str:
    """Get human-readable description for a service."""
    if service in API_KEY_CONFIG:
        return API_KEY_CONFIG[service]['description']
    return f"Unknown service: {service}"

def check_api_key_availability(session_state: Optional[Dict] = None) -> Dict[str, bool]:
    """
    Check availability of API keys for all services.

    Args:
        session_state: Streamlit session state dict (optional)

    Returns:
        Dict mapping service names to availability status
    """
    availability = {}
    for service in get_all_services():
        key = get_api_key(service, session_state)
        availability[service] = key is not None and not is_fallback_key(key)
    return availability

# ============================================================================
# LEGACY COMPATIBILITY
# ============================================================================

def get_gemini_api_key(session_state: Optional[Dict] = None) -> Optional[str]:
    """Legacy function for backwards compatibility."""
    return get_api_key('gemini', session_state)

def get_tts_api_key(session_state: Optional[Dict] = None) -> Optional[str]:
    """Legacy function for backwards compatibility."""
    return get_api_key('text_to_speech', session_state)