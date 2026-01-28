# languages/chinese_traditional/domain/zh_tw_validator.py
"""
Chinese Traditional Validator - Domain Component

Following Chinese Simplified Clean Architecture gold standard:
- Natural confidence scoring based on linguistic patterns
- Validation of grammatical role assignments
- Assessment of explanation quality and completeness
- Integration with configuration for validation rules

RESPONSIBILITIES:
1. Validate grammatical role assignments against linguistic rules
2. Assess explanation quality and completeness
3. Calculate natural confidence scores based on Chinese patterns
4. Provide validation feedback for response quality
5. Support different complexity levels in validation

INTEGRATION:
- Used by ZhTwResponseParser for confidence scoring
- Depends on ZhTwConfig for validation patterns and rules
- Works with ZhTwAnalyzer facade for final validation
- Provides quality metrics for UI presentation

VALIDATION STRATEGY:
1. Linguistic rule validation (Chinese-specific patterns)
2. Explanation completeness assessment
3. Confidence score calculation based on multiple factors
4. Complexity-level appropriate validation
"""

import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .zh_tw_config import ZhTwConfig, ComplexityLevel
from .zh_tw_response_parser import ParsedWord, ParsedSentence

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of validation with confidence scores."""
    is_valid: bool
    confidence_score: float
    issues: List[str]
    suggestions: List[str]

class ZhTwValidator:
    """
    Validates Chinese Traditional grammatical analysis results.

    Following Chinese Simplified Clean Architecture:
    - Natural validation: Linguistic rule-based assessment
    - Confidence scoring: Multi-factor confidence calculation
    - Quality metrics: Explanation completeness and accuracy
    - Complexity awareness: Different standards for different levels

    VALIDATION DIMENSIONS:
    1. Grammatical role validity (Chinese linguistic rules)
    2. Explanation quality (completeness, clarity, accuracy)
    3. Structural coherence (sentence-level relationships)
    4. Chinese-specific features (aspect, particles, classifiers)
    """

    def __init__(self, config: ZhTwConfig):
        """
        Initialize validator with configuration.

        Args:
            config: ZhTwConfig instance with validation patterns
        """
        self.config = config
        self._init_validation_patterns()

    def _init_validation_patterns(self):
        """Initialize validation patterns from configuration."""
        # Chinese Traditional specific validation patterns
        self.aspect_markers = set(self.config.aspect_markers.keys())
        self.modal_particles = set(self.config.modal_particles.keys())
        self.structural_particles = set(self.config.structural_particles.keys())
        self.common_classifiers = set(self.config.common_classifiers)

        # Role compatibility patterns (what roles can co-occur)
        self.role_patterns = {
            "verb": ["aspect_particle", "modal_particle", "adverb", "object"],
            "noun": ["measure_word", "structural_particle", "preposition"],
            "adjective": ["adverb", "structural_particle"],
            "numeral": ["measure_word", "noun"]
        }

    def validate_parsed_sentence(self, sentence: ParsedSentence, complexity: str = "intermediate") -> ValidationResult:
        """
        Validate a parsed sentence with comprehensive analysis.

        VALIDATION PROCESS:
        1. Individual word validation
        2. Structural coherence check
        3. Chinese-specific feature validation
        4. Explanation quality assessment
        5. Confidence score calculation

        Args:
            sentence: ParsedSentence to validate
            complexity: Learning complexity level

        Returns:
            ValidationResult with confidence and feedback
        """
        issues = []
        suggestions = []
        confidence_factors = []

        # Validate individual words
        word_validations = []
        for word in sentence.words:
            word_validation = self._validate_word(word, sentence, complexity)
            word_validations.append(word_validation)
            issues.extend(word_validation.issues)
            suggestions.extend(word_validation.suggestions)
            confidence_factors.append(word_validation.confidence_score)

        # Validate sentence structure
        structure_validation = self._validate_sentence_structure(sentence)
        issues.extend(structure_validation.issues)
        suggestions.extend(structure_validation.suggestions)
        confidence_factors.append(structure_validation.confidence_score)

        # Validate Chinese-specific features
        chinese_validation = self._validate_chinese_features(sentence)
        issues.extend(chinese_validation.issues)
        suggestions.extend(chinese_validation.suggestions)
        confidence_factors.append(chinese_validation.confidence_score)

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(confidence_factors)

        # Adjust for complexity level
        overall_confidence = self._adjust_confidence_for_complexity(overall_confidence, complexity)

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=overall_confidence,
            issues=issues,
            suggestions=suggestions
        )

    def _validate_word(self, word: ParsedWord, sentence: ParsedSentence, complexity: str) -> ValidationResult:
        """
        Validate individual word analysis.

        WORD VALIDATION CRITERIA:
        - Grammatical role validity
        - Explanation completeness
        - Role-word compatibility
        - Chinese character appropriateness
        """
        issues = []
        suggestions = []
        confidence = 1.0

        # Validate grammatical role
        if word.grammatical_role == "unknown":
            issues.append(f"Unknown grammatical role for word '{word.word}'")
            confidence *= 0.6
            suggestions.append(f"Consider classifying '{word.word}' as noun, verb, or particle")

        # Validate role-word compatibility
        role_confidence = self._validate_role_word_compatibility(word)
        confidence *= role_confidence

        if role_confidence < 0.8:
            suggestions.append(f"Review grammatical role assignment for '{word.word}'")

        # Validate explanation quality
        explanation_confidence = self._validate_explanation_quality(word.individual_meaning, complexity)
        confidence *= explanation_confidence

        if explanation_confidence < 0.7:
            issues.append(f"Explanation for '{word.word}' lacks detail")
            suggestions.append(f"Provide more specific explanation of '{word.word}'s grammatical function")

        # Validate Chinese character appropriateness
        if not self._is_chinese_character(word.word):
            issues.append(f"Word '{word.word}' may not be valid Chinese Traditional character")
            confidence *= 0.8

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=confidence,
            issues=issues,
            suggestions=suggestions
        )

    def _validate_sentence_structure(self, sentence: ParsedSentence) -> ValidationResult:
        """
        Validate sentence-level structural coherence.

        STRUCTURAL VALIDATION:
        - Role distribution balance
        - Required element presence
        - Relationship coherence
        - Overall structure explanation
        """
        issues = []
        suggestions = []
        confidence = 1.0

        roles = [w.grammatical_role for w in sentence.words]

        # Check for basic sentence elements
        has_subject = any(role in ["noun", "pronoun"] for role in roles)
        has_predicate = any(role in ["verb", "adjective"] for role in roles)

        if not has_subject:
            issues.append("Sentence appears to lack a subject (noun or pronoun)")
            confidence *= 0.8
            suggestions.append("Identify the subject of the sentence")

        if not has_predicate:
            issues.append("Sentence appears to lack a predicate (verb or adjective)")
            confidence *= 0.7
            suggestions.append("Identify the main verb or adjective in the sentence")

        # Check role distribution
        unknown_count = roles.count("unknown")
        if unknown_count > len(roles) * 0.3:
            issues.append(f"Too many unknown roles ({unknown_count}/{len(roles)})")
            confidence *= 0.7

        # Validate structure explanation
        if len(sentence.overall_structure) < 20:
            issues.append("Overall structure explanation is too brief")
            confidence *= 0.8
            suggestions.append("Provide more detailed explanation of sentence structure")

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=confidence,
            issues=issues,
            suggestions=suggestions
        )

    def _validate_chinese_features(self, sentence: ParsedSentence) -> ValidationResult:
        """
        Validate Chinese-specific grammatical features.

        CHINESE FEATURE VALIDATION:
        - Aspect particle usage
        - Measure word/classifier presence
        - Modal particle appropriateness
        - Traditional character usage
        """
        issues = []
        suggestions = []
        confidence = 1.0

        words = [w.word for w in sentence.words]
        roles = [w.grammatical_role for w in sentence.words]

        # Check aspect particle usage
        aspect_indices = [i for i, role in enumerate(roles) if role == "aspect_particle"]
        for idx in aspect_indices:
            if idx == 0 or roles[idx - 1] != "verb":
                issues.append(f"Aspect particle '{words[idx]}' should follow a verb")
                confidence *= 0.9
                suggestions.append(f"Ensure aspect particle '{words[idx]}' is correctly positioned after its verb")

        # Check measure word usage
        measure_indices = [i for i, role in enumerate(roles) if role == "measure_word"]
        for idx in measure_indices:
            # Measure words should precede nouns and follow numerals
            if idx > 0 and roles[idx - 1] not in ["numeral", "noun"]:
                suggestions.append(f"Review positioning of measure word '{words[idx]}'")
            if idx < len(roles) - 1 and roles[idx + 1] != "noun":
                issues.append(f"Measure word '{words[idx]}' should precede a noun")
                confidence *= 0.9

        # Check modal particle positioning
        modal_indices = [i for i, role in enumerate(roles) if role == "modal_particle"]
        for idx in modal_indices:
            if idx != len(roles) - 1:
                suggestions.append(f"Modal particle '{words[idx]}' typically appears at sentence end")

        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_score=confidence,
            issues=issues,
            suggestions=suggestions
        )

    def _validate_role_word_compatibility(self, word: ParsedWord) -> float:
        """
        Validate compatibility between word and assigned grammatical role.

        ROLE-WORD COMPATIBILITY:
        - Check against known patterns
        - Consider Chinese character types
        - Assess contextual appropriateness
        """
        confidence = 1.0

        # Check against known incompatible patterns
        if word.grammatical_role == "verb" and word.word in self.aspect_markers:
            confidence *= 0.3  # Aspect markers shouldn't be classified as verbs

        if word.grammatical_role == "noun" and word.word in self.modal_particles:
            confidence *= 0.3  # Modal particles aren't nouns

        # Check for common misclassifications
        if word.word in ["的", "地", "得"] and word.grammatical_role != "structural_particle":
            confidence *= 0.5
            logger.warning(f"Structural particle '{word.word}' incorrectly classified as {word.grammatical_role}")

        return confidence

    def _validate_explanation_quality(self, explanation: str, complexity: str) -> float:
        """
        Assess quality of grammatical explanation.

        EXPLANATION QUALITY CRITERIA:
        - Length appropriateness for complexity
        - Presence of key terms
        - Clarity and specificity
        - Linguistic accuracy
        """
        if not explanation:
            return 0.0

        confidence = 1.0
        length = len(explanation)

        # Length expectations by complexity
        min_lengths = {
            "beginner": 20,
            "intermediate": 30,
            "advanced": 40
        }

        min_length = min_lengths.get(complexity, 30)
        if length < min_length:
            confidence *= 0.7

        # Check for key linguistic terms
        key_terms = ["function", "role", "relationship", "meaning", "structure"]
        term_count = sum(1 for term in key_terms if term.lower() in explanation.lower())
        if term_count < 2:
            confidence *= 0.8

        # Check for Chinese-specific terms
        chinese_terms = ["aspect", "particle", "classifier", "measure word", "modal"]
        chinese_term_count = sum(1 for term in chinese_terms if term.lower() in explanation.lower())
        if chinese_term_count == 0:
            confidence *= 0.9

        return confidence

    def _is_chinese_character(self, word: str) -> bool:
        """
        Check if word contains valid Chinese Traditional characters.

        CHINESE CHARACTER VALIDATION:
        - Traditional character range
        - Common punctuation
        - Basic sanity check
        """
        if not word:
            return False

        # Check if all characters are Chinese or common punctuation
        for char in word:
            code = ord(char)
            # Traditional Chinese range + common punctuation
            if not (0x4E00 <= code <= 0x9FFF or  # CJK Unified Ideographs
                    char in "，。！？；：""''（）【】《》"):
                return False

        return True

    def _calculate_overall_confidence(self, confidence_factors: List[float]) -> float:
        """
        Calculate overall confidence from multiple factors.

        CONFIDENCE CALCULATION:
        - Weighted average of factors
        - Penalty for low individual scores
        - Bonus for consistently high scores
        """
        if not confidence_factors:
            return 0.0

        # Weighted average with emphasis on lower scores
        avg_confidence = sum(confidence_factors) / len(confidence_factors)

        # Apply penalty for any very low confidence factors
        min_confidence = min(confidence_factors)
        if min_confidence < 0.5:
            avg_confidence *= 0.8

        return max(0.0, min(1.0, avg_confidence))

    def _adjust_confidence_for_complexity(self, confidence: float, complexity: str) -> float:
        """
        Adjust confidence score based on complexity level.

        COMPLEXITY ADJUSTMENTS:
        - Beginner: More lenient validation
        - Advanced: Stricter requirements
        - Intermediate: Standard validation
        """
        adjustments = {
            "beginner": 1.1,    # Slight bonus for beginners
            "intermediate": 1.0, # Standard
            "advanced": 0.95    # Slight penalty for advanced (higher expectations)
        }

        adjustment = adjustments.get(complexity, 1.0)
        return max(0.0, min(1.0, confidence * adjustment))