# languages/chinese_traditional/domain/zh_tw_validator.py
"""
Validation logic for Chinese Traditional grammar analysis results.
Ensures analysis quality and linguistic accuracy for Chinese Traditional.
"""

import re
import logging
from typing import Dict, List, Any, Optional

from .zh_tw_config import ZhTwConfig

logger = logging.getLogger(__name__)


class ZhTwValidator:
    """
    Validates Chinese Traditional grammar analysis results.

    Performs quality checks on:
    - Grammatical role assignments
    - Word segmentation accuracy
    - Traditional character usage
    - Sentence structure coherence
    - Measure word correctness
    - Aspect particle usage
    """

    def __init__(self, config: ZhTwConfig):
        self.config = config
        self.validation_rules = config.get_validation_rules()

    def validate_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive validation on analysis result.

        Args:
            analysis_result: The analysis result to validate

        Returns:
            Validation report with issues and recommendations
        """

        validation_report = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'quality_score': 100
        }

        # Run all validation checks
        checks = [
            self._validate_basic_structure,
            self._validate_grammatical_roles,
            self._validate_word_segmentation,
            self._validate_traditional_characters,
            self._validate_measure_words,
            self._validate_aspect_particles,
            self._validate_sentence_coherence,
            self._validate_meanings_completeness
        ]

        for check in checks:
            try:
                check_result = check(analysis_result)
                if check_result:
                    validation_report['issues'].extend(check_result.get('issues', []))
                    validation_report['warnings'].extend(check_result.get('warnings', []))
                    validation_report['recommendations'].extend(check_result.get('recommendations', []))
                    validation_report['quality_score'] -= check_result.get('penalty', 0)
            except Exception as e:
                logger.error(f"Validation check failed: {e}")
                validation_report['issues'].append(f"Validation error: {str(e)}")

        # Final quality assessment
        validation_report['is_valid'] = len(validation_report['issues']) == 0
        validation_report['quality_score'] = max(0, validation_report['quality_score'])

        return validation_report

    def _validate_basic_structure(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate basic result structure."""
        issues = []

        if 'words' not in result:
            issues.append("Missing 'words' field in analysis result")

        if 'word_combinations' not in result:
            issues.append("Missing 'word_combinations' field")

        if 'original_sentence' not in result:
            issues.append("Missing 'original_sentence' field")

        words = result.get('words', [])
        if len(words) < self.validation_rules['min_words_per_sentence']:
            issues.append(f"Too few words analyzed: {len(words)} (minimum {self.validation_rules['min_words_per_sentence']})")

        if len(words) > self.validation_rules['max_words_per_sentence']:
            issues.append(f"Too many words analyzed: {len(words)} (maximum {self.validation_rules['max_words_per_sentence']})")

        if issues:
            return {'issues': issues, 'penalty': 20}

        return None

    def _validate_grammatical_roles(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate grammatical role assignments."""
        issues = []
        warnings = []

        words = result.get('words', [])
        allowed_roles = set(self.config.grammatical_roles.keys())

        for i, word_data in enumerate(words):
            role = word_data.get('grammatical_role', '')

            if role not in allowed_roles:
                issues.append(f"Word {i+1} ('{word_data.get('word', '')}'): Invalid grammatical role '{role}'")

            # Check for required categories
            if i == 0 and 'noun' not in [w.get('grammatical_role') for w in words]:
                warnings.append("No noun found in sentence - may indicate incorrect analysis")

            if 'verb' not in [w.get('grammatical_role') for w in words]:
                warnings.append("No verb found in sentence - may indicate incorrect analysis")

        if issues:
            return {'issues': issues, 'warnings': warnings, 'penalty': 15}

        return {'warnings': warnings} if warnings else None

    def _validate_word_segmentation(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate word segmentation quality."""
        issues = []
        warnings = []

        sentence = result.get('original_sentence', '')
        words = result.get('words', [])

        # Check if words roughly reconstruct the sentence
        analyzed_text = ''.join([w.get('word', '') for w in words])

        # Allow for some flexibility in segmentation
        if len(analyzed_text) < len(sentence) * 0.8:
            warnings.append("Analyzed text significantly shorter than original - possible under-segmentation")

        if len(analyzed_text) > len(sentence) * 1.5:
            issues.append("Analyzed text significantly longer than original - possible over-segmentation")

        # Check for common segmentation errors
        for word_data in words:
            word = word_data.get('word', '')
            if len(word) > 10:  # Very long "words" might be phrases
                warnings.append(f"Very long word detected: '{word}' - may need further segmentation")

        if issues:
            return {'issues': issues, 'warnings': warnings, 'penalty': 10}

        return {'warnings': warnings} if warnings else None

    def _validate_traditional_characters(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate use of Traditional Chinese characters."""
        issues = []

        sentence = result.get('original_sentence', '')

        # Common Traditional vs Simplified character pairs
        trad_simp_pairs = {
            '臺': '台', '體': '体', '學': '学', '說': '说', '點': '点',
            '們': '们', '還': '还', '時': '时', '間': '间', '電': '电',
            '國': '国', '們': '们', '對': '对', '來': '来', '東': '东'
        }

        has_traditional = False
        has_simplified = False

        for char in sentence:
            if char in trad_simp_pairs:
                has_traditional = True
            elif char in trad_simp_pairs.values():
                has_simplified = True

        if has_simplified and not has_traditional:
            issues.append("Sentence contains Simplified characters - should use Traditional for zh-tw")

        if self.validation_rules.get('traditional_characters_only', False) and has_simplified:
            return {'issues': issues, 'penalty': 25}

        return {'issues': issues, 'penalty': 5} if issues else None

    def _validate_measure_words(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate measure word usage."""
        warnings = []
        recommendations = []

        words = result.get('words', [])
        measure_words_found = []

        for word_data in words:
            if word_data.get('grammatical_role') == 'measure_word':
                measure_words_found.append(word_data.get('word', ''))

        # Check if measure words are appropriate
        valid_measure_words = set(self.config.word_patterns['measure_words'])

        for mw in measure_words_found:
            if mw not in valid_measure_words:
                warnings.append(f"Unusual measure word: '{mw}' - verify if correct")

        # Check for missing measure words before numerals
        for i, word_data in enumerate(words):
            if word_data.get('grammatical_role') == 'numeral':
                # Look ahead for nouns that might need measure words
                if i + 2 < len(words):
                    next_word = words[i + 1]
                    following_word = words[i + 2]

                    if (next_word.get('grammatical_role') == 'noun' and
                        following_word.get('grammatical_role') != 'measure_word'):
                        recommendations.append(f"Consider measure word before noun '{next_word.get('word')}' after numeral '{word_data.get('word')}'")

        return {'warnings': warnings, 'recommendations': recommendations} if warnings or recommendations else None

    def _validate_aspect_particles(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate aspect particle usage."""
        warnings = []

        words = result.get('words', [])
        aspect_particles = []

        for word_data in words:
            if word_data.get('grammatical_role') == 'aspect_particle':
                aspect_particles.append(word_data.get('word', ''))

        # Check for multiple aspect particles (unusual in Chinese)
        if len(aspect_particles) > 1:
            warnings.append(f"Multiple aspect particles found: {aspect_particles} - verify correctness")

        # Check for valid aspect particles
        valid_particles = set(self.config.word_patterns['aspect_particles'])
        for particle in aspect_particles:
            if particle not in valid_particles:
                warnings.append(f"Unusual aspect particle: '{particle}' - verify if correct")

        return {'warnings': warnings} if warnings else None

    def _validate_sentence_coherence(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate overall sentence coherence."""
        warnings = []

        words = result.get('words', [])
        roles = [w.get('grammatical_role') for w in words]

        # Basic coherence checks
        if roles.count('verb') == 0:
            warnings.append("No verbs detected - sentence may be incomplete or incorrectly analyzed")

        # Check for reasonable distribution
        content_words = sum(1 for r in roles if r in ['noun', 'verb', 'adjective', 'adverb'])
        function_words = len(roles) - content_words

        if content_words < function_words:
            warnings.append("More function words than content words - possible analysis error")

        return {'warnings': warnings} if warnings else None

    def _validate_meanings_completeness(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate completeness of word meanings."""
        issues = []

        words = result.get('words', [])

        for i, word_data in enumerate(words):
            meaning = word_data.get('individual_meaning', '').strip()

            if not meaning:
                issues.append(f"Word {i+1} ('{word_data.get('word', '')}'): Missing meaning")

            elif len(meaning) < 3:
                issues.append(f"Word {i+1} ('{word_data.get('word', '')}'): Meaning too short ('{meaning}')")

        return {'issues': issues, 'penalty': 10} if issues else None