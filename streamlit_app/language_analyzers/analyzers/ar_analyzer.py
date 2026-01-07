# Arabic Grammar Analyzer
# Comprehensive analyzer for Arabic (العربية)
# Language Family: Afro-Asiatic (Semitic)
# Script Type: abjad (RTL)
# Complexity Rating: high

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..base_analyzer import BaseGrammarAnalyzer, GrammarAnalysis, LanguageConfig

logger = logging.getLogger(__name__)

class ArAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Arabic (العربية).

    Key Features: ['root_based_morphology', 'case_marking_i3rab', 'verb_forms_abwab', 'definite_article_assimilation', 'particle_recognition']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "ar"
    LANGUAGE_NAME = "Arabic"

    # Arabic Unicode range for script validation
    ARABIC_UNICODE_RANGE = (0x0600, 0x06FF)

    # Standardized grammatical role enums for consistency across complexity levels
    GRAMMATICAL_ROLES = {
        'beginner': [
            'noun', 'verb', 'particle', 'other'
        ],
        'intermediate': [
            'noun', 'verb', 'adjective', 'preposition', 'conjunction',
            'interrogative', 'negation', 'definite_article', 'pronoun', 'other'
        ],
        'advanced': [
            'noun', 'verb', 'adjective', 'preposition', 'conjunction',
            'interrogative', 'negation', 'definite_article', 'pronoun',
            'nominative', 'accusative', 'genitive', 'perfect_verb', 'imperfect_verb',
            'imperative_verb', 'active_participle', 'passive_participle', 'other'
        ]
    }

    def __init__(self):
        config = LanguageConfig(
            code="ar",
            name="Arabic",
            native_name="العربية",
            family="Afro-Asiatic",
            script_type="abjad",
            complexity_rating="high",
            key_features=['root_based_morphology', 'case_marking_i3rab', 'verb_forms_abwab', 'definite_article_assimilation', 'particle_recognition'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

        # Language-specific patterns and rules
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize Arabic-specific patterns and rules"""

        # Case endings (ḥarakāt - diacritics for iʿrāb)
        self.case_endings = {
            'nominative': r'ُ',  # ḍamma (u)
            'accusative': r'َ',  # fatḥa (a)
            'genitive': r'ِ'     # kasra (i)
        }

        # Definite article assimilation patterns
        self.definite_article_patterns = {
            'original': r'\bال',
            'assimilated_ta': r'\bات',  # ال + ت → ات
            'assimilated_dad': r'\bاض', # ال + ض → اض
            'assimilated_tha': r'\bاظ', # ال + ظ → اظ
            'assimilated_nun': r'\bان'  # ال + ن → ان
        }

        # Common particles (ḥurūf)
        self.particle_patterns = {
            'prepositions': r'\b(فِي|مِن|عَلَى|إِلَى|عَن|مَع|بَيْن|حَتَّى|لِ|كَ|بِ|وَ|فَ|أَو|لَا|لَم|لَن|مَا)\b',
            'conjunctions': r'\b(وَ|فَ|أَو|لَكِن|بَل|أَمَّا|إِمَّا|إِذَا|إِذَن|حَيْثُ|مَعَ|مَعَ أَنَّ|رُبَمَا)\b',
            'interrogatives': r'\b(هَل|أَ|مَا|مَن|مَاذَا|أَيْن|كَيْف|مَتَى|كَم|أَيُّ|أَيَّان)\b',
            'negations': r'\b(لَا|لَم|لَن|مَا|لَيْسَ)\b'
        }

        # Verb form patterns (ʾabwāb - forms I-X)
        self.verb_form_patterns = {
            'form1_perfect': r'\bيَ\w*ُ\b',      # Form I perfect (yafʿulu)
            'form1_imperfect': r'\bيَ\w*ِ\w*ُ\b', # Form I imperfect (yafʿilu)
            'form2': r'\bيُ\w*ِّ\w*ُ\b',         # Form II (yufaʿʿilu)
            'form3': r'\bيُ\w*َا\w*ِ\w*ُ\b',     # Form III (yufāʿilu)
            'form4': r'\bيُ\w*ْ\w*ِ\w*ُ\b',     # Form IV (yuʾfilu)
            'form5': r'\bيَتَ\w*َ\w*ُ\b',       # Form V (yatafaʿʿalu)
            'form6': r'\bيَتَ\w*َا\w*ُ\b',      # Form VI (yatacāʿalu)
            'form7': r'\bيَنْ\w*ِ\w*ُ\b',       # Form VII (yanfilu)
            'form8': r'\bيَ\w*ْتَ\w*ِ\w*ُ\b',   # Form VIII (yaʾtafilu)
            'form9': r'\bيَ\w*ْفَعْلَلُ\b',     # Form IX (yaʾfalallu)
            'form10': r'\bيَسْتَ\w*ِ\w*ُ\b'     # Form X (yastaʾfilu)
        }

        # Root patterns (triliteral roots)
        self.root_patterns = [
            r'\b\w{3}\b',  # Basic triliteral
            r'\b\w{4}\b',  # Quadriliteral
        ]

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str, native_language: str = "English") -> str:
        """Generate AI prompt for Arabic grammar analysis"""
        if complexity == "beginner":
            return self._get_beginner_prompt(sentence, target_word, native_language)
        elif complexity == "intermediate":
            return self._get_intermediate_prompt(sentence, target_word, native_language)
        elif complexity == "advanced":
            return self._get_advanced_prompt(sentence, target_word, native_language)
        else:
            return self._get_beginner_prompt(sentence, target_word, native_language)

    def _get_beginner_prompt(self, sentence: str, target_word: str, native_language: str = "English") -> str:
        """Generate beginner-level Arabic grammar analysis prompt"""
        allowed_roles = self.GRAMMATICAL_ROLES['beginner']

        return f"""Analyze this Arabic sentence word by word: {sentence}

Target word: "{target_word}"

For EACH word in the sentence, IN THE ORDER THEY APPEAR IN THE SENTENCE (right to left, as Arabic is read), provide:
- word: the exact Arabic word as it appears
- individual_meaning: the {native_language} translation/meaning of this word
- grammatical_role: EXACTLY ONE category from: {', '.join(allowed_roles)}

CRITICAL REQUIREMENTS:
- WORDS MUST BE LISTED FROM RIGHT TO LEFT as they appear in the Arabic sentence (RTL order)
- EVERY word MUST have individual_meaning (translation)
- grammatical_role MUST be EXACTLY from the allowed list

Arabic grammatical categories:
- noun: اِسْم (things, people, places)
- verb: فِعْل (actions, states)
- particle: حَرْف (prepositions, conjunctions, etc.)
- other: anything not fitting above

Return JSON format:
{{
  "words": [
    {{
      "word": "الكتاب",
      "individual_meaning": "the book",
      "grammatical_role": "noun"
    }},
    {{
      "word": "في",
      "individual_meaning": "in",
      "grammatical_role": "particle"
    }}
  ]
}}

IMPORTANT: List words in RTL order (right to left) as they appear in Arabic text."""

    def _get_intermediate_prompt(self, sentence: str, target_word: str, native_language: str = "English") -> str:
        """Generate intermediate-level Arabic grammar analysis prompt"""
        allowed_roles = self.GRAMMATICAL_ROLES['intermediate']

        return f"""Analyze this Arabic sentence with intermediate grammar focus: {sentence}

Target word: "{target_word}"

Analyze each word IN THE ORDER THEY APPEAR IN THE SENTENCE (right to left - RTL):

For each word provide:
- word: exact Arabic word
- individual_meaning: {native_language} translation
- grammatical_role: from {', '.join(allowed_roles)}

Focus on:
- Definite article (ال) and assimilation
- Prepositions and their case requirements
- Basic verb forms and patterns
- Question particles

CRITICAL: WORDS MUST BE LISTED FROM RIGHT TO LEFT (RTL order) as they appear in Arabic.

Return JSON:
{{
  "words": [
    {{
      "word": "الطالب",
      "individual_meaning": "the student",
      "grammatical_role": "noun"
    }}
  ]
}}"""

    def _get_advanced_prompt(self, sentence: str, target_word: str, native_language: str = "English") -> str:
        """Generate advanced-level Arabic grammar analysis prompt"""
        allowed_roles = self.GRAMMATICAL_ROLES['advanced']

        return f"""Perform advanced morphological analysis of this Arabic sentence: {sentence}

Target word: "{target_word}"

Analyze each word IN RTL ORDER (right to left) with focus on:
- Root-based morphology (triliteral roots)
- Case markings (iʿrāb - nominative, accusative, genitive)
- Verb forms (ʾabwāb I-X)
- Complex particles and their grammatical functions

For each word:
- word: exact Arabic word
- individual_meaning: {native_language} translation
- grammatical_role: from {', '.join(allowed_roles)}

CRITICAL: WORDS MUST BE LISTED FROM RIGHT TO LEFT as they appear in Arabic text.

Include analysis of:
- Case endings (ḍamma, fatḥa, kasra)
- Definite article assimilation patterns
- Verb conjugation patterns
- Root extraction where applicable

Return JSON with comprehensive analysis."""

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """
        Parse AI response into standardized Arabic grammar analysis format.
        Handles RTL word ordering for Arabic script.
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed = json.loads(json_str)
                parsed['sentence'] = sentence
                return self._transform_to_standard_format(parsed, complexity, sentence)

            # Try direct JSON parsing
            parsed = json.loads(ai_response)
            parsed['sentence'] = sentence
            return self._transform_to_standard_format(parsed, complexity, sentence)

        except Exception as e:
            logger.error(f"Failed to parse Arabic grammar response: {e}")
            return self._create_fallback_parse(ai_response, sentence)

    def _transform_to_standard_format(self, parsed_data: Dict[str, Any], complexity: str = 'beginner', sentence: str = '') -> Dict[str, Any]:
        """Transform Arabic analyzer output to standard BaseGrammarAnalyzer format"""
        try:
            words = parsed_data.get('words', [])
            explanations = parsed_data.get('explanations', {})

            # Transform words into elements grouped by grammatical role
            elements = {}
            for word_data in words:
                grammatical_role = word_data.get('grammatical_role', 'other')
                if grammatical_role not in elements:
                    elements[grammatical_role] = []
                elements[grammatical_role].append(word_data)

            # Create word_explanations for HTML coloring
            word_explanations = []
            colors = self.get_color_scheme(complexity)

            for word_data in words:
                word = word_data.get('word', '')
                grammatical_role = word_data.get('grammatical_role', 'other')
                individual_meaning = word_data.get('individual_meaning', '')
                category = self._map_grammatical_role_to_category(grammatical_role)
                color = colors.get(category, '#888888')

                explanation = individual_meaning if individual_meaning else grammatical_role
                word_explanations.append([word, grammatical_role, color, explanation])

            # Reorder for RTL display
            word_explanations = self._reorder_explanations_for_rtl(sentence, word_explanations)

            return {
                'elements': elements,
                'explanations': explanations,
                'word_explanations': word_explanations,
                'sentence': parsed_data.get('sentence', sentence)
            }

        except Exception as e:
            logger.error(f"Failed to transform Arabic analysis data: {e}")
            return {
                'elements': {},
                'explanations': {'error': 'Data transformation failed'},
                'word_explanations': [],
                'sentence': parsed_data.get('sentence', sentence)
            }

    def _reorder_explanations_for_rtl(self, sentence: str, word_explanations: List) -> List:
        """
        Reorder word explanations for RTL Arabic display.
        Arabic is read right-to-left, so explanations should match this order.
        """
        if not word_explanations:
            return word_explanations

        # For Arabic (RTL), we need to reverse the order to match reading direction
        # This ensures explanations appear in the order words are encountered when reading Arabic
        return list(reversed(word_explanations))

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map Arabic grammatical roles to color categories"""
        mapping = {
            'noun': 'nouns',
            'verb': 'verbs',
            'adjective': 'adjectives',
            'preposition': 'particles',
            'conjunction': 'particles',
            'interrogative': 'particles',
            'negation': 'particles',
            'definite_article': 'articles',
            'pronoun': 'pronouns',
            'nominative': 'cases',
            'accusative': 'cases',
            'genitive': 'cases',
            'perfect_verb': 'verbs',
            'imperfect_verb': 'verbs',
            'imperative_verb': 'verbs',
            'active_participle': 'participles',
            'passive_participle': 'participles'
        }
        return mapping.get(grammatical_role, 'other')

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Arabic grammatical elements"""
        schemes = {
            "beginner": {
                "nouns": "#FFAA00",        # Orange - Things/objects
                "verbs": "#44FF44",        # Green - Actions
                "particles": "#FF4444",    # Red - Function words
                "other": "#888888"         # Gray
            },
            "intermediate": {
                "nouns": "#FFAA00",        # Orange
                "verbs": "#44FF44",        # Green
                "adjectives": "#FF44FF",   # Magenta
                "particles": "#FF4444",    # Red
                "articles": "#FFD700",     # Gold
                "pronouns": "#FF69B4",     # Pink
                "other": "#888888"
            },
            "advanced": {
                "nouns": "#FFAA00",        # Orange
                "verbs": "#44FF44",        # Green
                "adjectives": "#FF44FF",   # Magenta
                "particles": "#FF4444",    # Red
                "articles": "#FFD700",     # Gold
                "pronouns": "#FF69B4",     # Pink
                "cases": "#228B22",        # Forest Green
                "participles": "#32CD32",  # Lime Green
                "other": "#888888"
            }
        }

        return schemes.get(complexity, schemes["beginner"])

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Arabic grammar analysis quality (85% threshold required)"""
        try:
            words = parsed_data.get('word_explanations', [])
            elements = parsed_data.get('elements', {})

            # Basic checks
            has_words = len(words) > 0
            has_elements = len(elements) > 0

            # Check Arabic script usage
            arabic_chars = sum(1 for char in original_sentence if self.ARABIC_UNICODE_RANGE[0] <= ord(char) <= self.ARABIC_UNICODE_RANGE[1])
            arabic_ratio = arabic_chars / len(original_sentence) if original_sentence else 0

            # Word coverage
            sentence_words = original_sentence.split()
            analyzed_words = len(words)
            coverage = analyzed_words / len(sentence_words) if sentence_words else 0

            # Calculate confidence
            base_score = 0.8 if has_words else 0.5
            arabic_bonus = 0.1 if arabic_ratio > 0.5 else 0
            coverage_bonus = coverage * 0.1

            confidence = min(base_score + arabic_bonus + coverage_bonus, 1.0)
            return confidence

        except Exception as e:
            logger.error(f"Arabic validation failed: {e}")
            return 0.5

    def _create_fallback_parse(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Create fallback analysis when parsing fails"""
        return {
            'elements': {},
            'explanations': {'error': 'Analysis temporarily unavailable'},
            'word_explanations': [],
            'sentence': sentence
        }