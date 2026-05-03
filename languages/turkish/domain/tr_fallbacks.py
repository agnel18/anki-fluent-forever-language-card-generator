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
        """Generate a basic explanation for unknown words.

        Produces a multi-clause explanation including the word itself plus a
        Turkish-specific morphological note (case marker / possessive suffix /
        verb tense), mirroring de_fallbacks so cards never display generic stubs.
        """
        clean_word = word.strip('!?.,;:"\'()[]{}')

        if self._has_case_marker(clean_word):
            return (
                f"Noun '{word}' inflected with a case-marking suffix. Turkish nouns take six cases — nominative (∅), "
                f"accusative (-i/ı/u/ü), dative (-e/a), locative (-de/da), ablative (-den/dan), genitive (-in/ın/un/ün) — "
                f"following vowel-harmony rules."
            )
        if self._has_possessive_suffix(clean_word):
            return (
                f"Noun '{word}' inflected with a possessive suffix. Turkish encodes 'my/your/his/our/their' as a suffix "
                f"on the possessed noun (e.g. ev-im 'my house', ev-imiz 'our house'), following vowel-harmony rules."
            )
        if clean_word.endswith(('mak', 'mek')):
            return (
                f"Infinitive verb '{word}'. The -mak / -mek suffix forms the dictionary form of a Turkish verb; "
                f"-mak attaches to back-vowel stems and -mek to front-vowel stems (vowel harmony)."
            )
        if clean_word.endswith('yor'):
            return (
                f"Verb '{word}' in the present continuous tense. The -(I)yor suffix marks ongoing action; the verb "
                f"also takes a personal ending agreeing with the subject (-um/-sun/-uz/-sunuz/-lar)."
            )
        if clean_word.endswith(('di', 'dı', 'du', 'dü', 'ti', 'tı', 'tu', 'tü')):
            return (
                f"Verb '{word}' in the simple past (definite past) tense. The -DI suffix marks a witnessed past action; "
                f"the consonant alternates t/d under consonant assimilation, and the vowel obeys vowel harmony."
            )
        if clean_word.endswith(('miş', 'mış', 'muş', 'müş')):
            return (
                f"Verb '{word}' in the inferential past (-mIş) tense. Marks a reported, inferred, or unwitnessed past "
                f"action; the vowel obeys 4-way vowel harmony."
            )
        if clean_word.endswith(('ecek', 'acak')):
            return (
                f"Verb '{word}' in the future tense. The -(y)AcAk suffix marks future action; takes a personal ending "
                f"agreeing with the subject."
            )
        return (
            f"Turkish word '{word}' — POS could not be determined by rule-based fallback. "
            f"Turkish is agglutinative; suffixes carry case, possession, person, tense, and mood, so unrecognised "
            f"words may carry information not captured by the fallback heuristics."
        )

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