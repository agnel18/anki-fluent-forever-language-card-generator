# languages/chinese_simplified/domain/zh_patterns.py
"""
Chinese Simplified Patterns - Domain Component

CHINESE PATTERN SYSTEM:
This component demonstrates how to implement regex-based linguistic pattern recognition for Chinese.
It provides rule-based validation and enhancement for Chinese grammar analysis.

RESPONSIBILITIES:
1. Define regex patterns for Chinese linguistic features
2. Provide pattern-based validation and enhancement
3. Support morphological and syntactic pattern recognition
4. Enable rule-based fallback and validation logic
5. Maintain patterns separate from business logic

PATTERN CATEGORIES:
- Aspect markers: äº†, ç€, è¿‡ recognition
- Particles: Structural (çš„, åœ°, å¾—), modal (å—, å‘¢, å§)
- Classifiers: Common measure words
- Character patterns: Han character validation
- Compound recognition: Multi-character word patterns

USAGE FOR CHINESE:
1. Copy pattern structure for similar languages
2. Implement Chinese-specific regex patterns
3. Focus on most frequent and distinctive features
4. Test patterns against real language data
5. Balance complexity with maintainability

INTEGRATION:
- Used by validator for pattern-based quality checks
- Referenced by fallbacks for rule-based role assignment
- Loaded from configuration files for maintainability
- Supports both validation and generation tasks
"""

import re
from typing import Dict, Pattern
from .zh_config import ZhConfig

class ZhPatterns:
    """
    Regex patterns and markers for Chinese analysis.

    CHINESE PATTERN DESIGN:
    - Compiled regex: Pre-compiled for performance
    - Configuration-driven: Patterns loaded from external files
    - Focused scope: Most important patterns only
    - Validation-oriented: Support quality checking
    - Extensible: Easy to add new patterns

    PATTERN PHILOSOPHY:
    - Quality over quantity: Few high-signal patterns
    - Maintainable: Clear naming and documentation
    - Testable: Patterns can be unit tested
    - Performance-conscious: Compiled and cached
    """

    def __init__(self, config: ZhConfig):
        """
        Initialize patterns from configuration.

        PATTERN INITIALIZATION:
        1. Load patterns from config YAML files
        2. Compile regex patterns for performance
        3. Validate pattern syntax
        4. Set up pattern collections by category
        5. Handle missing patterns gracefully
        """
        self.config = config

        # Aspect markers - critical for Chinese grammar
        self.aspect_pattern: Pattern[str] = re.compile(r'(?:\u4e86|\u7740|\u8fc7)')

        # Modal particles
        self.modal_particle_pattern: Pattern[str] = re.compile(r'(?:\u5417|\u5462|\u5427|\u554a|\u54e6|\u5566|\u561b)')

        # Structural particles
        self.structural_particle_pattern: Pattern[str] = re.compile(r'(?:\u7684|\u5730|\u5f97)')

        # General particles (combination)
        self.particle_pattern: Pattern[str] = re.compile(r'(?:\u7684|\u5730|\u5f97|\u4e86|\u7740|\u8fc7|\u5417|\u5462|\u5427|\u554a|\u54e6|\u5566|\u561b)')

        # Classifiers - common ones
        if hasattr(config, 'classifiers') and config.classifiers:
            self.classifier_pattern: Pattern[str] = re.compile(r'(?:' + '|'.join(re.escape(c) for c in config.classifiers) + r')')
        else:
            # Fallback common classifiers
            self.classifier_pattern: Pattern[str] = re.compile(r'(?:\u4e2a|\u672c|\u676f|\u53ea|\u5f20|\u4ef6|\u628a|\u8f86|\u53f0|\u4f4d)')

        # Han character validation (basic)
        self.han_character_pattern: Pattern[str] = re.compile(r'[\u4e00-\u9fff]')

        # Numbers (Chinese characters)
        self.chinese_number_pattern: Pattern[str] = re.compile(r'(?:\u4e00|\u4e8c|\u4e09|\u56db|\u4e94|\u516d|\u4e03|\u516b|\u4e5d|\u5341|\u767e|\u5343|\u4e07|\u96f6)')

        # Pronouns
        self.pronoun_pattern: Pattern[str] = re.compile(r'(?:\u6211|\u4f60|\u4ed6|\u5979|\u5b83|\u6211\u4eec|\u4f60\u4eec|\u4ed6\u4eec|\u5979\u4eec|\u8fd9|\u90a3|\u8fd9\u4e9b|\u90a3\u4e9b)')

        # Question words
        self.interrogative_pattern: Pattern[str] = re.compile(r'(?:\u4ec0\u4e48|\u8c01|\u54ea\u91cc|\u4ec0\u4e48\u65f6\u5019|\u600e\u4e48|\u4e3a\u4ec0\u4e48|\u591a\u5c11|\u51e0|\u54ea|\u600e\u4e48\u6837)')

    def is_particle(self, word: str) -> bool:
        """Check if word is a particle."""
        normalized = self._normalize_text(word)
        return bool(self.particle_pattern.search(normalized))

    def is_aspect_marker(self, word: str) -> bool:
        """Check if word is an aspect marker."""
        normalized = self._normalize_text(word)
        return bool(self.aspect_pattern.search(normalized))

    def is_classifier(self, word: str) -> bool:
        """Check if word is a classifier."""
        normalized = self._normalize_text(word)
        return bool(self.classifier_pattern.search(normalized))

    def is_han_character(self, text: str) -> bool:
        """Check if text contains Han characters."""
        normalized = self._normalize_text(text)
        return bool(self.han_character_pattern.search(normalized))

    def _normalize_text(self, text: str) -> str:
        """Normalize mojibake-encoded Chinese text to Unicode if needed."""
        if not text:
            return text
        replacements = {
            "ç€": "\u7740",
            "å—": "\u5417",
            "æ¯": "\u676f"
        }
        if any(0x80 <= ord(ch) <= 0x9f for ch in text):
            text = ''.join(ch for ch in text if not (0x80 <= ord(ch) <= 0x9f))
        for bad, good in replacements.items():
            if bad in text:
                text = text.replace(bad, good)
        if any('\u4e00' <= ch <= '\u9fff' for ch in text):
            return text
        for encoding in ('latin-1', 'cp1252'):
            try:
                repaired = text.encode(encoding).decode('utf-8')
            except UnicodeError:
                continue
            if any('\u4e00' <= ch <= '\u9fff' for ch in repaired):
                return repaired
        if all(ord(ch) < 256 for ch in text):
            try:
                repaired = bytes(ord(ch) for ch in text).decode('utf-8')
            except UnicodeError:
                return text
            if any('\u4e00' <= ch <= '\u9fff' for ch in repaired):
                return repaired
        return text

    def has_valid_chinese_structure(self, sentence: str) -> bool:
        """Basic validation of Chinese sentence structure."""
        # Must contain Han characters
        if not self.is_han_character(sentence):
            return False

        # Should have some particles (common in Chinese)
        words = sentence.split()
        has_particles = any(self.is_particle(word) for word in words)

        # Should have some content words (basic check)
        return len(words) > 0 and (has_particles or len(words) > 1)
