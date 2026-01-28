# languages/chinese_traditional/domain/zh_tw_fallbacks.py
"""
Chinese Traditional Fallbacks - Domain Component

CHINESE TRADITIONAL FALLBACK SYSTEM:
This component provides comprehensive error recovery for Chinese Traditional grammar analysis.
It provides rule-based fallbacks when AI parsing fails, ensuring users always get results.

RESPONSIBILITIES:
1. Generate basic grammar analysis when AI fails
2. Apply rule-based role assignment using Chinese Traditional patterns
3. Provide meaningful explanations for fallback results
4. Maintain consistent output format with AI results
5. Use configuration data for accurate fallback assignments

FALLBACK STRATEGIES:
1. Dictionary lookup: Pre-defined meanings for known words
2. Pattern matching: Character-based role detection for particles/aspect
3. Morphological analysis: Basic compound word recognition
4. Contextual defaults: Chinese-appropriate default assignments
5. Color coding: Consistent with main analyzer color schemes

USAGE FOR CHINESE TRADITIONAL:
1. Copy fallback structure and pattern logic
2. Implement Chinese Traditional-specific role guessing rules (particles, aspect, classifiers)
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
from .zh_tw_config import ZhTwConfig

logger = logging.getLogger(__name__)

class ZhTwFallbacks:
    """
    Provides fallback responses when parsing fails.

    CHINESE TRADITIONAL FALLBACK DESIGN:
    - Rule-based analysis: Linguistic patterns over random guessing
    - Configuration-driven: Uses Chinese Traditional-specific data and patterns
    - Quality preservation: Better than no analysis, guides improvement
    - Consistent format: Same output structure as AI results
    - Logging: Tracks fallback usage for monitoring

    FALLBACK QUALITY PRINCIPLES:
    - Better than nothing: Useful even if not perfect
    - Language-aware: Uses real Chinese Traditional grammar patterns
    - Consistent: Same logic produces same results
    - Maintainable: Easy to improve with new patterns
    """

    def __init__(self, config: ZhTwConfig):
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
        # For Chinese Traditional, split by spaces (assuming pre-segmented) or by characters
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
        # Clean the word
        clean_word = word.strip('。！？，、；："''（）【】{}')

        # Aspect markers (very important in Chinese Traditional)
        if clean_word in ['了', '着', '過']:
            return 'aspect_marker'

        # Modal particles
        if clean_word in ['嗎', '呢', '吧', '啊', '呀', '啦', '嘛']:
            return 'modal_particle'

        # Structural particles
        if clean_word in ['的', '地', '得']:
            return 'structural_particle'

        # General particles
        if clean_word in ['了', '着', '過', '的', '地', '得', '嗎', '呢', '吧', '啊']:
            return 'particle'

        # Common classifiers (Traditional Chinese versions)
        if clean_word in self.config.common_classifiers:
            return 'classifier'

        # Pronouns
        if clean_word in ['我', '你', '他', '她', '它', '我們', '你們', '他們', '她們', '這', '那', '這些', '那些']:
            return 'pronoun'

        # Question words
        if clean_word in ['什麼', '誰', '哪裡', '什麼時候', '怎麼', '為什麼', '多少', '幾']:
            return 'interrogative'

        # Conjunctions
        if clean_word in ['和', '與', '或', '但是', '因為', '所以', '如果', '雖然']:
            return 'conjunction'

        # Prepositions
        if clean_word in ['在', '從', '到', '給', '對', '向', '跟', '被']:
            return 'preposition'

        # Numbers
        if clean_word.isdigit() or clean_word in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '萬']:
            return 'numeral'

        # Interjections
        if clean_word in ['啊', '哦', '哎呀', '嗯', '唉']:
            return 'interjection'

        # Verb-like endings or common verbs (basic heuristics)
        if len(clean_word) >= 2 and any(clean_word.endswith(suffix) for suffix in ['了', '着', '過', '來', '去', '到']):
            return 'verb'

        # Adjective-like (basic heuristics - adjectives often end with 的 or are single syllable)
        if len(clean_word) == 1 or clean_word.endswith('的'):
            return 'adjective'

        # Default to noun for most other words (most common in Chinese)
        return 'noun'

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
        return role_descriptions.get(role, f'a {role} in Chinese Traditional')