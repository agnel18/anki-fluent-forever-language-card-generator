# languages/hindi/domain/hi_validator.py
"""
Hindi Validator - Domain Component

GOLD STANDARD VALIDATION:
This component demonstrates how to validate grammar analysis results and calculate confidence scores.
It ensures result quality and provides confidence metrics for decision-making.

RESPONSIBILITIES:
1. Validate parsed grammar analysis results
2. Calculate confidence scores based on multiple heuristics
3. Check for valid Hindi grammar patterns
4. Apply quality thresholds and warnings
5. Enhance results with validation metadata

VALIDATION HEURISTICS:
- Word count matching: Results should match sentence word count
- Role distribution: Avoid too many 'other' roles
- Pattern recognition: Check for expected Hindi grammar patterns
- Confidence scoring: Multi-factor quality assessment
- Threshold application: Warn on low-confidence results

USAGE FOR NEW LANGUAGES:
1. Copy validation structure and heuristics
2. Implement language-specific pattern checks
3. Adjust confidence scoring weights for target language
4. Define appropriate quality thresholds
5. Test validation catches common AI errors

INTEGRATION:
- Called after response parsing in main analyzer
- Results include confidence scores for UI display
- Low confidence triggers warnings/logging
- Validation doesn't block processing (graceful degradation)
"""

import logging
from typing import Dict, Any, List
from .hi_config import HiConfig

logger = logging.getLogger(__name__)

class HiValidator:
    """
    Validates parsed grammar analysis results.

    GOLD STANDARD VALIDATION APPROACH:
    - Multi-heuristic scoring: Combine multiple quality indicators
    - Language-specific checks: Hindi grammar pattern validation
    - Confidence thresholds: Clear quality boundaries
    - Non-blocking: Validation enhances but doesn't prevent results
    - Logging: Detailed feedback for debugging and monitoring

    VALIDATION PHILOSOPHY:
    - Trust but verify: AI results are good but need validation
    - Graceful degradation: Poor results still better than no results
    - Continuous improvement: Validation guides AI prompt refinement
    - User transparency: Confidence scores inform user trust
    """

    def __init__(self, config: HiConfig):
        """
        Initialize validator with configuration.

        CONFIGURATION DEPENDENCY:
        1. Access to grammatical roles and patterns
        2. Language-specific validation rules
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

    def validate_explanation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality of word explanations for Hindi."""
        quality_score = 1.0
        issues = []

        word_explanations = result.get('word_explanations', [])
        explanations = result.get('explanations', {})

        for word_exp in word_explanations:
            if len(word_exp) >= 4:
                meaning = word_exp[3]
                if len(meaning) < 5:
                    quality_score *= 0.9
                    issues.append(f"Very short explanation for '{word_exp[0]}'")
                elif len(meaning) > 75:
                    quality_score *= 0.8
                    issues.append(f"Explanation too long for '{word_exp[0]}'")
            else:
                quality_score *= 0.8
                issues.append("Word explanation missing required fields")

        if not explanations:
            quality_score *= 0.7
            issues.append("Missing overall explanations section")
        else:
            overall_structure = explanations.get('overall_structure', '')
            key_features = explanations.get('key_features', '')

            if len(overall_structure.strip()) < 20:
                quality_score *= 0.9
                issues.append("Overall structure explanation too brief")

            if len(key_features.strip()) < 15:
                quality_score *= 0.9
                issues.append("Key features explanation too brief")

            hindi_features = ['postposition', 'gender', 'case', 'honorific', 'sov']
            combined = f"{overall_structure} {key_features}".lower()
            if not any(feature in combined for feature in hindi_features):
                quality_score *= 0.9
                issues.append("Explanations lack Hindi-specific grammatical features")

        quality_score = min(max(quality_score, 0.0), 1.0)

        return {
            'quality_score': quality_score,
            'issues': issues,
            'recommendations': self._generate_quality_recommendations(issues)
        }

    def _generate_quality_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on quality issues."""
        recommendations = []

        if any('brief' in issue.lower() for issue in issues):
            recommendations.append("Expand explanations to clarify grammatical function and relationships")

        if any('missing' in issue.lower() for issue in issues):
            recommendations.append("Include overall structure and key features in explanations")

        if any('hindi-specific' in issue.lower() for issue in issues):
            recommendations.append("Emphasize postpositions, agreement, and SOV structure in summaries")

        if not recommendations:
            recommendations.append("Analysis quality is good; consider adding more Hindi-specific details")

        return recommendations
    
    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score based on various heuristics."""
        score = 1.0
        
        # Check if words match sentence
        word_explanations = result.get('word_explanations', [])
        sentence_words = sentence.split()
        
        if len(word_explanations) != len(sentence_words):
            score *= 0.8
        
        # Check role distribution
        roles = [item[1] for item in word_explanations if len(item) > 1]
        if not roles:
            return 0.0
        
        # Penalize too many 'other' roles
        other_count = roles.count('other')
        if other_count / len(roles) > 0.5:
            score *= 0.7
        
        # Check for known patterns
        if self._has_valid_patterns(word_explanations):
            score *= 1.1
        else:
            score *= 0.9
        
        return min(max(score, 0.0), 1.0)
    
    def _has_valid_patterns(self, word_explanations: List[List[str]]) -> bool:
        """Check if result has valid Hindi grammar patterns."""
        # Simplified: check for subject-verb-object, postpositions, etc.
        roles = [item[1] for item in word_explanations if len(item) > 1]
        
        # Must have at least one noun and one verb
        has_noun = any(role in ['noun', 'pronoun'] for role in roles)
        has_verb = 'verb' in roles
        
        return has_noun and has_verb