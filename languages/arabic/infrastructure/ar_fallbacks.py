# Arabic Fallbacks - Infrastructure Component
# Provides fallback responses for Arabic grammar analysis

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ArabicFallbacks:
    """
    Provides fallback responses when Arabic parsing fails.
    """

    def __init__(self):
        self.fallback_data = {
            'noun': {'role': 'noun', 'meaning': 'Basic noun (اسم)', 'confidence': 'low'},
            'verb': {'role': 'verb', 'meaning': 'Basic verb (فعل)', 'confidence': 'low'},
            'particle': {'role': 'particle', 'meaning': 'Basic particle (حرف)', 'confidence': 'low'}
        }

    def get_fallback_analysis(self, word: str) -> Dict[str, Any]:
        """Get fallback analysis for a word"""
        # Simple fallback based on Arabic character patterns
        if any(char in 'فعل' for char in word):
            return self.fallback_data['verb']
        elif len(word) <= 3 and word in ['من', 'إلى', 'على', 'في', 'مع']:
            return self.fallback_data['particle']
        else:
            return self.fallback_data['noun']