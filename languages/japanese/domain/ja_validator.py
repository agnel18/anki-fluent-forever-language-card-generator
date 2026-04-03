# languages/japanese/domain/ja_validator.py
"""
Japanese Validator - Domain Component

Validates Japanese grammar analysis results and calculates confidence scores.
Checks for Japanese-specific patterns: particles, verb forms, politeness levels.
"""

import logging
from typing import Dict, Any, List
from .ja_config import JaConfig

logger = logging.getLogger(__name__)


class JaValidator:
    """Validates parsed Japanese grammar analysis results."""

    def __init__(self, config: JaConfig):
        self.config = config

    def validate_result(self, result: Dict[str, Any], sentence: str) -> Dict[str, Any]:
        """Validate and enhance result with confidence scores."""
        confidence = self._calculate_confidence(result, sentence)
        result['confidence'] = confidence

        if confidence < 0.5:
            logger.warning(f"Low confidence ({confidence}) for sentence: {sentence}")

        return result

    def _calculate_confidence(self, result: Dict[str, Any], sentence: str) -> float:
        """Calculate confidence score based on Japanese-specific heuristics."""
        score = 1.0

        word_explanations = result.get('word_explanations', [])

        if len(word_explanations) == 0:
            return 0.0

        # Japanese has no spaces — check character coverage instead of word count
        total_chars = sum(len(exp[0]) for exp in word_explanations if len(exp) > 0)
        sentence_chars = len(sentence.replace(' ', '').replace('　', ''))

        if sentence_chars > 0:
            coverage = total_chars / sentence_chars
            if coverage < 0.5:
                score *= 0.6
            elif coverage < 0.8:
                score *= 0.8
            elif coverage > 1.3:
                # Over-segmentation
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

        # Check for valid Japanese patterns
        if self._has_valid_japanese_patterns(word_explanations):
            score *= 1.1
        else:
            score *= 0.8

        # Bonus for Japanese-specific features
        has_particles = any(
            'particle' in role for role in roles
        )
        has_verb = any(
            role in ['verb', 'auxiliary_verb', 'honorific_verb', 'humble_verb',
                     'potential_verb', 'passive_verb', 'causative_verb', 'te_form']
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
        error_penalty = self._check_common_japanese_errors(word_explanations, sentence)
        score *= (1.0 - error_penalty)

        if len(word_explanations) > 3:
            score *= 1.02

        return min(max(score, 0.0), 1.0)

    def _has_valid_japanese_patterns(self, word_explanations: List[List[Any]]) -> bool:
        """Check if result has valid Japanese grammar patterns."""
        roles = [item[1] for item in word_explanations if len(item) > 1]

        # Japanese sentences typically end with a verb or copula
        has_verb_or_copula = any(
            role in ['verb', 'copula', 'auxiliary_verb', 'i_adjective', 'na_adjective',
                     'honorific_verb', 'humble_verb', 'te_form']
            for role in roles
        )

        # Most sentences have at least one particle
        has_particle = any('particle' in role for role in roles)

        # Must have at least one content word
        has_content = any(
            role in ['noun', 'verb', 'i_adjective', 'na_adjective', 'pronoun']
            for role in roles
        )

        return has_content and (has_verb_or_copula or has_particle)

    def _check_common_japanese_errors(self, word_explanations: List[List[Any]], sentence: str) -> float:
        """Check for common Japanese grammar analysis errors."""
        penalty = 0.0

        for explanation in word_explanations:
            if len(explanation) < 4:
                continue

            role = explanation[1]
            meaning = explanation[3].lower() if isinstance(explanation[3], str) else ''

            # Particles should have function explanations
            if 'particle' in role and len(meaning) < 5:
                penalty += 0.03

            # Verbs should mention conjugation or form
            if role == 'verb' and not any(
                v in meaning for v in ['form', 'conjugat', 'tense', 'plain', 'polite',
                                        'masu', 'dictionary', 'godan', 'ichidan']
            ):
                penalty += 0.03

        # Check if particles that should be present are missing
        common_particles = ['は', 'が', 'を', 'に', 'で', 'の', 'と', 'も', 'か']
        roles = [item[1] for item in word_explanations if len(item) > 1]
        words = [item[0] for item in word_explanations if len(item) > 0]

        # If sentence contains common particles but none were identified
        sentence_has_particles = any(p in sentence for p in common_particles)
        analysis_has_particles = any('particle' in r for r in roles)

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

            # Check for Japanese-specific features in explanations
            japanese_features = ['particle', 'verb form', 'conjugat', 'polite', 'plain',
                                'kanji', 'hiragana', 'katakana', 'reading',
                                'counter', 'honorific', 'humble']
            has_japanese_specific = any(
                feature in str(meaning).lower() for feature in japanese_features
            )
            if not has_japanese_specific and role in ['verb', 'particle', 'auxiliary_verb',
                                                       'copula', 'counter']:
                quality_score *= 0.95
                issues.append(f"Word '{word}' explanation lacks Japanese grammatical details")

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
            'recommendations': self._generate_quality_recommendations(issues)
        }

    def _generate_quality_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on identified quality issues."""
        recommendations = []

        if any('brief' in issue.lower() for issue in issues):
            recommendations.append("Expand explanations to cover particle functions and verb conjugation details")

        if any('japanese' in issue.lower() for issue in issues):
            recommendations.append("Include Japanese-specific features like particle types, verb groups, and politeness levels")

        if any('missing' in issue.lower() for issue in issues):
            recommendations.append("Ensure all morphemes have complete analysis including role, reading, and meaning")

        if not recommendations:
            recommendations.append("Analysis quality is good — consider adding more verb conjugation and particle detail")

        return recommendations
