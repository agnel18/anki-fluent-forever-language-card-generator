# languages/chinese_simplified/domain/zh_fallbacks.py
"""
Chinese Simplified Fallbacks - Domain Component

CHINESE FALLBACK SYSTEM:
This component demonstrates comprehensive error recovery for Chinese grammar analysis.
It provides rule-based fallbacks when AI parsing fails, ensuring users always get results.

RESPONSIBILITIES:
1. Generate basic grammar analysis when AI fails
2. Apply rule-based role assignment using Chinese patterns
3. Provide meaningful explanations for fallback results
4. Maintain consistent output format with AI results
5. Use configuration data for accurate fallback assignments

FALLBACK STRATEGIES:
1. Dictionary lookup: Pre-defined meanings for known words
2. Pattern matching: Character-based role detection for particles/aspect
3. Morphological analysis: Basic compound word recognition
4. Contextual defaults: Chinese-appropriate default assignments
5. Color coding: Consistent with main analyzer color schemes

USAGE FOR CHINESE:
1. Copy fallback structure and pattern logic
2. Implement Chinese-specific role guessing rules (particles, aspect, classifiers)
3. Create comprehensive word lists for target language
4. Test fallbacks provide reasonable quality
5. Ensure fallbacks maintain user experience continuity

INTEGRATION:
- Called by response parser when AI parsing fails
- Used by main analyzer for complete failure recovery
- Provides confidence scores (typically 0.3) for fallback results
- Maintains same output format as successful AI analysis
"""

import logging
from typing import Dict, Any
from .zh_config import ZhConfig

logger = logging.getLogger(__name__)

class ZhFallbacks:
    """
    Provides fallback responses when parsing fails.

    CHINESE FALLBACK DESIGN:
    - Rule-based analysis: Linguistic patterns over random guessing
    - Configuration-driven: Uses Chinese-specific data and patterns
    - Quality preservation: Better than no analysis, guides improvement
    - Consistent format: Same output structure as AI results
    - Logging: Tracks fallback usage for monitoring

    FALLBACK QUALITY PRINCIPLES:
    - Better than nothing: Useful even if not perfect
    - Language-aware: Uses real Chinese grammar patterns
    - Consistent: Same logic produces same results
    - Maintainable: Easy to improve with new patterns
    """

    def __init__(self, config: ZhConfig):
        """
        Initialize fallbacks with configuration.

        CONFIGURATION INTEGRATION:
        1. Access to pre-defined word meanings
        2. Common classifiers and particles
        3. Aspect markers and structural particles
        4. Pattern definitions for rule-based analysis
        5. Color schemes for consistent output
        """
        self.config = config

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic fallback analysis."""
        logger.info(f"Creating fallback analysis for sentence: '{sentence}'")
        # For Chinese, split by spaces (assuming pre-segmented) or by characters
        words = sentence.split() if ' ' in sentence else list(sentence)  # Character-level fallback
        word_explanations = []
        elements = {}

        for word in words:
            # Try to get meaning from config
            meaning = self.config.word_meanings.get(word, self._generate_fallback_explanation(word))
            role = self._guess_role(word)
            color = self._get_fallback_color(role)

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

    def _guess_role(self, word: str) -> str:
        """Guess grammatical role based on word characteristics."""
        word = self._normalize_text(word)
        # Clean the word
        clean_word = word.strip("\u3002\uff01\uff1f\uff0c\u3001\uff1b\uff1a\"'\uff08\uff09\u3010\u3011{}")

        # Aspect markers (very important in Chinese)
        if clean_word in ['\u4e86', '\u7740', '\u8fc7']:
            return 'aspect_marker'

        # Modal particles
        if clean_word in ['\u5417', '\u5462', '\u5427', '\u554a', '\u54e6', '\u5566', '\u561b']:
            return 'modal_particle'

        # Structural particles
        if clean_word in ['\u7684', '\u5730', '\u5f97']:
            return 'structural_particle'

        # General particles
        if clean_word in ['\u4e86', '\u7740', '\u8fc7', '\u7684', '\u5730', '\u5f97', '\u5417', '\u5462', '\u5427', '\u554a']:
            return 'particle'

        # Common classifiers
        if clean_word in self.config.classifiers:
            return 'classifier'

        # Pronouns
        if clean_word in ['\u6211', '\u4f60', '\u4ed6', '\u5979', '\u5b83', '\u6211\u4eec', '\u4f60\u4eec', '\u4ed6\u4eec', '\u5979\u4eec', '\u8fd9', '\u90a3', '\u8fd9\u4e9b', '\u90a3\u4e9b']:
            return 'pronoun'

        # Question words
        if clean_word in ['\u4ec0\u4e48', '\u8c01', '\u54ea\u91cc', '\u4ec0\u4e48\u65f6\u5019', '\u600e\u4e48', '\u4e3a\u4ec0\u4e48', '\u591a\u5c11', '\u51e0']:
            return 'interrogative'

        # Conjunctions
        if clean_word in ['\u548c', '\u4e0e', '\u6216', '\u4f46\u662f', '\u56e0\u4e3a', '\u6240\u4ee5', '\u5982\u679c', '\u867d\u7136']:
            return 'conjunction'

        # Prepositions
        if clean_word in ['\u5728', '\u4ece', '\u5230', '\u7ed9', '\u5bf9', '\u5411', '\u8ddf', '\u88ab']:
            return 'preposition'

        # Numbers
        if clean_word.isdigit() or clean_word in ['\u4e00', '\u4e8c', '\u4e09', '\u56db', '\u4e94', '\u516d', '\u4e03', '\u516b', '\u4e5d', '\u5341', '\u767e', '\u5343', '\u4e07']:
            return 'numeral'

        # Interjections
        if clean_word in ['\u554a', '\u54e6', '\u54ce\u54ce', '\u55ef', '\u54ce']:
            return 'interjection'

        # Verb-like endings or common verbs (basic heuristics)
        if len(clean_word) >= 2 and any(clean_word.endswith(suffix) for suffix in ['\u4e86', '\u7740', '\u8fc7', '\u6765', '\u53bb', '\u5230']):
            return 'verb'

        # Adjective-like (basic heuristics - adjectives often end with çš„ or are single syllable)
        if len(clean_word) == 1 or clean_word.endswith('\u7684'):
            return 'adjective'

        # Default to noun for most other words (most common in Chinese)
        return 'noun'

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

    def _get_fallback_color(self, role: str) -> str:
        """Get color for fallback role."""
        # Use the same color scheme as the main analyzer
        colors = self.config.get_color_scheme('intermediate')
        return colors.get(role, '#AAAAAA')

    def _generate_fallback_explanation(self, word: str) -> str:
        """Generate a basic explanation for a word when no specific meaning is available."""
        role = self._guess_role(word)
        role_descriptions = {
            'noun': 'a thing, person, or concept',
            'verb': 'an action or state of being',
            'adjective': 'a word that describes a noun',
            'pronoun': 'a word that replaces a noun',
            'particle': 'a grammatical function word',
            'aspect_marker': 'a marker indicating action completion, ongoing state, or experience',
            'modal_particle': 'a particle expressing mood, tone, or attitude',
            'structural_particle': 'a particle connecting elements in a sentence',
            'classifier': 'a measure word used with numerals and nouns',
            'preposition': 'a word showing relationship or direction',
            'conjunction': 'a word connecting clauses or sentences',
            'interjection': 'an exclamation or sound',
            'numeral': 'a number',
            'interrogative': 'a question word',
            'other': 'a word in the sentence'
        }
        return role_descriptions.get(role, f'a {role} in Chinese')
