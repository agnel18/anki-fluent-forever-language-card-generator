"""
Turkish Language Analyzer Domain Layer
=====================================

Domain components for Turkish language analysis following Clean Architecture.
Implements prevention-at-source methodology for agglutinative language processing.

Components:
- TrConfig: Configuration and linguistic rules
- TrPromptBuilder: Prevention-at-source prompt generation
- TrResponseParser: AI response parsing and validation
- TrValidator: Comprehensive analysis validation

Following gold standard patterns from German/Spanish analyzers.
"""

from .tr_config import TrConfig
from .tr_prompt_builder import TrPromptBuilder
from .tr_response_parser import TrResponseParser
from .tr_validator import TrValidator

__all__ = [
    # Configuration
    'TurkishConfig',

    # Prompt Building
    'TurkishPromptBuilder',

    # Response Parsing
    'TurkishResponseParser',
    'TurkishSentenceAnalysis',
    'TurkishAnalysisResult',

    # Validation
    'TurkishValidator',
    'ValidationResult',
    'ValidationIssue',
]