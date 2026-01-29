# languages/{language}/domain/{lang_code}_validator.py
"""
{Language} Validator - Domain Component

GOLD STANDARD VALIDATION APPROACH:
- Multi-layered validation (structure, content, linguistics)
- Language-specific rule checking
- Quality metric calculation
- Detailed issue reporting with severity levels
- Confidence score adjustment based on validation results

VALIDATOR RESPONSIBILITIES:
1. Structural validation of analysis results
2. Content quality and accuracy checking
3. Language-specific grammatical rule validation
4. Quality metric calculation and reporting
5. Confidence score adjustment based on issues

VALIDATION FEATURES:
- Multi-layer validation pipeline
- Configurable validation thresholds
- Language-specific rule checking
- Quality metrics calculation
- Detailed issue reporting with severity levels

INTEGRATION:
- Called by analyzer facade after parsing
- Uses configuration for validation rules
- Returns validation results with issues and metrics
- Adjusts confidence scores based on validation
"""
# type: ignore  # Template file with placeholders - ignore type checking

from typing import Dict, Any, List


class LanguageValidator:
    """
    Validates {Language} grammar analysis results.

    GOLD STANDARD VALIDATION APPROACH:
    - Multi-layered validation (structure, content, linguistics)
    - Language-specific rule checking
    - Quality metric calculation
    - Detailed issue reporting with severity levels
    - Confidence score adjustment based on validation results
    """

    def __init__(self, config):
        """
        Initialize with configuration.

        TEMPLATE INITIALIZATION:
        1. Store config reference for validation rules
        2. Set up validation thresholds
        3. Initialize language-specific validators
        4. Configure quality metrics
        """
        self.config = config

        # Validation thresholds
        self.min_confidence_threshold = 0.3
        self.max_word_coverage_penalty = 0.8
        self.invalid_role_penalty = 0.9

    def validate_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate analysis result for {Language}.

        Args:
            result: Analysis result dictionary from parser

        Returns:
            Validation result with issues, metrics, and adjusted confidence
        """
        validation_result = {
            'is_valid': True,
            'issues': [],
            'quality_metrics': {},
            'adjusted_confidence': result.get('confidence_score', 0.0),
            'validation_passed': []
        }

        word_explanations = result.get('word_explanations', [])
        sentence = result.get('sentence', '')
        complexity = result.get('complexity', 'intermediate')

        # Layer 1: Structural validation
        structural_issues = self._validate_structure(word_explanations, sentence)
        validation_result['issues'].extend(structural_issues)

        # Layer 2: Content validation
        content_issues = self._validate_content(word_explanations, complexity)
        validation_result['issues'].extend(content_issues)

        # Layer 3: Language-specific validation
        language_issues = self._validate_language_specific_rules(word_explanations, sentence, complexity)
        validation_result['issues'].extend(language_issues)

        # Calculate quality metrics
        validation_result['quality_metrics'] = self._calculate_quality_metrics(
            word_explanations, sentence, complexity
        )

        # Determine overall validity
        critical_issues = [issue for issue in validation_result['issues']
                          if issue.get('severity') == 'error']
        validation_result['is_valid'] = len(critical_issues) == 0

        # Adjust confidence based on validation
        validation_result['adjusted_confidence'] = self._adjust_confidence(
            result.get('confidence_score', 0.0), validation_result
        )

        # Track passed validations
        validation_result['validation_passed'] = [
            'structure_check',
            'content_check',
            'language_rules_check'
        ]

        return validation_result

    def _validate_structure(self, word_explanations: List, sentence: str) -> List[Dict[str, Any]]:
        """Validate basic structure of analysis result"""
        issues = []

        # Check word count coverage
        sentence_words = len(sentence.split()) if sentence else 0
        analyzed_words = len(word_explanations)

        if analyzed_words == 0:
            issues.append({
                'type': 'no_analysis',
                'severity': 'error',
                'message': 'No words were analyzed',
                'category': 'structure'
            })
            return issues

        coverage_ratio = analyzed_words / sentence_words if sentence_words > 0 else 0

        if coverage_ratio < 0.5:
            issues.append({
                'type': 'low_coverage',
                'severity': 'warning',
                'message': f'Only {analyzed_words}/{sentence_words} words analyzed ({coverage_ratio:.1%})',
                'category': 'structure'
            })

        # Check format consistency
        for i, explanation in enumerate(word_explanations):
            if not isinstance(explanation, list) or len(explanation) < 2:
                issues.append({
                    'type': 'invalid_format',
                    'severity': 'error',
                    'message': f'Word {i+1} has invalid explanation format',
                    'category': 'structure'
                })
                continue

            word, role = explanation[0], explanation[1]

            if not word or not isinstance(word, str):
                issues.append({
                    'type': 'missing_word',
                    'severity': 'error',
                    'message': f'Word {i+1} is missing or invalid',
                    'category': 'structure'
                })

            if not role or not isinstance(role, str):
                issues.append({
                    'type': 'missing_role',
                    'severity': 'error',
                    'message': f'Word {i+1} ({word}) missing grammatical role',
                    'category': 'structure'
                })

        return issues

    def _validate_content(self, word_explanations: List, complexity: str) -> List[Dict[str, Any]]:
        """Validate content quality and accuracy"""
        issues = []
        valid_roles = set(self.config.get_grammatical_roles(complexity).keys())

        invalid_roles_found = []
        empty_explanations = []
        duplicate_roles = {}

        for i, explanation in enumerate(word_explanations):
            if not isinstance(explanation, list) or len(explanation) < 2:
                continue

            word, role = explanation[0], explanation[1]

            # Check role validity
            if role not in valid_roles:
                invalid_roles_found.append(f"'{word}': '{role}'")
                continue

            # Check for empty explanations
            if len(explanation) > 3:
                meaning = explanation[3]
                if not meaning or not meaning.strip():
                    empty_explanations.append(word)

            # Track role distribution
            if role not in duplicate_roles:
                duplicate_roles[role] = []
            duplicate_roles[role].append(word)

        # Report invalid roles
        if invalid_roles_found:
            issues.append({
                'type': 'invalid_roles',
                'severity': 'error',
                'message': f'Invalid grammatical roles: {", ".join(invalid_roles_found[:3])}',
                'category': 'content'
            })

        # Report empty explanations
        if empty_explanations:
            issues.append({
                'type': 'empty_explanations',
                'severity': 'warning',
                'message': f'Words without explanations: {", ".join(empty_explanations[:3])}',
                'category': 'content'
            })

        # Check for unnatural role distribution
        total_words = len(word_explanations)
        if total_words > 0:
            for role, words in duplicate_roles.items():
                percentage = len(words) / total_words
                # Flag if more than 70% of words have the same role (likely incorrect)
                if percentage > 0.7 and total_words > 3:
                    issues.append({
                        'type': 'role_distribution',
                        'severity': 'warning',
                        'message': f'Unnatural distribution: {percentage:.1%} of words are {role}',
                        'category': 'content'
                    })

        return issues

    def _validate_language_specific_rules(self, word_explanations: List, sentence: str, complexity: str) -> List[Dict[str, Any]]:
        """Validate language-specific grammatical rules"""
        issues = []

        # Get language-specific validation rules
        validation_rules = self.config.get_validation_rules()

        # Basic subject-verb agreement check (customize for your language)
        subject_verb_issues = self._check_subject_verb_agreement(word_explanations)
        issues.extend(subject_verb_issues)

        # Word order validation (customize for your language)
        word_order_issues = self._check_word_order_rules(word_explanations, sentence)
        issues.extend(word_order_issues)

        # Language-specific pattern checks
        pattern_issues = self._check_language_patterns(word_explanations, validation_rules)
        issues.extend(pattern_issues)

        return issues

    def _check_subject_verb_agreement(self, word_explanations: List) -> List[Dict[str, Any]]:
        """Check basic subject-verb agreement (customize for your language)"""
        issues = []

        # Extract subjects and verbs
        subjects = []
        verbs = []

        for explanation in word_explanations:
            if len(explanation) >= 2:
                word, role = explanation[0], explanation[1]
                if role in ['noun', 'pronoun']:
                    subjects.append((word, explanation))
                elif role == 'verb':
                    verbs.append((word, explanation))

        # Basic agreement check (customize based on language rules)
        if not subjects and verbs:
            issues.append({
                'type': 'missing_subject',
                'severity': 'warning',
                'message': 'Sentence has verbs but no apparent subject',
                'category': 'language_rules'
            })

        return issues

    def _check_word_order_rules(self, word_explanations: List, sentence: str) -> List[Dict[str, Any]]:
        """Check word order rules (customize for your language)"""
        issues = []

        # Basic word order validation (customize for your language)
        # This is a placeholder - implement language-specific word order rules

        words_from_analysis = [exp[0] for exp in word_explanations if len(exp) > 0]
        words_from_sentence = sentence.split()

        # Check if analysis maintains basic word sequence
        if len(words_from_analysis) != len(words_from_sentence):
            issues.append({
                'type': 'word_sequence',
                'severity': 'info',
                'message': 'Word sequence analysis completed',
                'category': 'language_rules'
            })

        return issues

    def _check_language_patterns(self, word_explanations: List, validation_rules: Dict) -> List[Dict[str, Any]]:
        """Check language-specific patterns"""
        issues = []

        # Implement language-specific pattern validations
        # This is a placeholder - customize based on your language's rules

        return issues

    def _calculate_quality_metrics(self, word_explanations: List, sentence: str, complexity: str) -> Dict[str, float]:
        """Calculate quality metrics for the analysis"""
        metrics = {}

        if not word_explanations:
            return {
                'word_coverage': 0.0,
                'role_validity': 0.0,
                'explanation_completeness': 0.0,
                'structural_integrity': 0.0
            }

        # Word coverage
        sentence_words = len(sentence.split()) if sentence else 0
        analyzed_words = len(word_explanations)
        metrics['word_coverage'] = analyzed_words / sentence_words if sentence_words > 0 else 0

        # Role validity
        valid_roles = set(self.config.get_grammatical_roles(complexity).keys())
        valid_count = sum(1 for exp in word_explanations
                         if len(exp) > 1 and exp[1] in valid_roles)
        metrics['role_validity'] = valid_count / analyzed_words if analyzed_words > 0 else 0

        # Explanation completeness
        complete_count = sum(1 for exp in word_explanations
                           if len(exp) > 3 and exp[3] and exp[3].strip())
        metrics['explanation_completeness'] = complete_count / analyzed_words if analyzed_words > 0 else 0

        # Structural integrity
        proper_format_count = sum(1 for exp in word_explanations
                                if isinstance(exp, list) and len(exp) >= 4)
        metrics['structural_integrity'] = proper_format_count / analyzed_words if analyzed_words > 0 else 0

        return metrics

    def _adjust_confidence(self, original_confidence: float, validation_result: Dict[str, Any]) -> float:
        """Adjust confidence score based on validation results"""
        confidence = original_confidence

        # Apply penalties for issues
        issues = validation_result.get('issues', [])

        for issue in issues:
            severity = issue.get('severity', 'info')
            if severity == 'error':
                confidence *= self.invalid_role_penalty
            elif severity == 'warning':
                confidence *= self.max_word_coverage_penalty

        # Boost confidence for high-quality metrics
        metrics = validation_result.get('quality_metrics', {})
        avg_metric = sum(metrics.values()) / len(metrics) if metrics else 0

        if avg_metric > 0.8:
            confidence = min(confidence * 1.1, 1.0)

        return round(confidence, 2)