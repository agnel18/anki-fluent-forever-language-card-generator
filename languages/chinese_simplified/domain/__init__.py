# languages/zh/domain/__init__.py
"""
Chinese Simplified Domain Components Package

This package contains all domain components for Chinese Simplified grammar analysis.
Domain components are the core business logic separated from infrastructure concerns.

COMPONENTS:
- ZhConfig: Configuration management and color schemes
- ZhPromptBuilder: AI prompt generation using templates
- ZhResponseParser: AI response parsing and fallback application
- ZhValidator: Result validation and confidence scoring
- ZhFallbacks: Rule-based error recovery
- ZhPatterns: Regex patterns for linguistic features

ARCHITECTURAL PRINCIPLES:
- Domain-Driven Design: Business logic separated from infrastructure
- Dependency Injection: Components receive dependencies via constructor
- Single Responsibility: Each component has one clear purpose
- Clean Architecture: Dependencies point inward toward domain
"""

from .zh_config import ZhConfig
from .zh_prompt_builder import ZhPromptBuilder
from .zh_response_parser import ZhResponseParser
from .zh_validator import ZhValidator
from .zh_fallbacks import ZhFallbacks
from .zh_patterns import ZhPatterns

__all__ = [
    'ZhConfig',
    'ZhPromptBuilder',
    'ZhResponseParser',
    'ZhValidator',
    'ZhFallbacks',
    'ZhPatterns'
]