# languages/turkish/domain/tr_fallbacks.py
"""
Turkish Language Analyzer - Fallback Analysis Component

FALLBACK ANALYSIS STRATEGY:
- When AI analysis fails, provide rule-based analysis
- Use Turkish linguistic patterns for grammatical role detection
- Maintain consistent output format with AI results
- Include confidence scoring and fallback indicators

TURKISH FALLBACK PRINCIPLES:
- Agglutination-aware: Handle suffix analysis
- Vowel harmony: Respect harmony rules in fallbacks
- Case system: Identify case markers
- SOV word order: Consider Turkish sentence structure
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Import config for type hints
from .tr_config import TrConfig


class TrFallbacks:
    """
    Turkish Fallback Analysis Component

    PURPOSE:
    - Provide rule-based analysis when AI fails
    - Use Turkish-specific linguistic patterns
    - Maintain consistent output structure
    - Track fallback usage for monitoring

    TURKISH FALLBACK FEATURES:
    - Agglutination handling for compound words
    - Vowel harmony pattern recognition
    - Case marker identification
    - Basic morphological analysis
    """

    def __init__(self, config: TrConfig):
        """
        Initialize fallbacks with configuration.

        CONFIGURATION INTEGRATION:
        1. Access to pre-defined word meanings
        2. Common suffixes and case markers
        3. Vowel harmony patterns
        4. Grammatical role mappings
        """
        self.config = config

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic fallback analysis for Turkish text."""
        logger.info(f"Creating fallback analysis for sentence: '{sentence}'")

        # Split sentence into words (basic tokenization)
        words = self._tokenize_turkish(sentence)
        word_explanations = []
        elements = {}

        for word in words:
            # Try to get meaning from config
            meaning = self.config.word_meanings.get(word, self._generate_fallback_explanation(word))
            role = self._guess_role(word)
            color = self._get_fallback_color(role, complexity)

            word_explanations.append([word, role, color, meaning])

            if role not in elements:
                elements[role] = []
            elements[role].append({'word': word, 'grammatical_role': role})

        result = {
            'sentence': sentence,
            'elements': elements,
            'explanations': {},
            'word_explanations': word_explanations,
            'confidence': 0.3,
            'is_fallback': True
        }

        logger.info(f"Fallback created with {len(word_explanations)} word explanations")
        return result

    def _tokenize_turkish(self, sentence: str) -> List[str]:
        """Basic Turkish tokenization."""
        # Remove extra whitespace and split on spaces
        # Note: This is a simple tokenization; real Turkish NLP would use more sophisticated methods
        return sentence.strip().split()

    def _guess_role(self, word: str) -> str:
        """Guess grammatical role based on Turkish word characteristics."""
        # Clean the word for better matching
        clean_word = word.strip('!?.,;:\"\'()[]{}')

        # Pronouns (zamirler)
        pronouns = [
            'ben', 'sen', 'o', 'biz', 'siz', 'onlar',
            'benim', 'senin', 'onun', 'bizim', 'sizin', 'onların',
            'bana', 'sana', 'ona', 'bize', 'size', 'onlara',
            'beni', 'seni', 'onu', 'bizi', 'sizi', 'onları',
            'bende', 'sende', 'onda', 'bizde', 'sizde', 'onlarda',
            'benden', 'senden', 'ondan', 'bizden', 'sizden', 'onlardan',
            'bu', 'şu', 'o', 'bunlar', 'şunlar', 'onlar'
        ]
        if clean_word in pronouns:
            return 'pronoun'

        # Prepositions (edatlar)
        prepositions = [
            'için', 'ile', 'gibi', 'kadar', 'doğru', 'karşı', 'üzere',
            'itibaren', 'rağmen', 'dolayı', 'yönelik', 'bağlı', 'ilişkin'
        ]
        if clean_word in prepositions:
            return 'preposition'

        # Question words (soru zamirleri)
        question_words = [
            'ne', 'kim', 'nasıl', 'neden', 'nerede', 'ne zaman', 'kaç', 'hangi', 'mi'
        ]
        if clean_word in question_words:
            return 'question_word'

        # Conjunctions (bağlaçlar)
        conjunctions = [
            've', 'veya', 'ama', 'fakat', 'çünkü', 'ki', 'eğer', 'madem', 'halbuki'
        ]
        if clean_word in conjunctions:
            return 'conjunction'

        # Check for case markers (hal ekleri)
        if self._has_case_marker(clean_word):
            return 'noun'

        # Check for possessive suffixes
        if self._has_possessive_suffix(clean_word):
            return 'noun'

        # Default to verb if ends with common verb suffixes
        if any(clean_word.endswith(suffix) for suffix in ['mak', 'mek', 'yor', 'di', 'miş', 'ecek']):
            return 'verb'

        # Default to noun for most other words
        return 'noun'

    def _has_case_marker(self, word: str) -> bool:
        """Check if word has Turkish case markers."""
        case_markers = ['i', 'ı', 'u', 'ü', 'e', 'a', 'da', 'de', 'ta', 'te', 'den', 'dan', 'ten', 'tan', 'in', 'ın', 'un', 'ün']
        return any(word.endswith(marker) for marker in case_markers)

    def _has_possessive_suffix(self, word: str) -> bool:
        """Check if word has Turkish possessive suffixes."""
        possessive_suffixes = ['im', 'ım', 'um', 'üm', 'in', 'ın', 'un', 'ün', 'imiz', 'ımız', 'umuz', 'ümüz', 'iniz', 'ınız', 'unuz', 'ünüz', 'leri']
        return any(word.endswith(suffix) for suffix in possessive_suffixes)

    def _generate_fallback_explanation(self, word: str) -> str:
        """Generate a basic explanation for unknown words."""
        if self._has_case_marker(word):
            return f"Turkish noun with case marker"
        elif self._has_possessive_suffix(word):
            return f"Turkish noun with possessive suffix"
        elif word.endswith(('mak', 'mek')):
            return f"Turkish infinitive verb"
        elif word.endswith('yor'):
            return f"Turkish present continuous verb"
        else:
            return f"Turkish word (meaning not in dictionary)"

    def _get_fallback_color(self, role: str, complexity: str) -> str:
        """Get fallback color based on grammatical role and complexity."""
        # Use config color scheme if available
        color_scheme = self.config.get_color_scheme(complexity)
        if color_scheme and role in color_scheme:
            return color_scheme[role]

        # Fallback colors based on role
        fallback_colors = {
            'noun': '#FF6B6B',      # Red
            'verb': '#4ECDC4',      # Teal
            'adjective': '#45B7D1', # Blue
            'pronoun': '#96CEB4',   # Green
            'preposition': '#FFEAA7', # Yellow
            'conjunction': '#DDA0DD', # Plum
            'question_word': '#98D8C8', # Mint
            'other': '#F7DC6F'      # Light yellow
        }

        return fallback_colors.get(role, '#F7DC6F')