# Language Analyzers Package
# Provides language-specific grammar analysis for 77 languages

from .base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis
from .analyzer_registry import AnalyzerRegistry, get_registry, get_analyzer, get_available_languages, is_language_supported

__all__ = [
    'BaseGrammarAnalyzer',
    'LanguageConfig',
    'GrammarAnalysis',
    'AnalyzerRegistry',
    'get_registry',
    'get_analyzer',
    'get_available_languages',
    'is_language_supported'
]

__version__ = "1.0.0"