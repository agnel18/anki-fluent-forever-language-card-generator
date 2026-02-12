# Spanish Validator
# Validates Spanish analysis results and calculates confidence scores
# Spanish-specific validation for agreement, conjugation, etc.

import logging
from typing import Dict, List, Any
from .es_config import EsConfig

logger = logging.getLogger(__name__)

class EsValidator:
    """
    Validates Spanish analysis results.
    Checks for Spanish-specific linguistic patterns and calculates confidence.
    """

    def __init__(self, config: EsConfig):
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """
        Validate analysis result and calculate confidence score.
        Spanish-specific validation includes agreement checking, conjugation validation, etc.
        """
        confidence = 0.8  # Start with high confidence for Spanish (inflectional language)

        try:
            word_explanations = result.get('word_explanations') or result.get('words', [])

            # Check for minimum requirements
            if len(word_explanations) == 0:
                confidence = 0.1
                logger.warning("No word explanations found")

            # Check for explanations
            explanations_key = 'explanations' if 'explanations' in result else 'overall_analysis'
            if explanations_key not in result:
                confidence *= 0.7
                logger.warning("No explanations section found")

            # Spanish-specific validations
            confidence *= self._validate_spanish_patterns(result, sentence)

            # Ensure confidence is within bounds
            confidence = max(0.0, min(1.0, confidence))

            result['confidence'] = confidence
            logger.info(f"Spanish validation complete. Confidence: {confidence:.2f}")

        except Exception as e:
            logger.error(f"Error in Spanish validation: {e}")
            result['confidence'] = 0.1

        return result

    def validate_explanation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality of word explanations for Spanish."""
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

            spanish_features = ['agreement', 'gender', 'conjugation', 'tense', 'ser', 'estar']
            combined = f"{overall_structure} {key_features}".lower()
            if not any(feature in combined for feature in spanish_features):
                quality_score *= 0.9
                issues.append("Explanations lack Spanish-specific grammatical features")

        quality_score = max(0.0, min(1.0, quality_score))

        return {
            'quality_score': quality_score,
            'issues': issues,
            'recommendations': self._generate_quality_recommendations(issues)
        }

    def _generate_quality_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on quality issues."""
        recommendations = []

        if any('brief' in issue.lower() for issue in issues):
            recommendations.append("Provide clearer explanations of Spanish grammatical function")

        if any('missing' in issue.lower() for issue in issues):
            recommendations.append("Include overall structure and key features for each sentence")

        if any('spanish-specific' in issue.lower() for issue in issues):
            recommendations.append("Highlight agreement, conjugation, and tense usage in summaries")

        if not recommendations:
            recommendations.append("Analysis quality is good; consider adding more Spanish-specific details")

        return recommendations

    def _validate_spanish_patterns(self, result: Dict[str, Any], sentence: str) -> float:
        """
        Validate Spanish-specific linguistic patterns.
        Returns a multiplier for confidence score.
        """
        multiplier = 1.0

        try:
            words_data = result.get('words') or result.get('word_explanations', [])

            # Check for agreement patterns
            agreement_score = self._check_agreement_patterns(words_data)
            multiplier *= agreement_score

            # Check for verb conjugation consistency
            conjugation_score = self._check_verb_conjugation(words_data, sentence)
            multiplier *= conjugation_score

            # Check for preposition usage
            preposition_score = self._check_preposition_usage(words_data)
            multiplier *= preposition_score

            # Check for determiner-noun agreement
            determiner_score = self._check_determiner_agreement(words_data)
            multiplier *= determiner_score

        except Exception as e:
            logger.error(f"Error in Spanish pattern validation: {e}")
            multiplier *= 0.8  # Slight penalty for validation errors

        return multiplier

    def _check_agreement_patterns(self, words_data: List[Dict[str, Any]]) -> float:
        """Check for gender/number agreement between adjectives and nouns"""
        # This is a simplified check - could be expanded with more sophisticated analysis
        score = 1.0

        # Look for adjective-noun pairs
        nouns = [w for w in words_data if w.get('grammatical_role') == 'noun']
        adjectives = [w for w in words_data if w.get('grammatical_role') == 'adjective']

        if len(adjectives) > 0 and len(nouns) > 0:
            # Basic check: if we have both, assume agreement for now
            # In a full implementation, this would check actual agreement rules
            score = 0.9  # Slight penalty for not doing detailed checking yet

        return score

    def _check_verb_conjugation(self, words_data: List[Dict[str, Any]], sentence: str) -> float:
        """Check for consistent verb conjugation patterns"""
        score = 1.0

        verbs = [w for w in words_data if w.get('grammatical_role') == 'verb']

        if len(verbs) > 1:
            # Check if verb forms are consistent (e.g., same tense/person)
            # This is simplified - real implementation would parse conjugation
            score = 0.9

        return score

    def _check_preposition_usage(self, words_data: List[Dict[str, Any]]) -> float:
        """Check for appropriate preposition usage (por/para distinction)"""
        score = 1.0

        prepositions = [w for w in words_data if w.get('grammatical_role') == 'preposition']

        # Look for por/para usage
        por_para_found = any(w.get('word', '').lower() in ['por', 'para'] for w in prepositions)

        if por_para_found:
            # In a full implementation, this would check contextual appropriateness
            score = 0.9  # Slight penalty for not doing detailed checking

        return score

    def _check_determiner_agreement(self, words_data: List[Dict[str, Any]]) -> float:
        """Check determiner-noun agreement"""
        score = 1.0

        determiners = [w for w in words_data if w.get('grammatical_role') == 'determiner']
        nouns = [w for w in words_data if w.get('grammatical_role') == 'noun']

        if len(determiners) > 0 and len(nouns) > 0:
            # Basic check for determiner-noun proximity
            # Real implementation would check actual agreement
            score = 0.9

        return score