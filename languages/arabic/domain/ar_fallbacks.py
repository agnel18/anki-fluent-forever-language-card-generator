"""
Arabic Language Analyzer - Fallback Analysis Component

FALLBACK ANALYSIS STRATEGY:
- When AI analysis fails, provide rule-based analysis
- Use Arabic linguistic patterns for grammatical role detection
- Maintain consistent output format with AI results
- Include confidence scoring and fallback indicators

FALLBACK QUALITY PRINCIPLES:
- Better than nothing: Useful even if not perfect
- Language-aware: Uses real Arabic grammar patterns
- Consistent: Same logic produces same results
- Maintainable: Easy to improve with new patterns
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Import config for type hints
from .ar_config import ArConfig


class ArFallbacks:
    """
    Arabic Fallback Analysis Component

    PURPOSE:
    - Provide rule-based analysis when AI fails
    - Use Arabic-specific linguistic patterns
    - Maintain consistent output structure
    - Track fallback usage for monitoring

    FALLBACK QUALITY PRINCIPLES:
    - Better than nothing: Useful even if not perfect
    - Language-aware: Uses real Arabic grammar patterns
    - Consistent: Same logic produces same results
    - Maintainable: Easy to improve with new patterns
    """

    def __init__(self, config: ArConfig):
        """
        Initialize fallbacks with configuration.

        CONFIGURATION INTEGRATION:
        1. Access to pre-defined word meanings
        2. Common prepositions and particles
        3. Gender, case, and number markers
        4. Pattern definitions for rule-based analysis
        5. Color schemes for consistent output
        """
        self.config = config

    def create_fallback(self, sentence: str, complexity: str) -> Dict[str, Any]:
        """Create a basic fallback analysis for Arabic text."""
        logger.info(f"Creating fallback analysis for sentence: '{sentence}'")

        # Split sentence into words (basic tokenization)
        words = self._tokenize_arabic(sentence)
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

    def _tokenize_arabic(self, sentence: str) -> List[str]:
        """Basic Arabic tokenization."""
        # Remove extra whitespace and split on spaces
        # Note: This is a simple tokenization; real Arabic NLP would use more sophisticated methods
        return sentence.strip().split()

    def _guess_role(self, word: str) -> str:
        """Guess grammatical role based on Arabic word characteristics."""
        # Clean the word for better matching
        clean_word = word.strip('؟!?.,;:\"\'()[]{}')

        # Pronouns (ضمائر)
        pronouns = [
            'أنا', 'أنت', 'أنتِ', 'هو', 'هي', 'نحن', 'أنتم', 'أنتن', 'هم', 'هن',
            'أنا', 'إياي', 'إياك', 'إياه', 'إياها', 'إيانا', 'إياكم', 'إياكما', 'إياهم', 'إياهن',
            'هذا', 'هذه', 'هؤلاء', 'ذاك', 'تلك', 'أولئك'
        ]
        if clean_word in pronouns:
            return 'pronoun'

        # Prepositions (حروف الجر)
        prepositions = [
            'في', 'على', 'من', 'إلى', 'عن', 'مع', 'بعد', 'قبل', 'خلال', 'أثناء',
            'حتى', 'بدون', 'أمام', 'خلف', 'فوق', 'تحت', 'بين', 'عند', 'لدى', 'مع'
        ]
        if clean_word in prepositions:
            return 'preposition'

        # Question words (أدوات الاستفهام)
        question_words = [
            'ما', 'من', 'أين', 'متى', 'كيف', 'لماذا', 'كم', 'أي', 'هل'
        ]
        if clean_word in question_words:
            return 'interrogative'

        # Conjunctions (حروف العطف والربط)
        conjunctions = [
            'و', 'أو', 'لكن', 'بل', 'ثم', 'حتى', 'أما', 'إما', 'إذن', 'لذا', 'ف'
        ]
        if clean_word in conjunctions:
            return 'conjunction'

        # Definite article (ال)
        if clean_word.startswith('ال') and len(clean_word) > 3:
            return 'noun'  # Words with definite article are typically nouns

        # Verb patterns (أفعال) - basic heuristics
        verb_patterns = [
            'فعل', 'يفعل', 'تفعل', 'يفعلان', 'تفعلان', 'يفعلون', 'يفعلن',
            'فعلت', 'فعلنا', 'فعلتم', 'فعلوا', 'فعلن',
            'سأفعل', 'ستفعل', 'سأفعل', 'سنفعل', 'ستفعلون', 'سيفعلن'
        ]
        if any(pattern in clean_word for pattern in verb_patterns) or clean_word.endswith(('ت', 'نا', 'تم', 'وا', 'ن')):
            return 'verb'

        # Adjective patterns (صفات) - basic heuristics
        if clean_word.endswith(('ة', 'ون', 'ين', 'ان', 'ات', 'يات', 'وات')) and len(clean_word) > 2:
            return 'adjective'

        # Numbers (أرقام)
        numbers = [
            'واحد', 'اثنان', 'ثلاثة', 'أربعة', 'خمسة', 'ستة', 'سبعة', 'ثمانية', 'تسعة', 'عشرة',
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
        ]
        if clean_word.isdigit() or clean_word in numbers:
            return 'numeral'

        # Particles (حروف) - negation, etc.
        particles = ['لا', 'لم', 'لن', 'ما', 'إن', 'أن', 'كأن', 'ليت', 'لعل']
        if clean_word in particles:
            return 'particle'

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
            'preposition': 'a word that shows relationship or direction',
            'adverb': 'a word that describes a verb, adjective, or adverb',
            'conjunction': 'a word that connects clauses or sentences',
            'interrogative': 'a question word',
            'numeral': 'a number',
            'particle': 'a grammatical particle',
            'other': 'a word in the sentence'
        }
        return role_descriptions.get(role, f'a {role} in Arabic')