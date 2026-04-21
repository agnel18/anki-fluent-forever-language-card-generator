"""
Dataclasses and type definitions for Chinese Simplified analyzer.
Mirrors the structure of the Traditional analyzer for type safety and clarity.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class AnalysisRequest:
    sentence: str
    target_word: Optional[str] = None
    complexity: str = "intermediate"
    analysis_type: str = "single"  # "single" or "batch"

@dataclass
class AnalysisResult:
    success: bool
    sentence: str
    words: List[Dict[str, Any]]
    overall_structure: str
    key_features: str
    confidence: float
    validation_issues: List[str]
    validation_suggestions: List[str]
    error_message: Optional[str] = None
    fallback_used: bool = False

@dataclass
class BatchAnalysisResult:
    success: bool
    results: List[AnalysisResult]
    total_sentences: int
    average_confidence: float
    error_message: Optional[str] = None
    fallback_used: bool = False

@dataclass
class ParsedWord:
    word: str
    grammatical_role: str
    individual_meaning: str
    confidence: float = 1.0

@dataclass
class ParsedSentence:
    sentence: str
    words: List[ParsedWord]
    overall_structure: str
    key_features: str
    confidence: float = 1.0

@dataclass
class ParseResult:
    sentences: List[ParsedSentence]
    success: bool
    error_message: Optional[str] = None
    fallback_used: bool = False

@dataclass
class ValidationResult:
    is_valid: bool
    confidence_score: float
    issues: List[str]
    suggestions: List[str]
