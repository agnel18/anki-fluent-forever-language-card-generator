"""
Turkish Language Analyzer
========================

Turkish (Türkçe) language analyzer for the Language Learning application.
Implements comprehensive morphological analysis with prevention-at-source methodology.

Key Features:
- Agglutination handling with morphological decomposition
- Vowel harmony validation and correction
- Case system analysis (6 cases)
- Word order flexibility with case-based disambiguation
- Prevention-at-source prompt engineering
- Multi-level complexity analysis (beginner/intermediate/advanced)

Architecture:
- Clean Architecture with domain/infrastructure separation
- Prevention-at-source methodology (learned from German/Spanish gold standards)
- Comprehensive validation and error handling
- External configuration support

Usage:
    from languages.turkish import TurkishAnalyzer

    analyzer = TrAnalyzer()
    result = analyzer.analyze("Merhaba dünya!")
    print(analyzer.format_analysis_result(result))
"""

from .tr_analyzer import TrAnalyzer

# Version info
__version__ = "1.0.0"
__language__ = "Turkish"
__language_code__ = "tr"

# Main exports
__all__ = [
    'TurkishAnalyzer',
    '__version__',
    '__language__',
    '__language_code__'
]