# languages/french/domain/fr_validator.py
"""
French Validator - Domain Component

FRENCH VALIDATION:
This component demonstrates how to validate French grammar analysis results and calculate confidence scores.
It ensures result quality and provides confidence metrics for decision-making.

RESPONSIBILITIES:
1. Validate parsed grammar analysis results
2. Calculate confidence scores based on multiple heuristics
3. Check for valid French grammar patterns
4. Apply quality thresholds and warnings
5. Enhance results with validation metadata

VALIDATION HEURISTICS:
- Word count matching: Results should match sentence breakdown
- Role distribution: Check for appropriate French grammatical elements
- Pattern recognition: Validate gender agreement, verb conjugations, preposition usage
- Confidence scoring: Multi-factor quality assessment
- Threshold application: Warn on low-confidence results

USAGE FOR FRENCH:
1. Copy validation structure and heuristics
2. Implement French-specific pattern checks (gender agreement, conjugations, pronouns)
3. Adjust confidence scoring weights for French grammar
4. Define appropriate quality thresholds
5. Test validation catches common AI errors in French analysis

INTEGRATION:
- Called after response parsing in main analyzer
- Results include confidence scores for UI display
- Low confidence triggers warnings/logging
- Validation doesn't block processing (graceful degradation)
"""

import logging
from typing import Dict, Any, List
from .fr_config import FrConfig

logger = logging.getLogger(__name__)

class FrValidator:
    """
    Validates parsed French grammar analysis results.

    FRENCH VALIDATION APPROACH:
    - Multi-heuristic scoring: Combine multiple quality indicators
    - Language-specific checks: French grammar pattern validation
    - Confidence thresholds: Clear quality boundaries
    - Non-blocking: Validation enhances but doesn't prevent results
    - Logging: Detailed feedback for debugging and monitoring

    VALIDATION PHILOSOPHY:
    - Trust but verify: AI results are good but need validation
    - Graceful degradation: Poor results still better than no results
    - Continuous improvement: Validation guides AI prompt refinement
    - User transparency: Confidence scores inform user trust
    """

    def __init__(self, config: FrConfig):
        """
        Initialize validator with configuration.

        CONFIGURATION DEPENDENCY:
        1. Access to grammatical roles and patterns
        2. French-specific validation rules
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
        """Calculate confidence score based on various French-specific heuristics."""
        score = 1.0

        # Check if words match sentence breakdown
        word_explanations = result.get('word_explanations', [])
        sentence_words = sentence.split()

        if len(word_explanations) == 0:
            return 0.0

        # Check word count alignment (allowing for some flexibility)
        word_count_diff = abs(len(word_explanations) - len(sentence_words))
        if word_count_diff > 2:
            score *= 0.7
        elif word_count_diff > 0:
            score *= 0.9

        # Check role distribution
        roles = [item[1] for item in word_explanations if len(item) > 1]
        if not roles:
            return 0.0

        # Penalize too many 'other' roles
        other_count = roles.count('other')
        if other_count / len(roles) > 0.4:
            score *= 0.6
        elif other_count / len(roles) > 0.2:
            score *= 0.8

        # Check for valid French patterns
        if self._has_valid_french_patterns(word_explanations):
            score *= 1.1
        else:
            score *= 0.8

        # Bonus for French-specific grammatical features
        has_agreement = self._check_agreement_patterns(word_explanations)
        has_conjugation = any(role in ['verb', 'auxiliary_verb', 'modal_verb'] for role in roles)
        has_pronouns = any('pronoun' in role for role in roles)
        has_determiners = 'determiner' in roles
        has_prepositions = 'preposition' in roles

        if has_agreement:
            score *= 1.08
        if has_conjugation:
            score *= 1.05
        if has_pronouns and has_determiners:
            score *= 1.03
        if has_prepositions:
            score *= 1.02

        # Check for common French grammar errors
        error_penalty = self._check_common_french_errors(word_explanations, sentence)
        score *= (1.0 - error_penalty)

        # Length-based adjustment (longer analyses tend to be more detailed)
        if len(word_explanations) > 5:
            score *= 1.02

        return min(max(score, 0.0), 1.0)

    def _has_valid_french_patterns(self, word_explanations: List[List[str]]) -> bool:
        """Check if result has valid French grammar patterns."""
        roles = [item[1] for item in word_explanations if len(item) > 1]

        # Must have at least one noun/pronoun (basic requirement)
        has_noun = any(role in ['noun', 'pronoun', 'personal_pronoun'] for role in roles)

        # Should have some verbs (most sentences do)
        has_verb = any('verb' in role for role in roles)

        # French-specific: check for determiners (very common)
        has_determiner = 'determiner' in roles

        # Basic validity: has content words
        return has_noun and (has_verb or has_determiner)

    def _check_agreement_patterns(self, word_explanations: List[List[str]]) -> bool:
        """Check for gender/number agreement patterns in the analysis."""
        # Simple check: look for determiners followed by nouns with potential agreement
        agreement_found = False

        for i, explanation in enumerate(word_explanations):
            if len(explanation) < 4:
                continue

            role = explanation[1]
            meaning = explanation[3].lower()

            # Check if explanation mentions gender agreement
            if 'gender' in meaning or 'masculine' in meaning or 'feminine' in meaning:
                agreement_found = True
                break

            # Check for determiner-noun agreement patterns
            if role == 'determiner' and i + 1 < len(word_explanations):
                next_role = word_explanations[i + 1][1] if len(word_explanations[i + 1]) > 1 else ''
                if next_role in ['noun', 'adjective']:
                    agreement_found = True
                    break

        return agreement_found

    def _check_common_french_errors(self, word_explanations: List[List[str]], sentence: str) -> float:
        """Check for common French grammar analysis errors and return penalty score (0.0-1.0)."""
        penalty = 0.0

        # Check for missing gender information on nouns/adjectives
        for explanation in word_explanations:
            if len(explanation) < 4:
                continue

            role = explanation[1]
            meaning = explanation[3].lower()

            # Nouns and adjectives should mention gender in French
            if role in ['noun', 'adjective'] and not any(gender in meaning for gender in ['masculine', 'feminine', 'neutral']):
                penalty += 0.05

            # Verbs should mention person/tense information
            if role == 'verb' and not any(verb_info in meaning for verb_info in ['person', 'tense', 'present', 'past', 'future']):
                penalty += 0.03

        # Check for pronoun agreement issues
        pronoun_noun_pairs = []
        for i, explanation in enumerate(word_explanations):
            if len(explanation) < 2:
                continue
            role = explanation[1]
            if 'pronoun' in role:
                # Look for nearby nouns
                for j in range(max(0, i-3), min(len(word_explanations), i+4)):
                    if j != i and len(word_explanations[j]) > 1:
                        other_role = word_explanations[j][1]
                        if other_role in ['noun', 'adjective']:
                            pronoun_noun_pairs.append((i, j))

        # Penalize if no pronoun-noun relationships found in complex sentences
        if len(sentence.split()) > 4 and len(pronoun_noun_pairs) == 0:
            pronouns = [exp[1] for exp in word_explanations if len(exp) > 1 and 'pronoun' in exp[1]]
            nouns = [exp[1] for exp in word_explanations if len(exp) > 1 and exp[1] in ['noun', 'adjective']]
            if pronouns and nouns:
                penalty += 0.02

        # Check for preposition usage patterns
        preposition_count = sum(1 for exp in word_explanations if len(exp) > 1 and exp[1] == 'preposition')
        if preposition_count > len(word_explanations) * 0.3:  # Too many prepositions
            penalty += 0.05

        return min(penalty, 0.3)  # Cap penalty at 30%

    def validate_explanation_quality(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality and comprehensiveness of explanations in the analysis result."""
        quality_score = 1.0
        issues = []

        # Check word explanations for comprehensiveness
        word_explanations = result.get('word_explanations', [])
        for i, explanation in enumerate(word_explanations):
            if len(explanation) < 4:
                quality_score *= 0.8
                issues.append(f"Word explanation {i} missing meaning component")
                continue

            word, role, color, meaning = explanation[:4]

            # Check if meaning is detailed enough (not just brief)
            if len(meaning.strip()) < 10:
                quality_score *= 0.9
                issues.append(f"Word '{word}' has too brief explanation: '{meaning}'")

            # Check for French-specific features
            french_features = ['gender', 'masculine', 'feminine', 'person', 'tense', 'mood',
                             'agreement', 'conjugation', 'plural', 'singular']
            has_french_specific = any(feature in meaning.lower() for feature in french_features)
            if not has_french_specific and role in ['noun', 'adjective', 'verb', 'pronoun', 'determiner']:
                quality_score *= 0.95
                issues.append(f"Word '{word}' explanation lacks French grammatical details")

        # Check overall explanations section
        explanations = result.get('explanations', {})
        if not explanations:
            quality_score *= 0.7
            issues.append("Missing overall explanations section")
        else:
            # Check for comprehensive structural analysis
            overall_structure = explanations.get('overall_structure', '')
            if len(overall_structure.strip()) < 20:
                quality_score *= 0.9
                issues.append("Overall structure explanation too brief")

            # Check for agreement patterns explanation
            agreement_patterns = explanations.get('agreement_patterns', '')
            if len(agreement_patterns.strip()) < 15:
                quality_score *= 0.9
                issues.append("Agreement patterns explanation too brief")

            # Check for key features explanation
            key_features = explanations.get('key_features', '')
            if len(key_features.strip()) < 15:
                quality_score *= 0.9
                issues.append("Key features explanation too brief")

            # Check for French-specific content
            french_grammar = ['gender', 'agreement', 'conjugation', 'verb', 'pronoun', 'determiner']
            has_french_specific = any(feature in (overall_structure + agreement_patterns + key_features).lower()
                                    for feature in french_grammar)
            if not has_french_specific:
                quality_score *= 0.9
                issues.append("Explanations lack French-specific grammatical features")

        # Ensure quality score is within bounds
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
            recommendations.append("Expand explanations to provide more detailed analysis of word functions and relationships")

        if any('french' in issue.lower() for issue in issues):
            recommendations.append("Include French-specific grammatical features like gender, agreement, conjugation, and verb forms")

        if any('relationship' in issue.lower() for issue in issues):
            recommendations.append("Explain how words relate to each other through agreement and grammatical dependencies")

        if any('missing' in issue.lower() for issue in issues):
            recommendations.append("Ensure all words have complete grammatical analysis including role, color, and detailed meaning")

        if any('agreement' in issue.lower() for issue in issues):
            recommendations.append("Highlight gender and number agreement patterns between determiners, adjectives, and nouns")

        if not recommendations:
            recommendations.append("Analysis quality is good - consider adding more advanced French linguistic details")

        return recommendations