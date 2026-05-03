# languages/russian/infrastructure/ru_fallbacks.py
"""
Re-export Russian fallbacks from domain layer.
Infrastructure layer — external concerns (data, I/O).
"""

from ..domain.ru_fallbacks import RuFallbacks

__all__ = ["RuFallbacks"]
