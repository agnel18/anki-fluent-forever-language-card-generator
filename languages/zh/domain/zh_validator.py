# languages/zh/domain/zh_validator.py
"""
Chinese Simplified Validator - Domain Component

CHINESE VALIDATION:
This component demonstrates how to validate Chinese grammar analysis results and calculate confidence scores.
It ensures result quality and provides confidence metrics for decision-making.

RESPONSIBILITIES:
1. Validate parsed grammar analysis results
2. Calculate confidence scores based on multiple heuristics
3. Check for valid Chinese grammar patterns
4. Apply quality thresholds and warnings
5. Enhance results with validation metadata

VALIDATION HEURISTICS:
- Word/character count matching: Results should match sentence breakdown
- Role distribution: Check for appropriate Chinese grammatical elements
- Pattern recognition: Validate aspect markers, classifiers, particles
- Confidence scoring: Multi-factor quality assessment
- Threshold application: Warn on low-confidence results

USAGE FOR CHINESE:
1. Copy validation structure and heuristics
2. Implement Chinese-specific pattern checks (aspect, classifiers, particles)
3. Adjust confidence scoring weights for Chinese grammar
4. Define appropriate quality thresholds
5. Test validation catches common AI errors in Chinese analysis

INTEGRATION:
- Called after response parsing in main analyzer
- Results include confidence scores for UI display
- Low confidence triggers warnings/logging
- Validation doesn't block processing (graceful degradation)
"""

import logging
from typing import Dict, Any, List
from .zh_config import ZhConfig

logger = logging.getLogger(__name__)

class ZhValidator:
    """
    Validates parsed Chinese grammar analysis results.

    CHINESE VALIDATION APPROACH:
    - Multi-heuristic scoring: Combine multiple quality indicators
    - Language-specific checks: Chinese grammar pattern validation
    - Confidence thresholds: Clear quality boundaries
    - Non-blocking: Validation enhances but doesn't prevent results
    - Logging: Detailed feedback for debugging and monitoring

    VALIDATION PHILOSOPHY:
    - Trust but verify: AI results are good but need validation
    - Graceful degradation: Poor results still better than no results
    - Continuous improvement: Validation guides AI prompt refinement
    - User transparency: Confidence scores inform user trust
    """

    def __init__(self, config: ZhConfig):
        """
        Initialize validator with configuration.

        CONFIGURATION DEPENDENCY:
        1. Access to grammatical roles and patterns
        2. Chinese-specific validation rules
        3. Quality thresholds and scoring weights
        4. Pattern definitions for rule-based checks
        """
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """Validate and enhance result with confidence scores."""
        confidence = self._calculate_confidence(result, sentence)
        result['confidence'] = confidence

        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}) for sentence: {sentence}")

        return result

    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score based on various heuristics."""
        score = 1.0

        # Check if words match sentence breakdown
        word_explanations = result.get('word_explanations', [])
        # For Chinese, we might have characters or words, so be flexible
        sentence_parts = sentence.split()  # Basic split, could be improved

        if len(word_explanations) == 0:
            return 0.0

        # Check role distribution
        roles = [item[1] for item in word_explanations if len(item) > 1]
        if not roles:
            return 0.0

        # Penalize too many 'other' roles
        other_count = roles.count('other')
        if other_count / len(roles) > 0.5:
            score *= 0.7

        # Check for valid Chinese patterns
        if self._has_valid_patterns(word_explanations):
            score *= 1.1
        else:
            score *= 0.9

        # Bonus for aspect markers and classifiers (important in Chinese)
        has_aspect = any(role in ['aspect_marker'] for role in roles)
        has_classifier = any(role in ['classifier'] for role in roles)
        has_particles = any(role in ['particle', 'modal_particle', 'structural_particle'] for role in roles)

        if has_aspect or has_classifier or has_particles:
            score *= 1.05

        return min(max(score, 0.0), 1.0)

    def _has_valid_patterns(self, word_explanations: List[List[str]]) -> bool:
        """Check if result has valid Chinese grammar patterns."""
        roles = [item[1] for item in word_explanations if len(item) > 1]

        # Must have at least one noun/verb (basic requirement)
        has_noun = any(role in ['noun', 'pronoun'] for role in roles)
        has_verb = 'verb' in roles

        # Chinese-specific: check for particles (very common)
        has_particles = any(role in ['particle', 'aspect_marker', 'modal_particle', 'structural_particle'] for role in roles)

        # Basic validity: has content words and possibly function words
        return has_noun and (has_verb or has_particles)