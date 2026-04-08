# languages/malayalam/domain/ml_fallbacks.py
"""
Malayalam Fallbacks - Domain Component

Rule-based fallback analysis for when AI parsing fails.
Uses Malayalam-specific word patterns and common word lists.
"""

import logging
import re
import unicodedata
from typing import Dict, Any, List
from .ml_config import MlConfig

logger = logging.getLogger(__name__)


class MlFallbacks:
    """Provides fallback responses when AI parsing fails for Malayalam."""

    def __init__(self, config: MlConfig):
        self.config = config

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic fallback analysis for a Malayalam sentence."""
        logger.info(f"Creating fallback analysis for sentence: '{sentence}'")

        tokens = self._basic_tokenize(sentence)
        word_explanations = []
        elements = {}

        for token in tokens:
            meaning = self.config.word_meanings.get('common_words', {}).get(
                token, self._generate_fallback_explanation(token)
            )
            role = self._guess_role(token)
            color = self._get_fallback_color(role, complexity)

            word_explanations.append([token, role, color, meaning])

            if role not in elements:
                elements[role] = []
            elements[role].append({'word': token, 'grammatical_role': role})

        result = {
            'sentence': sentence,
            'elements': elements,
            'explanations': {
                'overall_structure': 'Basic grammatical analysis (fallback)',
                'key_features': 'Malayalam word type detection based on patterns',
                'complexity_notes': 'Rule-based analysis without AI'
            },
            'word_explanations': word_explanations,
            'confidence': 0.3,
            'is_fallback': True
        }
        logger.info(f"Fallback created with {len(word_explanations)} word explanations")
        return result

    def _basic_tokenize(self, sentence: str) -> List[str]:
        """
        Basic Malayalam tokenization by splitting on spaces and punctuation.

        Malayalam uses spaces between words (unlike Japanese), so basic
        whitespace tokenization works reasonably well.
        """
        if not sentence:
            return []

        # Remove common punctuation
        cleaned = re.sub(r'[।,.!?;:\'"()""''…]', ' ', sentence)
        tokens = [t.strip() for t in cleaned.split() if t.strip()]
        return tokens

    def _guess_role(self, token: str) -> str:
        """Guess grammatical role based on Malayalam word patterns."""
        # Common pronouns
        pronouns = {
            'ഞാൻ', 'നീ', 'അവൻ', 'അവൾ', 'അത്', 'ഞങ്ങൾ', 'നിങ്ങൾ',
            'അവർ', 'താങ്കൾ', 'ഇത്', 'എന്റെ', 'നിന്റെ', 'അവന്റെ',
            'അവളുടെ', 'നമ്മുടെ', 'എനിക്ക്', 'നിനക്ക്'
        }
        if token in pronouns:
            return 'pronoun'

        # Common postpositions
        postpositions = {
            'മുകളിൽ', 'താഴെ', 'അടുത്ത്', 'പിന്നിൽ', 'മുന്നിൽ',
            'ഇടയിൽ', 'വേണ്ടി', 'കുറിച്ച്', 'മുതൽ', 'വരെ',
            'ശേഷം', 'മുമ്പ്', 'കൂടെ', 'ഒപ്പം'
        }
        if token in postpositions:
            return 'postposition'

        # Conjunctions
        conjunctions = {'ഉം', 'അല്ലെങ്കിൽ', 'പക്ഷേ', 'എന്നാൽ', 'കാരണം', 'അതുകൊണ്ട്'}
        if token in conjunctions:
            return 'conjunction'

        # Demonstratives
        demonstratives = {'ഈ', 'ആ', 'അത്', 'ഇത്', 'അവ', 'ഇവ'}
        if token in demonstratives:
            return 'demonstrative'

        # Negative particles
        if token in {'ഇല്ല', 'അല്ല', 'വേണ്ട'}:
            return 'negative_particle'

        # Check verb patterns (common endings)
        verb_endings = ['ുന്നു', 'ുന്നു.', 'ുകയാണ്', 'ച്ചു', 'ത്തു', 'യും',
                        'ണം', 'ുക', 'ിക്കുക', 'ാൻ', 'ുമ്പോൾ']
        for ending in verb_endings:
            if token.endswith(ending):
                return 'verb'

        # Check locative case endings
        if token.endswith('ിൽ') or token.endswith('ത്ത്') or token.endswith('ത്തിൽ'):
            return 'noun'

        # Check accusative case
        if token.endswith('യെ') or token.endswith('നെ') or token.endswith('ത്തെ'):
            return 'noun'

        # Check dative case
        if token.endswith('ക്കു') or token.endswith('ക്ക്') or token.endswith('ിന്'):
            return 'noun'

        # Check genitive case
        if token.endswith('ന്റെ') or token.endswith('ുടെ') or token.endswith('ടെ'):
            return 'noun'

        # Check if it's Malayalam script
        if any('\u0D00' <= c <= '\u0D7F' for c in token):
            return 'noun'  # Default for Malayalam words

        return 'other'

    def _generate_fallback_explanation(self, token: str) -> str:
        """Generate a basic explanation for an unknown token."""
        role = self._guess_role(token)
        role_descriptions = self.config.grammatical_roles.get('role_descriptions', {})
        if role in role_descriptions:
            return role_descriptions[role]
        return f"Malayalam word (role: {role.replace('_', ' ')})"

    def _get_fallback_color(self, role: str, complexity: str) -> str:
        """Get color for a given role based on complexity."""
        colors = self.config.get_color_scheme(complexity)
        return colors.get(role, colors.get('other', '#AAAAAA'))
