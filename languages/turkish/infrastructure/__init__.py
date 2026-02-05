"""
Turkish Language Analyzer Infrastructure Layer
============================================

Infrastructure components for Turkish language analysis.
Handles external dependencies and system integration.

Components:
- TurkishAnalyzerInfrastructure: Main infrastructure orchestrator
- AnalysisRequest/Response: Data transfer objects

Following Clean Architecture principles.
"""

from .tr_analyzer_infrastructure import (
    TurkishAnalyzerInfrastructure,
    AnalysisRequest,
    AnalysisResponse
)

__all__ = [
    'TurkishAnalyzerInfrastructure',
    'AnalysisRequest',
    'AnalysisResponse',
]