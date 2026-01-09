# Arabic Grammar Analyzer
# Comprehensive analyzer for Arabic (العربية)
# Language Family: Afro-Asiatic (Semitic)
# Script Type: abjad (RTL)
# Complexity Rating: high

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, GrammarAnalysis, LanguageConfig

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
        """Generate beginner-level Arabic grammar analysis prompt with contextual meanings"""
        allowed_roles = self.GRAMMATICAL_ROLES['beginner']

        return f"""Analyze this Arabic sentence word by word: {sentence}

Target word: "{target_word}"

For EACH word in the sentence, IN THE ORDER THEY APPEAR IN THE SENTENCE (right to left - RTL), provide:
- word: the exact Arabic word as it appears
- individual_meaning: the {native_language} translation WITH grammatical context (e.g., "the book (noun)", "in (preposition)")
- grammatical_role: EXACTLY ONE category from: {', '.join(allowed_roles)}

CRITICAL REQUIREMENTS:
- WORDS MUST BE LISTED FROM RIGHT TO LEFT as they appear in the Arabic sentence (RTL order)
- EVERY word MUST have individual_meaning with BOTH translation AND grammatical context
- grammatical_role MUST be EXACTLY from the allowed list

Arabic grammatical categories:
- noun: اِسْم (things, people, places - can have definite article ال)
- verb: فِعْل (actions, states - can be perfect or imperfect)
- particle: حَرْف (prepositions, conjunctions, etc.)
- other: anything not fitting above

Examples:
- "الكتاب" → individual_meaning: "the book (definite noun)", grammatical_role: "noun"
- "في" → individual_meaning: "in/inside (preposition)", grammatical_role: "particle"
- "يقرأ" → individual_meaning: "reads (verb)", grammatical_role: "verb"
- "جميل" → individual_meaning: "beautiful (adjective used as noun)", grammatical_role: "noun"

Return JSON format:
{{
  "words": [
    {{
      "word": "الكتاب",
      "individual_meaning": "the book (definite noun)",
      "grammatical_role": "noun"
    }},
    {{
      "word": "يقرأ",
      "individual_meaning": "reads (verb)",
      "grammatical_role": "verb"
    }}
  ]
}}

VALIDATION REQUIREMENTS:
- EVERY word in the sentence MUST have an "individual_meaning" field with context
- individual_meaning MUST include both translation and grammatical function
- Provide explanations in {native_language}
"""

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
        Reorder word explanations to match Arabic RTL reading order.
        Arabic is read right-to-left, so explanations should match this order.
        """
        if not word_explanations or not sentence:
            return word_explanations

        # For Arabic (RTL), we need to reorder explanations to match the reading direction
        # Find position of each word in the sentence and sort from right to left
        positioned_explanations = []

        for explanation in word_explanations:
            if len(explanation) >= 4:
                word = explanation[0]  # word is at index 0
                if word:
                    # Find all occurrences of this word in the sentence
                    positions = []
                    start = 0
                    while True:
                        pos = sentence.find(word, start)
                        if pos == -1:
                            break
                        positions.append(pos)
                        start = pos + 1

                    # Use the first occurrence position
                    # For RTL, we'll sort by position descending (right to left)
                    position = positions[0] if positions else float('inf')
                    positioned_explanations.append((position, explanation))

        # Sort by position in ascending order (RTL reading: left to right in string = right to left in reading)
        positioned_explanations.sort(key=lambda x: x[0])

        # Extract just the explanations
        sorted_explanations = [exp for _, exp in positioned_explanations]

        return sorted_explanations

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map Arabic grammatical roles to color categories"""
        # For Arabic, the color scheme keys match the grammatical roles directly
        return grammatical_role

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Arabic grammatical elements"""
        schemes = {
            "beginner": {
                "noun": "#FFAA00",        # Orange - Things/objects
                "verb": "#44FF44",        # Green - Actions
                "particle": "#FF4444",    # Red - Function words
                "other": "#888888"         # Gray
            },
            "intermediate": {
                "noun": "#FFAA00",        # Orange
                "verb": "#44FF44",        # Green
                "adjective": "#FF44FF",   # Magenta
                "preposition": "#FF4444", # Red
                "conjunction": "#FF4444", # Red
                "interrogative": "#FF4444", # Red
                "negation": "#FF4444",    # Red
                "definite_article": "#FFD700", # Gold
                "pronoun": "#FF69B4",     # Pink
                "other": "#888888"
            },
            "advanced": {
                "noun": "#FFAA00",        # Orange
                "verb": "#44FF44",        # Green
                "adjective": "#FF44FF",   # Magenta
                "preposition": "#FF4444", # Red
                "conjunction": "#FF4444", # Red
                "interrogative": "#FF4444", # Red
                "negation": "#FF4444",    # Red
                "definite_article": "#FFD700", # Gold
                "pronoun": "#FF69B4",     # Pink
                "nominative": "#228B22",  # Forest Green
                "accusative": "#228B22",  # Forest Green
                "genitive": "#228B22",    # Forest Green
                "perfect_verb": "#32CD32", # Lime Green
                "imperfect_verb": "#32CD32", # Lime Green
                "imperative_verb": "#32CD32", # Lime Green
                "active_participle": "#32CD32", # Lime Green
                "passive_participle": "#32CD32", # Lime Green
                "other": "#888888"
            }
        }

        return schemes.get(complexity, schemes["beginner"])

    def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
        """Generate Arabic-specific AI prompt for batch grammar analysis with RTL ordering and contextual meanings"""
        allowed_roles = self.GRAMMATICAL_ROLES.get(complexity, self.GRAMMATICAL_ROLES['intermediate'])
        sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        return f"""Analyze the grammar of these Arabic sentences and provide detailed word-by-word analysis for each one.

Target word: "{target_word}"
Language: Arabic (العربية)
Complexity level: {complexity}
Analysis should be in {native_language}

Sentences to analyze:
{sentences_text}

For EACH word in EVERY sentence, IN THE ORDER THEY APPEAR IN THE SENTENCE (right to left, as Arabic is read from right to left), provide:
- word: the exact Arabic word as it appears in the sentence
- individual_meaning: the {native_language} translation/meaning WITH CONTEXT (MANDATORY - provide detailed, contextual meanings like grammatical function + basic meaning)
- grammatical_role: EXACTLY ONE category from this list: {', '.join(allowed_roles)}

CRITICAL REQUIREMENTS:
- WORDS MUST BE LISTED IN THE EXACT ORDER THEY APPEAR IN THE SENTENCE (right to left for Arabic)
- individual_meaning MUST include BOTH the basic translation AND grammatical context
- grammatical_role MUST be EXACTLY from the allowed list (one word only)
- Do NOT group words by category - list them in sentence reading order

Examples of DETAILED contextual meanings:
- الكتاب: individual_meaning: "the book (definite noun with definite article)", grammatical_role: "noun"
- في: individual_meaning: "in/inside (preposition requiring genitive case)", grammatical_role: "preposition"
- يقرأ: individual_meaning: "reads/is reading (imperfect verb, form I, third person masculine singular)", grammatical_role: "verb"
- الطالب: individual_meaning: "the student (definite noun, nominative case)", grammatical_role: "noun"
- ذلك: individual_meaning: "that (demonstrative pronoun, masculine singular)", grammatical_role: "pronoun"
- جميل: individual_meaning: "beautiful (adjective agreeing with noun in gender/case)", grammatical_role: "adjective"
- ما: individual_meaning: "what (interrogative particle introducing question)", grammatical_role: "interrogative"
- أحب: individual_meaning: "I love (perfect verb, first person singular, form I)", grammatical_role: "verb"

For ADVANCED level, include morphological details:
- Root information (triliteral roots)
- Verb form (ʾabwāb I-X)
- Case markings (ʾiʿrāb: nominative/accusative/genitive)
- Definite article assimilation

Return JSON in this exact format:
{{
  "batch_results": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "words": [
        {{
          "word": "الكتاب",
          "individual_meaning": "the book (definite noun with definite article)",
          "grammatical_role": "noun"
        }},
        {{
          "word": "يقرأ",
          "individual_meaning": "reads (imperfect verb, third person masculine singular)",
          "grammatical_role": "verb"
        }}
      ],
      "word_combinations": [],
      "explanations": {{
        "sentence_structure": "Brief grammatical summary of the sentence",
        "complexity_notes": "Notes about grammatical structures used at {complexity} level"
      }}
    }}
  ]
}}

IMPORTANT:
- Analyze ALL {len(sentences)} sentences
- EVERY word MUST have DETAILED individual_meaning (translation + grammatical context)
- grammatical_role MUST be EXACTLY from the allowed list
- Words must be in RIGHT-TO-LEFT reading order for Arabic
- Include morphological details for advanced analysis
- Return ONLY the JSON object, no additional text
"""

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