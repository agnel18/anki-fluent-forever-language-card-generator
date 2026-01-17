# languages/hindi/domain/hi_fallbacks.py
import logging
from typing import Dict, Any
from .hi_config import HiConfig

logger = logging.getLogger(__name__)

class HiFallbacks:
    """Provides fallback responses when parsing fails."""
    
    def __init__(self, config: HiConfig):
        self.config = config
    
    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic fallback analysis."""
        logger.info(f"Creating fallback analysis for sentence: '{sentence}'")
        words = sentence.split()
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
        # Clean the word for better matching
        clean_word = word.strip('।!?.,;:\"\'()[]{}')
        
        # Pronouns
        if clean_word in ['मैं', 'तुम', 'यह', 'वह', 'हम', 'तुम्हें', 'वे', 'उस', 'इन', 'उन', 'मुझ', 'तुझ', 'उसको', 'हमको']:
            return 'pronoun'
        
        # Postpositions (common ones)
        if clean_word in self.config.postpositions:
            return 'postposition'
        
        # Question words
        if clean_word in ['क्या', 'कौन', 'कहाँ', 'कब', 'कैसे', 'क्यों', 'कितना', 'कितने']:
            return 'interrogative'
        
        # Conjunctions
        if clean_word in ['और', 'या', 'पर', 'लेकिन', 'किंतु', 'अतः', 'इसलिए', 'तथा']:
            return 'conjunction'
        
        # Verb endings (basic heuristics)
        if clean_word.endswith(('ता', 'ना', 'या', 'गा', 'गी', 'गे', 'कर', 'करता', 'करती', 'करते')):
            return 'verb'
        
        # Adjective endings
        if clean_word.endswith(('ा', 'ी', 'े', 'ू')) and len(clean_word) > 2:
            return 'adjective'
        
        # Numbers
        if clean_word.isdigit() or clean_word in ['एक', 'दो', 'तीन', 'चार', 'पाँच', 'छह', 'सात', 'आठ', 'नौ', 'दस']:
            return 'numeral'
        
        # Default to noun for most other words
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
            'postposition': 'a word that shows relationship or direction',
            'adverb': 'a word that describes a verb, adjective, or adverb',
            'conjunction': 'a word that connects clauses or sentences',
            'interrogative': 'a question word',
            'numeral': 'a number',
            'other': 'a word in the sentence'
        }
        return role_descriptions.get(role, f'a {role} in Hindi')