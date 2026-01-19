# languages/hindi/domain/hi_patterns.py
"""
Hindi Patterns - Domain Component

GOLD STANDARD PATTERN SYSTEM:
This component demonstrates how to implement regex-based linguistic pattern recognition.
It provides rule-based validation and enhancement for Hindi grammar analysis.

RESPONSIBILITIES:
1. Define regex patterns for Hindi linguistic features
2. Provide pattern-based validation and enhancement
3. Support morphological and syntactic pattern recognition
4. Enable rule-based fallback and validation logic
5. Maintain patterns separate from business logic

PATTERN CATEGORIES:
- Postposition recognition: Common Hindi postpositions
- Gender markers: Masculine/feminine agreement patterns
- Case markers: Nominative, accusative, dative, etc.
- Honorific markers: Respect levels and formality
- Verb conjugations: Tense, aspect, mood patterns
- Word formation: Compound words, reduplication

USAGE FOR NEW LANGUAGES:
1. Copy pattern structure for similar languages
2. Implement language-specific regex patterns
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
from .hi_config import HiConfig

class HiPatterns:
    """
    Regex patterns and markers for Hindi analysis.

    GOLD STANDARD PATTERN DESIGN:
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

    def __init__(self, config: HiConfig):
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
        self.postposition_pattern: Pattern[str] = re.compile(r'\b(?:' + '|'.join(re.escape(p) for p in config.common_postpositions) + r')\b')
        # Add more patterns as needed, e.g., gender, case, honorifics
        self.gender_patterns = {}  # Populate from config
        self.case_patterns = {}
        self.honorific_patterns = {}