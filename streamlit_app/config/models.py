# config/models.py - Centralized model and API endpoint configuration
"""
Centralized configuration for AI models and API endpoints.
Single source of truth for model names, API endpoints, and service configurations.
"""

import os
from typing import Dict, List, Optional

# ============================================================================
# GEMINI AI MODELS
# ============================================================================
# Source: https://ai.google.dev/gemini-api/docs/models  (updated 2026-03-10)
#         https://ai.google.dev/gemini-api/docs/pricing (updated 2026-03-12)
#
# gemini-2.5-flash  : STABLE. Best price-performance, 1M context, thinking support.
#                     Free tier: tokens free of charge, ~1,500 RPD, 10 RPM.
#                     Paid: $0.30/1M input, $2.50/1M output.
#
# gemini-3-flash-preview : PREVIEW. Frontier-class, multimodal, agentic.
#                          Free tier: free of charge; note MORE RESTRICTIVE rate limits
#                          (preview models). Verify exact RPD in AI Studio.
#                          Paid: $0.50/1M input, $3.00/1M output.
#
# Verify your live rate limits at: https://aistudio.google.com/rate-limit

GEMINI_MODELS = {
    'default': 'gemini-2.5-flash',          # Stable — recommended for production
    'fallback': 'gemini-3-flash-preview',   # Preview — higher capability, more restrictive limits
    'deprecated': [
        'gemini-1.5-flash',        # Deprecated (no shutdown date announced)
        'gemini-2.0-flash',        # Deprecated — shut down June 1, 2026
        'gemini-2.0-flash-lite',   # Deprecated — shut down June 1, 2026
        'gemini-3-pro-preview',    # SHUT DOWN March 9, 2026
    ],
}

def get_gemini_model() -> str:
    """Get the primary Gemini model, with environment override."""
    return os.getenv('GEMINI_MODEL', GEMINI_MODELS['default'])

def get_gemini_fallback_model() -> str:
    """Get the fallback Gemini model, with environment override."""
    return os.getenv('GEMINI_FALLBACK_MODEL', GEMINI_MODELS['fallback'])

def get_available_gemini_models() -> List[str]:
    """Get list of all available Gemini models."""
    return [get_gemini_model(), get_gemini_fallback_model()] + GEMINI_MODELS['deprecated']

def is_deprecated_model(model: str) -> bool:
    """Check if a model is deprecated."""
    return model in GEMINI_MODELS['deprecated']

# ============================================================================
# API ENDPOINTS
# ============================================================================

API_ENDPOINTS = {
    'gemini': {
        'base_url': 'https://generativelanguage.googleapis.com',
        'generate_content': '/v1beta/models/{model}:generateContent',
        'list_models': '/v1beta/models',
    },
    'text_to_speech': {
        'base_url': 'https://texttospeech.googleapis.com',
        'synthesize': '/v1/text:synthesize',
        'voices': '/v1/voices',
    }
}

def get_gemini_endpoint(operation: str = 'generate_content') -> str:
    """Get Gemini API endpoint URL."""
    base = API_ENDPOINTS['gemini']['base_url']
    path = API_ENDPOINTS['gemini'][operation]
    return f"{base}{path}"

def get_tts_endpoint(operation: str = 'synthesize') -> str:
    """Get Google Text-to-Speech API endpoint URL."""
    base = API_ENDPOINTS['text_to_speech']['base_url']
    path = API_ENDPOINTS['text_to_speech'][operation]
    return f"{base}{path}"

# ============================================================================
# SERVICE CONFIGURATION
# ============================================================================

SERVICE_CONFIG = {
    'gemini': {
        'max_tokens': 20000,
        'temperature': 0.7,
        'top_p': 0.8,
        'top_k': 40,
    },
    'text_to_speech': {
        'audio_encoding': 'MP3',
        'speaking_rate': 1.0,
        'pitch': 0.0,
    }
}

def get_service_config(service: str) -> Dict:
    """Get configuration for a specific service."""
    return SERVICE_CONFIG.get(service, {})