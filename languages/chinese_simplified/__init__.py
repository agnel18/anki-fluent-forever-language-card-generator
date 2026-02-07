# languages/chinese_simplified/__init__.py
"""
Chinese Simplified Grammar Analyzer Package

This package provides comprehensive grammar analysis for Chinese Simplified.
It follows domain-driven design principles with clean architecture.

MAIN COMPONENTS:
- ZhAnalyzer: Main facade orchestrating all analysis components
- zh_grammar_concepts.md: Linguistic research and implementation guide

DOMAIN COMPONENTS (in domain/):
- ZhConfig: Configuration and color schemes
- ZhPromptBuilder: AI prompt generation
- ZhResponseParser: Response parsing and fallbacks
- ZhValidator: Quality validation and confidence scoring
- ZhFallbacks: Rule-based error recovery
- ZhPatterns: Linguistic pattern recognition

ARCHITECTURE:
- Clean Architecture: Domain logic separated from infrastructure
- Domain-Driven Design: Business logic organized by domain concepts
- Facade Pattern: Single entry point through ZhAnalyzer
- Error Recovery: Comprehensive fallbacks ensure user experience

USAGE:
    from languages.chinese_simplified.zh_analyzer import ZhAnalyzer

    analyzer = ZhAnalyzer()
    result = analyzer.analyze_grammar("æˆ‘åƒäº†ä¸€ä¸ªè‹¹æžœ", "è‹¹æžœ", "intermediate", api_key)
"""

from .zh_analyzer import ZhAnalyzer

__all__ = ['ZhAnalyzer']

