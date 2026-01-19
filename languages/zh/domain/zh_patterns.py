# languages/zh/domain/zh_patterns.py
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
- Aspect markers: 了, 着, 过 recognition
- Particles: Structural (的, 地, 得), modal (吗, 呢, 吧)
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
        self.aspect_pattern: Pattern[str] = re.compile(r'\b(?:了|着|过)\b')

        # Modal particles
        self.modal_particle_pattern: Pattern[str] = re.compile(r'\b(?:吗|呢|吧|啊|呀|啦|嘛)\b')

        # Structural particles
        self.structural_particle_pattern: Pattern[str] = re.compile(r'\b(?:的|地|得)\b')

        # General particles (combination)
        self.particle_pattern: Pattern[str] = re.compile(r'\b(?:的|地|得|了|着|过|吗|呢|吧|啊|呀|啦|嘛)\b')

        # Classifiers - common ones
        if hasattr(config, 'classifiers') and config.classifiers:
            self.classifier_pattern: Pattern[str] = re.compile(r'\b(?:' + '|'.join(re.escape(c) for c in config.classifiers) + r')\b')
        else:
            # Fallback common classifiers
            self.classifier_pattern: Pattern[str] = re.compile(r'\b(?:个|本|杯|只|张|件|把|辆|台|位)\b')

        # Han character validation (basic)
        self.han_character_pattern: Pattern[str] = re.compile(r'[\u4e00-\u9fff]')

        # Numbers (Chinese characters)
        self.chinese_number_pattern: Pattern[str] = re.compile(r'\b(?:一|二|三|四|五|六|七|八|九|十|百|千|万|零)\b')

        # Pronouns
        self.pronoun_pattern: Pattern[str] = re.compile(r'\b(?:我|你|他|她|它|我们|你们|他们|她们|这|那|这些|那些)\b')

        # Question words
        self.interrogative_pattern: Pattern[str] = re.compile(r'\b(?:什么|谁|哪里|什么时候|怎么|为什么|多少|几|哪|怎么样)\b')

    def is_particle(self, word: str) -> bool:
        """Check if word is a particle."""
        return bool(self.particle_pattern.search(word))

    def is_aspect_marker(self, word: str) -> bool:
        """Check if word is an aspect marker."""
        return bool(self.aspect_pattern.search(word))

    def is_classifier(self, word: str) -> bool:
        """Check if word is a classifier."""
        return bool(self.classifier_pattern.search(word))

    def is_han_character(self, text: str) -> bool:
        """Check if text contains Han characters."""
        return bool(self.han_character_pattern.search(text))

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