# languages/hungarian/domain/hu_validator.py
"""
Hungarian Validator - Domain Component

Validates Hungarian grammar analysis results and calculates confidence scores.
Checks for Hungarian-specific patterns: case markers, conjugation types, preverbs, postpositions.
"""

import logging
from typing import Dict, Any, List
from .hu_config import HuConfig

logger = logging.getLogger(__name__)


class HuValidator:
    """Validates parsed Hungarian grammar analysis results."""

    def __init__(self, config: HuConfig):
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """Validate and enhance result with confidence scores."""
        confidence = self._calculate_confidence(result, sentence)
        result['confidence'] = confidence

        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}) for sentence: {sentence}")

        return result

    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score based on Hungarian-specific heuristics."""
        score = 1.0

        word_explanations = result.get('word_explanations', [])

        if len(word_explanations) == 0:
            return 0.0

        # Hungarian uses spaces — check word coverage
        analysis_words = [exp[0] for exp in word_explanations if len(exp) > 0]
        analysis_text = ''.join(analysis_words).replace(' ', '')
        sentence_text = sentence.replace(' ', '').rstrip('.!?;:,')

        if len(sentence_text) > 0:
            coverage = len(analysis_text) / len(sentence_text)
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

        # Check for valid Hungarian patterns
        if self._has_valid_hungarian_patterns(word_explanations):
            score *= 1.1
        else:
            score *= 0.8

        # Bonus for Hungarian-specific features
        has_case_marker = any(
            role in ['accusative', 'dative', 'instrumental', 'causal_final',
                     'translative', 'inessive', 'superessive', 'adessive',
                     'sublative', 'delative', 'elative', 'illative',
                     'allative', 'ablative', 'terminative', 'essive_formal',
                     'distributive']
            for role in roles
        )
        has_verb = any(
            role in ['verb', 'definite_conjugation', 'indefinite_conjugation',
                     'auxiliary_verb', 'causative_verb', 'potential_verb']
            for role in roles
        )
        has_article = any(
            role in ['definite_article', 'indefinite_article']
            for role in roles
        )

        if has_case_marker:
            score *= 1.05
        if has_verb:
            score *= 1.05
        if has_article:
            score *= 1.02

        # Check for common errors
        error_penalty = self._check_common_hungarian_errors(word_explanations, sentence)
        score *= (1.0 - error_penalty)

        if len(word_explanations) > 3:
            score *= 1.02

        return min(max(score, 0.0), 1.0)

    def _has_valid_hungarian_patterns(self, word_explanations: List[List[Any]]) -> bool:
        """Check if result has valid Hungarian grammar patterns."""
        roles = [item[1] for item in word_explanations if len(item) > 1]

        # Hungarian sentences typically have a verb (conjugated)
        has_predicate = any(
            role in ['verb', 'definite_conjugation', 'indefinite_conjugation',
                     'copula', 'auxiliary_verb']
            for role in roles
        )

        # Must have at least one content word
        has_content = any(
            role in ['noun', 'verb', 'adjective', 'pronoun',
                     'definite_conjugation', 'indefinite_conjugation']
            for role in roles
        )

        return has_content and has_predicate

    def _check_common_hungarian_errors(self, word_explanations: List[List[Any]], sentence: str) -> float:
        """Check for common Hungarian grammar analysis errors."""
        penalty = 0.0

        for explanation in word_explanations:
            if len(explanation) < 4:
                continue

            role = explanation[1]
            meaning = explanation[3].lower() if isinstance(explanation[3], str) else ''

            # Case markers should have function explanations
            case_roles = ['accusative', 'dative', 'instrumental', 'inessive',
                         'superessive', 'sublative', 'elative', 'illative',
                         'allative', 'ablative']
            if role in case_roles and len(meaning) < 5:
                penalty += 0.03

            # Verbs should mention conjugation type
            if role in ['verb', 'definite_conjugation', 'indefinite_conjugation']:
                if not any(v in meaning for v in ['conjugat', 'definite', 'indefinite',
                                                   'tense', 'present', 'past',
                                                   'person', 'singular', 'plural']):
                    penalty += 0.03

        # Check if definite article is present but no article role detected
        roles = [item[1] for item in word_explanations if len(item) > 1]
        words_lower = [item[0].lower() for item in word_explanations if len(item) > 0]

        sentence_has_article = 'a ' in sentence.lower() or sentence.lower().startswith('a ') or 'az ' in sentence.lower()
        analysis_has_article = any(
            r in ['definite_article', 'indefinite_article']
            for r in roles
        )

        if sentence_has_article and not analysis_has_article:
            penalty += 0.08

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

            # Check for Hungarian-specific features in explanations
            hungarian_features = ['case', 'accusative', 'dative', 'instrumental',
                                  'inessive', 'conjugat', 'definite', 'indefinite',
                                  'preverb', 'postposition', 'possessive',
                                  'vowel harmony', 'suffix', 'tense', 'mood']
            has_hungarian_specific = any(
                feature in str(meaning).lower() for feature in hungarian_features
            )
            if not has_hungarian_specific and role in ['verb', 'definite_conjugation',
                                                        'indefinite_conjugation',
                                                        'accusative', 'dative',
                                                        'instrumental', 'inessive',
                                                        'postposition', 'preverb']:
                quality_score *= 0.95
                issues.append(f"Word '{word}' explanation lacks Hungarian grammatical details")

        return {
            'quality_score': min(max(quality_score, 0.0), 1.0),
            'issues': issues,
            'total_words': len(word_explanations)
        }
