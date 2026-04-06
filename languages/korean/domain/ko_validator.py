# languages/korean/domain/ko_validator.py
"""
Korean Validator - Domain Component

Validates Korean grammar analysis results and calculates confidence scores.
Checks for Korean-specific patterns: particles, verb forms, speech levels.
"""

import logging
from typing import Dict, Any, List
from .ko_config import KoConfig

logger = logging.getLogger(__name__)


class KoValidator:
    """Validates parsed Korean grammar analysis results."""

    def __init__(self, config: KoConfig):
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """Validate and enhance result with confidence scores."""
        confidence = self._calculate_confidence(result, sentence)
        result['confidence'] = confidence

        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}) for sentence: {sentence}")

        return result

    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score based on Korean-specific heuristics."""
        score = 1.0

        word_explanations = result.get('word_explanations', [])

        if len(word_explanations) == 0:
            return 0.0

        # Korean uses spaces — check word coverage
        analysis_words = [exp[0] for exp in word_explanations if len(exp) > 0]
        analysis_text = ''.join(analysis_words).replace(' ', '')
        sentence_text = sentence.replace(' ', '')

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

        # Check for valid Korean patterns
        if self._has_valid_korean_patterns(word_explanations):
            score *= 1.1
        else:
            score *= 0.8

        # Bonus for Korean-specific features
        has_particles = any(
            role in ['particle', 'topic_marker', 'subject_marker', 'object_marker',
                     'locative_particle', 'possessive_particle', 'instrumental_particle',
                     'comitative_particle', 'honorific_particle']
            for role in roles
        )
        has_verb = any(
            role in ['verb', 'auxiliary_verb', 'honorific_verb', 'humble_verb',
                     'passive_verb', 'causative_verb']
            for role in roles
        )
        has_copula = 'copula' in roles

        if has_particles:
            score *= 1.08
        if has_verb:
            score *= 1.05
        if has_copula:
            score *= 1.02

        # Check for common errors
        error_penalty = self._check_common_korean_errors(word_explanations, sentence)
        score *= (1.0 - error_penalty)

        if len(word_explanations) > 3:
            score *= 1.02

        return min(max(score, 0.0), 1.0)

    def _has_valid_korean_patterns(self, word_explanations: List[List[Any]]) -> bool:
        """Check if result has valid Korean grammar patterns."""
        roles = [item[1] for item in word_explanations if len(item) > 1]

        # Korean sentences typically end with a verb, adjective, or copula
        has_predicate = any(
            role in ['verb', 'copula', 'auxiliary_verb', 'adjective',
                     'descriptive_verb', 'honorific_verb', 'humble_verb']
            for role in roles
        )

        # Most sentences have at least one particle
        has_particle = any(
            role in ['particle', 'topic_marker', 'subject_marker', 'object_marker',
                     'locative_particle', 'possessive_particle', 'instrumental_particle',
                     'comitative_particle', 'honorific_particle']
            for role in roles
        )

        # Must have at least one content word
        has_content = any(
            role in ['noun', 'verb', 'adjective', 'pronoun']
            for role in roles
        )

        return has_content and (has_predicate or has_particle)

    def _check_common_korean_errors(self, word_explanations: List[List[Any]], sentence: str) -> float:
        """Check for common Korean grammar analysis errors."""
        penalty = 0.0

        for explanation in word_explanations:
            if len(explanation) < 4:
                continue

            role = explanation[1]
            meaning = explanation[3].lower() if isinstance(explanation[3], str) else ''

            # Particles should have function explanations
            if 'marker' in role or role == 'particle':
                if len(meaning) < 5:
                    penalty += 0.03

            # Verbs should mention conjugation or speech level
            if role == 'verb' and not any(
                v in meaning for v in ['form', 'conjugat', 'tense', 'present', 'past',
                                        'polite', 'formal', 'casual', 'plain',
                                        'speech level', 'stem']
            ):
                penalty += 0.03

        # Check if particles that should be present are missing
        common_particles = ['은', '는', '이', '가', '을', '를', '에', '에서', '의', '도']
        roles = [item[1] for item in word_explanations if len(item) > 1]

        sentence_has_particles = any(p in sentence for p in common_particles)
        analysis_has_particles = any(
            r in ['particle', 'topic_marker', 'subject_marker', 'object_marker',
                  'locative_particle', 'possessive_particle', 'instrumental_particle',
                  'comitative_particle', 'honorific_particle']
            for r in roles
        )

        if sentence_has_particles and not analysis_has_particles:
            penalty += 0.1

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

            # Check for Korean-specific features in explanations
            korean_features = ['particle', 'marker', 'speech level', 'polite', 'formal',
                              'casual', 'honorific', 'humble', 'conjugat', 'tense',
                              'subject', 'topic', 'object', 'ending']
            has_korean_specific = any(
                feature in str(meaning).lower() for feature in korean_features
            )
            if not has_korean_specific and role in ['verb', 'particle', 'auxiliary_verb',
                                                     'copula', 'topic_marker', 'subject_marker',
                                                     'object_marker']:
                quality_score *= 0.95
                issues.append(f"Word '{word}' explanation lacks Korean grammatical details")

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
            'is_acceptable': quality_score >= 0.7,
        }
