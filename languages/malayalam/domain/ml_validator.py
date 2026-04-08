# languages/malayalam/domain/ml_validator.py
"""
Malayalam Validator - Domain Component

Validates Malayalam grammar analysis results and calculates confidence scores.
Checks for Malayalam-specific patterns: case markers, verb forms, postpositions.
"""

import logging
from typing import Dict, Any, List
from .ml_config import MlConfig

logger = logging.getLogger(__name__)


class MlValidator:
    """Validates parsed Malayalam grammar analysis results."""

    def __init__(self, config: MlConfig):
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """Validate and enhance result with confidence scores."""
        confidence = self._calculate_confidence(result, sentence)
        result['confidence'] = confidence

        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}) for sentence: {sentence}")

        return result

    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score based on Malayalam-specific heuristics."""
        score = 1.0

        word_explanations = result.get('word_explanations', [])

        if len(word_explanations) == 0:
            return 0.0

        # Check word coverage
        analyzed_text = ''.join(exp[0] for exp in word_explanations if len(exp) > 0)
        # Remove spaces and punctuation from sentence for comparison
        clean_sentence = sentence.replace(' ', '').replace('।', '').replace('.', '').replace(',', '').replace('?', '').replace('!', '')
        clean_analyzed = analyzed_text.replace(' ', '')

        if len(clean_sentence) > 0:
            coverage = len(clean_analyzed) / len(clean_sentence)
            if coverage < 0.5:
                score *= 0.6
            elif coverage < 0.8:
                score *= 0.8
            elif coverage > 1.3:
                score *= 0.85

        # Check role distribution
        roles = [item[1] for item in word_explanations if len(item) > 1]
        if not roles:
            return 0.0

        other_count = roles.count('other')
        if len(roles) > 0 and other_count / len(roles) > 0.4:
            score *= 0.6
        elif len(roles) > 0 and other_count / len(roles) > 0.2:
            score *= 0.8

        # Check for valid Malayalam patterns
        if self._has_valid_malayalam_patterns(word_explanations):
            score *= 1.1
        else:
            score *= 0.8

        # Bonus for Malayalam-specific features
        has_verb = any(
            role in ['verb', 'auxiliary_verb', 'causative_verb',
                     'passive_verb', 'verbal_participle', 'copula']
            for role in roles
        )
        has_noun = 'noun' in roles
        has_postposition = 'postposition' in roles
        has_case_marker = 'case_marker' in roles

        if has_verb:
            score *= 1.05
        if has_noun:
            score *= 1.05
        if has_postposition:
            score *= 1.03
        if has_case_marker:
            score *= 1.03

        # Check for common errors
        error_penalty = self._check_common_malayalam_errors(word_explanations, sentence)
        score *= (1.0 - error_penalty)

        if len(word_explanations) > 3:
            score *= 1.02

        return min(max(score, 0.0), 1.0)

    def _has_valid_malayalam_patterns(self, word_explanations: List[List[Any]]) -> bool:
        """Check if result has valid Malayalam grammar patterns."""
        roles = [item[1] for item in word_explanations if len(item) > 1]

        # Malayalam sentences typically end with a verb (SOV)
        has_verb = any(
            role in ['verb', 'auxiliary_verb', 'copula', 'verbal_participle',
                     'causative_verb', 'passive_verb']
            for role in roles
        )

        # Must have at least one content word
        has_content = any(
            role in ['noun', 'verb', 'adjective', 'pronoun']
            for role in roles
        )

        return has_content and has_verb

    def _check_common_malayalam_errors(self, word_explanations: List[List[Any]], sentence: str) -> float:
        """Check for common Malayalam grammar analysis errors."""
        penalty = 0.0

        for explanation in word_explanations:
            if len(explanation) < 4:
                continue

            role = explanation[1]
            meaning = explanation[3].lower() if isinstance(explanation[3], str) else ''

            # Postpositions should have function explanations
            if role == 'postposition' and len(meaning) < 5:
                penalty += 0.03

            # Verbs should mention tense or form
            if role == 'verb' and not any(
                v in meaning for v in ['tense', 'past', 'present', 'future',
                                        'form', 'conjugat', 'participle', 'imperative',
                                        'infinitive', 'negative']
            ):
                penalty += 0.03

        # Check if verb-final pattern is present (SOV)
        roles = [item[1] for item in word_explanations if len(item) > 1]
        verb_roles = {'verb', 'auxiliary_verb', 'copula', 'causative_verb', 'passive_verb'}

        if roles and roles[-1] not in verb_roles:
            # Not ending with verb — less typical for Malayalam
            # But don't penalize too heavily (questions, exclamations)
            penalty += 0.02

        return min(penalty, 0.3)

    def validate_explanation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality and comprehensiveness of explanations."""
        quality_score = 1.0
        issues = []

        word_explanations = result.get('word_explanations', [])
        for i, explanation in enumerate(word_explanations):
            if len(explanation) < 4:
                quality_score *= 0.8
                issues.append(f"Word explanation {i} missing meaning component")
                continue

            word, role, color, meaning = explanation[:4]

            if len(str(meaning).strip()) < 5:
                quality_score *= 0.9
                issues.append(f"Word '{word}' has too brief explanation")

            # Check for Malayalam-specific features in explanations
            malayalam_features = ['case', 'suffix', 'agglut', 'postposition',
                                  'tense', 'aspect', 'mood', 'participle',
                                  'sandhi', 'honorific', 'nominative', 'accusative',
                                  'dative', 'genitive', 'locative', 'instrumental']
            has_malayalam_specific = any(
                feature in str(meaning).lower() for feature in malayalam_features
            )
            if not has_malayalam_specific and role in ['verb', 'case_marker',
                                                        'postposition', 'auxiliary_verb',
                                                        'verbal_participle']:
                quality_score *= 0.95
                issues.append(f"Word '{word}' explanation lacks Malayalam grammatical details")

        explanations = result.get('explanations', {})
        if not explanations:
            quality_score *= 0.7
            issues.append("Missing overall explanations section")
        else:
            overall = explanations.get('overall_structure', '')
            if len(str(overall).strip()) < 20:
                quality_score *= 0.9
                issues.append("Overall structure explanation too brief")

        quality_score = min(max(quality_score, 0.0), 1.0)

        return {
            'quality_score': quality_score,
            'issues': issues,
            'total_words_checked': len(word_explanations)
        }
