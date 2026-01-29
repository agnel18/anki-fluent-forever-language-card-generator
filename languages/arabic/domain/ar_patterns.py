# languages/arabic/domain/ar_patterns.py
"""
Arabic Patterns - Domain Component

GOLD STANDARD PATTERN SYSTEM:
This component demonstrates how to implement regex-based linguistic pattern recognition.
It provides rule-based validation and enhancement for Arabic grammar analysis.

RESPONSIBILITIES:
1. Define regex patterns for Arabic linguistic features
2. Provide pattern-based validation and enhancement
3. Support morphological and syntactic pattern recognition
4. Enable rule-based fallback and validation logic
5. Maintain patterns separate from business logic

PATTERN CATEGORIES:
- Definite article patterns: Sun/moon letter assimilation
- Case marking patterns: Tanween and i'rab markers
- Verb form patterns: Perfect, imperfect, imperative
- Noun patterns: Sound/broken plural patterns
- Root patterns: Triliteral morphological patterns
- Particle patterns: Prepositions, conjunctions, interrogatives

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
from typing import Dict, Pattern, List, Any
from .ar_config import ArConfig

class ArPatterns:
    """
    Regex patterns and markers for Arabic analysis.

    GOLD STANDARD PATTERN DESIGN:
    - Compiled regex: Pre-compiled for performance
    - Configuration-driven: Patterns loaded from external files
    - Focused scope: Most important patterns only
    - Validation-oriented: Support quality checking
    """

    def __init__(self, config: ArConfig):
        self.config = config
        self._compiled_patterns = {}
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize and compile Arabic-specific regex patterns"""
        # Load patterns from config if available
        patterns_data = getattr(self.config, 'patterns', {})

        # Definite article patterns
        self._compiled_patterns['definite_article_sun'] = re.compile(
            r'\bا[سشصضطظلن]\w*', re.UNICODE
        )
        self._compiled_patterns['definite_article_moon'] = re.compile(
            r'\bال\w+', re.UNICODE
        )

        # Case marking patterns (i'rab)
        self._compiled_patterns['tanween_dhamma'] = re.compile(
            r'\w+ٌ\b', re.UNICODE
        )
        self._compiled_patterns['tanween_kasra'] = re.compile(
            r'\w+ٍ\b', re.UNICODE
        )
        self._compiled_patterns['tanween_fatha'] = re.compile(
            r'\w+ً\b', re.UNICODE
        )

        # Verb form patterns
        self._compiled_patterns['perfect_verb'] = re.compile(
            r'\b\w*[اى](\s|$)', re.UNICODE
        )
        self._compiled_patterns['imperfect_verb'] = re.compile(
            r'\bي\w*[و]\b', re.UNICODE
        )
        self._compiled_patterns['imperative_verb'] = re.compile(
            r'\b[ائ]\w*[و]\b', re.UNICODE
        )

        # Noun patterns
        self._compiled_patterns['sound_masculine_plural'] = re.compile(
            r'\w+ون\b', re.UNICODE
        )
        self._compiled_patterns['sound_feminine_plural'] = re.compile(
            r'\w+ات\b', re.UNICODE
        )
        self._compiled_patterns['dual'] = re.compile(
            r'\w+ان\b', re.UNICODE
        )

        # Particle patterns
        self._compiled_patterns['preposition'] = re.compile(
            r'\b(في|من|إلى|على|مع|بعد|قبل|حتى|خلال|عند)\b', re.UNICODE
        )
        self._compiled_patterns['conjunction'] = re.compile(
            r'\b(و|ف|ثم|بل|لكن|أما|إما|إذن|لأن|حتى)\b', re.UNICODE
        )
        self._compiled_patterns['interrogative'] = re.compile(
            r'\b(هل|من|ما|متى|أين|كيف|لماذا|أي)\b', re.UNICODE
        )

        # Number patterns
        self._compiled_patterns['cardinal_number'] = re.compile(
            r'\b(واحد|اثنان|ثلاثة|أربعة|خمسة|ستة|سبعة|ثمانية|تسعة|عشرة)\b', re.UNICODE
        )
        self._compiled_patterns['ordinal_number'] = re.compile(
            r'\b(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر)\b', re.UNICODE
        )

    def get_pattern(self, pattern_name: str) -> Pattern:
        """Get a compiled regex pattern by name"""
        return self._compiled_patterns.get(pattern_name)

    def match_pattern(self, text: str, pattern_name: str) -> bool:
        """Check if text matches a specific pattern"""
        pattern = self.get_pattern(pattern_name)
        if pattern:
            return bool(pattern.search(text))
        return False

    def find_all_matches(self, text: str, pattern_name: str) -> List[str]:
        """Find all matches of a pattern in text"""
        pattern = self.get_pattern(pattern_name)
        if pattern:
            return pattern.findall(text)
        return []

    def is_definite_article_sun(self, word: str) -> bool:
        """Check if word starts with definite article + sun letter"""
        return self.match_pattern(word, 'definite_article_sun')

    def is_definite_article_moon(self, word: str) -> bool:
        """Check if word starts with definite article + moon letter"""
        return self.match_pattern(word, 'definite_article_moon')

    def has_tanween(self, word: str) -> str:
        """Check what type of tanween (if any) a word has"""
        if self.match_pattern(word, 'tanween_dhamma'):
            return 'dhamma'
        elif self.match_pattern(word, 'tanween_kasra'):
            return 'kasra'
        elif self.match_pattern(word, 'tanween_fatha'):
            return 'fatha'
        return None

    def get_verb_form(self, word: str) -> str:
        """Determine verb form based on patterns"""
        if self.match_pattern(word, 'perfect_verb'):
            return 'perfect'
        elif self.match_pattern(word, 'imperfect_verb'):
            return 'imperfect'
        elif self.match_pattern(word, 'imperative_verb'):
            return 'imperative'
        return None

    def get_noun_form(self, word: str) -> str:
        """Determine noun number form based on patterns"""
        if self.match_pattern(word, 'sound_masculine_plural'):
            return 'sound_masculine_plural'
        elif self.match_pattern(word, 'sound_feminine_plural'):
            return 'sound_feminine_plural'
        elif self.match_pattern(word, 'dual'):
            return 'dual'
        return 'singular'

    def get_particle_type(self, word: str) -> str:
        """Determine particle type based on patterns"""
        if self.match_pattern(word, 'preposition'):
            return 'preposition'
        elif self.match_pattern(word, 'conjunction'):
            return 'conjunction'
        elif self.match_pattern(word, 'interrogative'):
            return 'interrogative'
        return None

    def get_number_type(self, word: str) -> str:
        """Determine number type based on patterns"""
        if self.match_pattern(word, 'cardinal_number'):
            return 'cardinal'
        elif self.match_pattern(word, 'ordinal_number'):
            return 'ordinal'
        return None

    def validate_arabic_text(self, text: str) -> Dict[str, Any]:
        """Comprehensive validation of Arabic text using patterns"""
        validation = {
            'is_arabic': False,
            'has_tanween': False,
            'has_definite_article': False,
            'verb_forms': [],
            'noun_forms': [],
            'particles': [],
            'numbers': [],
            'confidence_score': 0.0
        }

        # Check for Arabic characters
        arabic_chars = sum(1 for char in text if 0x0600 <= ord(char) <= 0x06FF)
        validation['is_arabic'] = arabic_chars > 0

        if not validation['is_arabic']:
            return validation

        # Analyze words
        words = re.findall(r'\S+', text)

        for word in words:
            # Check tanween
            tanween_type = self.has_tanween(word)
            if tanween_type:
                validation['has_tanween'] = True

            # Check definite article
            if self.is_definite_article_sun(word) or self.is_definite_article_moon(word):
                validation['has_definite_article'] = True

            # Check verb forms
            verb_form = self.get_verb_form(word)
            if verb_form:
                validation['verb_forms'].append(verb_form)

            # Check noun forms
            noun_form = self.get_noun_form(word)
            if noun_form != 'singular':
                validation['noun_forms'].append(noun_form)

            # Check particles
            particle_type = self.get_particle_type(word)
            if particle_type:
                validation['particles'].append(particle_type)

            # Check numbers
            number_type = self.get_number_type(word)
            if number_type:
                validation['numbers'].append(number_type)

        # Calculate confidence score
        features_found = sum([
            validation['has_tanween'],
            validation['has_definite_article'],
            len(validation['verb_forms']) > 0,
            len(validation['noun_forms']) > 0,
            len(validation['particles']) > 0,
            len(validation['numbers']) > 0
        ])

        validation['confidence_score'] = min(features_found * 0.2, 1.0)

        return validation