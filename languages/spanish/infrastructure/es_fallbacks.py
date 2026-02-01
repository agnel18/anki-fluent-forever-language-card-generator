# Spanish Fallbacks
# Provides fallback mechanisms for Spanish grammar analysis
# Handles parsing failures and creates basic analyses

import logging
import re
from typing import Dict, List, Any, Optional
from ..domain.es_config import EsConfig

logger = logging.getLogger(__name__)

class EsFallbacks:
    """
    Fallback mechanisms for Spanish grammar analysis.
    Creates basic analyses when AI parsing fails.
    """

    def __init__(self, config: EsConfig):
        self.config = config

    def create_fallback(self, sentence: str, complexity: str, target_word: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a basic fallback analysis for Spanish sentences.
        Used when AI response parsing fails.
        """
        logger.info(f"Creating Spanish fallback analysis for: {sentence}")

        # Split sentence into words (basic tokenization)
        words = self._tokenize_spanish(sentence)

        fallback_words = []
        for word in words:
            role = self._classify_spanish_word(word)
            meaning = self._create_fallback_meaning(word, role, sentence)

            fallback_words.append({
                "word": word,
                "grammatical_role": role,
                "meaning": meaning
            })

        return {
            "words": fallback_words,
            "overall_analysis": {
                "sentence_structure": "Basic Spanish sentence structure (fallback analysis)",
                "key_features": "Analysis generated due to parsing failure"
            },
            "confidence": 0.3  # Low confidence for fallback
        }

    def _tokenize_spanish(self, sentence: str) -> List[str]:
        """Basic tokenization for Spanish text"""
        # Remove extra whitespace and split on spaces
        # Note: Spanish doesn't have complex tokenization issues like Chinese
        return sentence.strip().split()

    def _classify_spanish_word(self, word: str) -> str:
        """Classify a Spanish word into basic grammatical categories"""
        word_lower = word.lower().strip('.,!?;:"')

        # Remove punctuation for classification
        clean_word = re.sub(r'[^\w\s]', '', word_lower)

        # Articles/Determiners
        if clean_word in ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'este', 'esta', 'ese', 'esa', 'aquel', 'aquella']:
            return 'determiner'

        # Prepositions
        if clean_word in ['a', 'de', 'en', 'con', 'por', 'para', 'sin', 'sobre', 'desde', 'hasta', 'durante', 'entre', 'contra']:
            return 'preposition'

        # Conjunctions
        if clean_word in ['y', 'o', 'pero', 'que', 'como', 'si', 'cuando', 'donde', 'porque', 'aunque', 'mientras', 'sin embargo']:
            return 'conjunction'

        # Pronouns
        if clean_word in ['yo', 'tú', 'él', 'ella', 'nosotros', 'nosotras', 'ellos', 'ellas', 'me', 'te', 'se', 'lo', 'la', 'los', 'las', 'le', 'les', 'mi', 'tu', 'su', 'nuestro', 'vuestro']:
            return 'pronoun'

        # Common verbs (basic check for conjugation patterns)
        if self._is_spanish_verb(clean_word):
            return 'verb'

        # Adjectives (common endings)
        if self._is_spanish_adjective(clean_word):
            return 'adjective'

        # Adverbs (common endings or known adverbs)
        if clean_word in ['muy', 'más', 'menos', 'aquí', 'allí', 'ahora', 'siempre', 'nunca', 'también', 'tampoco'] or clean_word.endswith(('mente', 'mente')):
            return 'adverb'

        # Default to noun
        return 'noun'

    def _is_spanish_verb(self, word: str) -> bool:
        """Check if word appears to be a Spanish verb"""
        # Common verb endings and conjugations
        verb_patterns = [
            r'ar$', r'er$', r'ir$',  # infinitives
            r'o$', r'as$', r'a$', r'amos$', r'áis$', r'an$',  # present indicative
            r'é$', r'aste$', r'ó$', r'ampos$', r'asteis$', r'aron$',  # preterite
            r'aba$', r'abas$', r'aba$', r'ábamos$', r'abais$', r'aban$',  # imperfect
        ]

        return any(re.search(pattern, word) for pattern in verb_patterns)

    def _is_spanish_adjective(self, word: str) -> bool:
        """Check if word appears to be a Spanish adjective"""
        # Common adjective endings
        adj_endings = ['o', 'a', 'os', 'as', 'e', 'es', 'ante', 'ente']

        # Check for adjective endings
        if any(word.endswith(ending) for ending in adj_endings):
            return True

        # Common adjectives
        common_adjs = ['bueno', 'buena', 'malo', 'mala', 'grande', 'pequeño', 'pequeña', 'bonito', 'bonita', 'feo', 'fea']
        return word in common_adjs

    def _create_fallback_meaning(self, word: str, role: str, sentence: str) -> str:
        """Create a basic meaning explanation for fallback"""
        # Simple fallback format
        return f"{word} ({role}): {word}; word in the sentence"