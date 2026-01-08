# Spanish Grammar Analyzer
# Auto-generated analyzer for Spanish (español)
# Language Family: Indo-European
# Script Type: alphabetic
# Complexity Rating: medium

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..family_base_analyzers.indo_european_analyzer import IndoEuropeanAnalyzer
from ..base_analyzer import GrammarAnalysis, LanguageConfig

logger = logging.getLogger(__name__)

class EsAnalyzer(IndoEuropeanAnalyzer):
    """
    Grammar analyzer for Spanish (español).

    Key Features: ['verb_conjugation', 'gender_agreement', 'noun_adjective_agreement', 'clitic_pronouns', 'ser_estar_distinction']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "es"
    LANGUAGE_NAME = "Spanish"

    # Standardized grammatical role enums for consistency across complexity levels
    GRAMMATICAL_ROLES = {
        'beginner': [
            'noun', 'adjective', 'verb', 'adverb', 'pronoun', 'article',
            'preposition', 'conjunction', 'interjection', 'auxiliary', 'other'
        ],
        'intermediate': [
            'noun', 'adjective', 'verb', 'adverb', 'pronoun', 'personal_pronoun',
            'demonstrative_pronoun', 'possessive_pronoun', 'reflexive_pronoun',
            'article', 'preposition', 'conjunction', 'interjection', 'auxiliary',
            'numeral', 'relative_pronoun', 'interrogative_pronoun', 'other'
        ],
        'advanced': [
            'noun', 'adjective', 'verb', 'adverb', 'pronoun', 'personal_pronoun',
            'demonstrative_pronoun', 'possessive_pronoun', 'reflexive_pronoun',
            'article', 'preposition', 'conjunction', 'interjection', 'auxiliary',
            'numeral', 'relative_pronoun', 'interrogative_pronoun', 'indefinite_pronoun',
            'clitic', 'gerund', 'past_participle', 'infinitive', 'other'
        ]
    }

    def __init__(self):
        config = LanguageConfig(
            code="es",
            name="Spanish",
            native_name="español",
            family="Indo-European",
            script_type="alphabetic",
            complexity_rating="medium",
            key_features=['verb_conjugation', 'gender_agreement', 'noun_adjective_agreement', 'clitic_pronouns', 'ser_estar_distinction'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

        # Language-specific patterns and rules
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize language-specific patterns and rules for Spanish"""
        # Verb conjugation patterns (conjugaciones verbales)
        self.verb_endings = {
            'present_indicative': {
                'ar': ['o', 'as', 'a', 'amos', 'áis', 'an'],
                'er': ['o', 'es', 'e', 'emos', 'éis', 'en'],
                'ir': ['o', 'es', 'e', 'imos', 'ís', 'en']
            },
            'preterite': {
                'ar': ['é', 'aste', 'ó', 'amos', 'asteis', 'aron'],
                'er': ['í', 'iste', 'ió', 'imos', 'isteis', 'ieron'],
                'ir': ['í', 'iste', 'ió', 'imos', 'isteis', 'ieron']
            },
            'imperfect': {
                'ar': ['aba', 'abas', 'aba', 'ábamos', 'abais', 'aban'],
                'er': ['ía', 'ías', 'ía', 'íamos', 'íais', 'ían'],
                'ir': ['ía', 'ías', 'ía', 'íamos', 'íais', 'ían']
            }
        }

        # Gender markers (marcadores de género)
        self.masculine_markers = [
            r'\b(?:el|los|un|unos)\b',  # Masculine articles
            r'\b\w*o\b(?!\w)',  # Words ending in -o
            r'\b\w*ón\b',  # Augmentative -ón
        ]
        self.feminine_markers = [
            r'\b(?:la|las|una|unas)\b',  # Feminine articles
            r'\b\w*a\b(?!\w)',  # Words ending in -a
            r'\b\w*ción\b',  # -ción endings
            r'\b\w*sión\b',  # -sión endings
        ]

        # Clitic pronoun patterns (pronombres clíticos)
        self.clitic_patterns = [
            r'\b(?:me|te|se|nos|os|lo|la|los|las|le|les)\b'
        ]

        # Ser vs Estar distinction patterns
        self.ser_patterns = [
            r'\b(?:soy|eres|es|somos|sois|son)\b',  # Ser conjugations
            r'\bser\b'  # Infinitive
        ]
        self.estar_patterns = [
            r'\b(?:estoy|estás|está|estamos|estáis|están)\b',  # Estar conjugations
            r'\bestar\b'  # Infinitive
        ]

        # Preposition patterns (preposiciones)
        self.preposition_patterns = [
            r'\b(?:a|ante|bajo|cabe|con|contra|de|desde|durante|en|entre|hacia|hasta|mediante|para|por|según|sin|sobre|tras|versus|durante)\b'
        ]

        # Article patterns (artículos)
        self.definite_articles = [r'\b(?:el|la|los|las)\b']
        self.indefinite_articles = [r'\b(?:un|una|unos|unas)\b']

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str, native_language: str = "English") -> str:
        """Generate AI prompt for Spanish grammar analysis"""
        if complexity == "beginner":
            return self._get_beginner_prompt(sentence, target_word, native_language)
        elif complexity == "intermediate":
            return self._get_intermediate_prompt(sentence, target_word, native_language)
        elif complexity == "advanced":
            return self._get_advanced_prompt(sentence, target_word, native_language)
        else:
            return self._get_beginner_prompt(sentence, target_word, native_language)

    def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
        """Generate Spanish-specific AI prompt for batch grammar analysis"""
        allowed_roles = self.GRAMMATICAL_ROLES.get(complexity, self.GRAMMATICAL_ROLES['intermediate'])
        sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        return f"""Analyze the grammar of these Spanish sentences and provide detailed word-by-word analysis for each one.

Target word: "{target_word}"
Language: Spanish
Complexity level: {complexity}
Analysis should be in {native_language}

Sentences to analyze:
{sentences_text}

For EACH word in EVERY sentence, IN THE ORDER THEY APPEAR IN THE SENTENCE (left to right), provide:
- word: the exact word as it appears in the sentence
- individual_meaning: the English translation/meaning of this specific word (MANDATORY - do not leave empty)
- grammatical_role: EXACTLY ONE category from this list: {', '.join(allowed_roles)}

CRITICAL REQUIREMENTS:
- individual_meaning MUST be provided for EVERY word
- grammatical_role MUST be EXACTLY one word from the allowed list (no spaces, no prefixes, no suffixes)
- WORDS MUST BE LISTED IN THE EXACT ORDER THEY APPEAR IN THE SENTENCE (left to right, no grouping by category)
- Examples of correct grammatical_role:
  - "noun" (not "common noun" or "n noun")
  - "verb" (not "v verb" or "main verb")
  - "article" (not "definite article")
  - "preposition" (not "prep" or "prepositional")
  - "auxiliary" (not "aux verb" or "auxiliary verb")
  - "other" for anything not in the list

Examples:
- "casa" → individual_meaning: "house", grammatical_role: "noun"
- "la" → individual_meaning: "the", grammatical_role: "article"
- "es" → individual_meaning: "is", grammatical_role: "verb"
- "en" → individual_meaning: "in", grammatical_role: "preposition"

Return JSON in this exact format:
{{
  "batch_results": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "words": [
        {{
          "word": "casa",
          "individual_meaning": "house",
          "grammatical_role": "noun"
        }},
        {{
          "word": "la",
          "individual_meaning": "the",
          "grammatical_role": "article"
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
- EVERY word MUST have individual_meaning (English translation)
- grammatical_role MUST be EXACTLY from the allowed list (one word only)
- Return ONLY the JSON object, no additional text
"""

    def _get_beginner_prompt(self, sentence: str, target_word: str, native_language: str = "English") -> str:
        """Generate beginner-level grammar analysis prompt with condensed descriptions"""
        allowed_roles = self.GRAMMATICAL_ROLES['beginner']
        roles_list = "\n- ".join(allowed_roles)

        base_prompt = f"""Analyze this ENTIRE Spanish sentence WORD BY WORD: SENTENCE_PLACEHOLDER

For EACH word, provide:
- Individual meaning (English translation)
- Grammatical role (use EXACTLY ONE from this list: {', '.join(allowed_roles)})

SPANISH GRAMMATICAL ROLES - Use these exact ENUM values:

{roles_list}

Pay special attention to: TARGET_PLACEHOLDER

Return JSON with word-by-word analysis:
{{
  "words": [
    {{
      "word": "la",
      "individual_meaning": "the",
      "grammatical_role": "article"
    }},
    {{
      "word": "casa",
      "individual_meaning": "house",
      "grammatical_role": "noun"
    }}
  ]
}}

VALIDATION REQUIREMENTS:
- EVERY word in the sentence MUST have an "individual_meaning" field
- individual_meaning MUST be the actual English meaning/translation of the word (not grammatical labels)
- If you cannot provide a meaning, use the word's basic dictionary definition
- Do NOT leave individual_meaning empty or use grammatical roles as meanings
- Examples: "perro" → "dog", "corre" → "runs/is running", "es" → "is", "en" → "in"
- Provide explanations in {native_language}
"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str, native_language: str = "English") -> str:
        """Generate intermediate-level grammar analysis prompt with condensed descriptions"""
        allowed_roles = self.GRAMMATICAL_ROLES['intermediate']
        base_prompt = f"""Analyze this Spanish sentence with INTERMEDIATE grammar focus: SENTENCE_PLACEHOLDER

Provide detailed analysis including:
- Verb conjugations and tense/aspect/mood (person, number, tense)
- Gender and number agreement patterns (article-adjective-noun agreement)
- Pronoun usage and clitic placement (me/te/se object pronouns)
- Ser vs Estar distinction (permanent vs temporary states)
- Prepositional phrases and contractions (al = a+el, del = de+el)

IMPORTANT: Use specific grammatical categories from this list: {', '.join(allowed_roles)}

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with comprehensive analysis:
{{
  "words": [
    {{
      "word": "habla",
      "individual_meaning": "speaks/is speaking",
      "grammatical_role": "verb"
    }},
    {{
      "word": "la",
      "individual_meaning": "the",
      "grammatical_role": "article"
    }}
  ]
}}
"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str, native_language: str = "English") -> str:
        """Generate advanced-level grammar analysis prompt with condensed descriptions"""
        allowed_roles = self.GRAMMATICAL_ROLES['advanced']

        base_prompt = f"""Perform ADVANCED morphological and syntactic analysis of this Spanish sentence: SENTENCE_PLACEHOLDER

Analyze complex features including:
- Subjunctive mood usage (doubt, emotion, volition)
- Compound tenses (haber + past participle for perfect)
- Passive voice constructions (ser + past participle)
- Complex clitic climbing and pronoun placement
- Por vs Para distinction (cause vs destination/purpose)
- Imperfect vs Preterite aspectual choice
- Relative clauses and complex subordination

IMPORTANT: Use specific grammatical categories from this list: {', '.join(allowed_roles)}
- personal_pronoun: yo (I), tú (you informal), él/ella (he/she), nosotros (we), vosotros (you plural informal), ellos/ellas (they)
- demonstrative_pronoun: este/esta (this), ese/esa (that), aquel/aquella (that over there)
- possessive_pronoun: mío/mía (mine), tuyo/tuya (yours), suyo/suya (his/hers/its/yours formal)
- reflexive_pronoun: me (myself), te (yourself), se (himself/herself/itself/yourself formal), nos (ourselves), os (yourselves), se (themselves)
- clitic: me/te/se/nos/os (indirect objects), lo/la/los/las (direct objects), le/les (indirect formal)

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with advanced grammatical analysis:
{{
  "words": [
    {{
      "word": "hubiera",
      "individual_meaning": "had (pluperfect subjunctive)",
      "grammatical_role": "auxiliary"
    }},
    {{
      "word": "hablado",
      "individual_meaning": "spoken",
      "grammatical_role": "past_participle"
    }}
  ]
}}
"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def validate_analysis(self, analysis_result: Dict[str, Any], sentence: str, complexity: str = "intermediate") -> Tuple[bool, float, str]:
        """
        Validate Spanish grammar analysis with language-specific checks.

        Returns:
            Tuple[bool, float, str]: (is_valid, confidence_score, feedback_message)
        """
        try:
            words = analysis_result.get('words', [])
            if not words:
                return False, 0.0, "No words found in analysis"

            # Basic validation
            total_words = len([w for w in sentence.split() if w.strip()])
            analyzed_words = len(words)

            if analyzed_words < total_words * 0.8:  # Allow 20% tolerance for punctuation/compound words
                return False, 0.3, f"Analysis incomplete: {analyzed_words}/{total_words} words analyzed"

            # Spanish-specific validation checks
            validation_score = 0.0
            issues = []

            # Check 1: Gender agreement patterns
            gender_agreement_score = self._validate_gender_agreement(words)
            validation_score += gender_agreement_score * 0.3

            # Check 2: Verb conjugation patterns
            verb_conjugation_score = self._validate_verb_conjugations(words)
            validation_score += verb_conjugation_score * 0.3

            # Check 3: Article-noun agreement
            article_agreement_score = self._validate_article_noun_agreement(words)
            validation_score += article_agreement_score * 0.2

            # Check 4: Ser vs Estar usage
            ser_estar_score = self._validate_ser_estar_usage(words)
            validation_score += ser_estar_score * 0.2

            # Ensure minimum confidence threshold
            confidence = max(0.1, min(1.0, validation_score))

            # Provide feedback
            if confidence >= 0.85:
                feedback = "High confidence analysis with proper Spanish grammatical patterns"
            elif confidence >= 0.7:
                feedback = "Good analysis with minor agreement or conjugation issues"
            else:
                feedback = "Analysis needs improvement in Spanish grammatical agreement patterns"

            return True, confidence, feedback

        except Exception as e:
            logger.error(f"Spanish validation error: {e}")
            return False, 0.1, f"Validation failed: {str(e)}"

    def _validate_gender_agreement(self, words: List[Dict[str, Any]]) -> float:
        """Validate gender agreement between articles, adjectives, and nouns"""
        score = 1.0  # Start with perfect score

        # Simple pattern-based validation
        for i, word_data in enumerate(words):
            word = word_data.get('word', '').lower()
            role = word_data.get('grammatical_role', '')

            # Check for obvious gender mismatches
            if role == 'article':
                if word in ['el', 'los', 'un', 'unos']:  # Masculine articles
                    # Look ahead for noun/adjective
                    for j in range(i+1, min(i+3, len(words))):
                        next_word = words[j].get('word', '').lower()
                        next_role = words[j].get('grammatical_role', '')
                        if next_role in ['noun', 'adjective']:
                            # Check for feminine endings with masculine articles (error)
                            if next_word.endswith(('a', 'as', 'ción', 'sión')) and not next_word.endswith(('o', 'os', 'ón')):
                                score -= 0.2
                                break
                elif word in ['la', 'las', 'una', 'unas']:  # Feminine articles
                    # Look ahead for noun/adjective
                    for j in range(i+1, min(i+3, len(words))):
                        next_word = words[j].get('word', '').lower()
                        next_role = words[j].get('grammatical_role', '')
                        if next_role in ['noun', 'adjective']:
                            # Check for masculine endings with feminine articles (error)
                            if next_word.endswith(('o', 'os', 'ón')) and not next_word.endswith(('a', 'as', 'ción', 'sión')):
                                score -= 0.2
                                break

        return max(0.0, score)

    def _validate_verb_conjugations(self, words: List[Dict[str, Any]]) -> float:
        """Validate verb conjugation patterns"""
        score = 1.0

        for word_data in words:
            word = word_data.get('word', '').lower()
            role = word_data.get('grammatical_role', '')

            if role == 'verb':
                # Check for irregular verb forms that should be caught
                irregular_indicators = ['soy', 'estoy', 'voy', 'hago', 'digo', 'tengo', 'vengo']
                if word in irregular_indicators:
                    # These are correctly irregular, no penalty
                    continue
                # Could add more sophisticated conjugation validation here
                # For now, basic check that it doesn't end with impossible combinations

        return score

    def _validate_article_noun_agreement(self, words: List[Dict[str, Any]]) -> float:
        """Validate agreement between articles and nouns"""
        score = 1.0

        i = 0
        while i < len(words) - 1:
            current_word = words[i].get('word', '').lower()
            current_role = words[i].get('grammatical_role', '')
            next_word = words[i+1].get('word', '').lower()
            next_role = words[i+1].get('grammatical_role', '')

            if current_role == 'article' and next_role == 'noun':
                # Check number agreement
                if current_word in ['el', 'la', 'un', 'una']:  # Singular articles
                    if next_word.endswith('s') and not next_word.endswith(('as', 'es', 'is', 'os', 'us')):
                        # Plural noun with singular article - potential issue
                        score -= 0.1
                elif current_word in ['los', 'las', 'unos', 'unas']:  # Plural articles
                    if not next_word.endswith('s'):
                        # Singular noun with plural article - potential issue
                        score -= 0.1

            i += 1

        return max(0.0, score)

    def _validate_ser_estar_usage(self, words: List[Dict[str, Any]]) -> float:
        """Validate appropriate usage of ser vs estar"""
        score = 1.0

        for word_data in words:
            word = word_data.get('word', '').lower()
            role = word_data.get('grammatical_role', '')

            if role == 'verb' and word in ['ser', 'estar', 'soy', 'eres', 'es', 'somos', 'sois', 'son', 'estoy', 'estás', 'está', 'estamos', 'estáis', 'están']:
                # Basic check - could be enhanced with context analysis
                # For now, just ensure it's recognized as a verb
                continue

        return score

    def _reorder_explanations_by_sentence_position(self, sentence: str, word_explanations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Reorder word explanations to match the order they appear in the sentence.
        Spanish uses left-to-right (LTR) word order like English.

        This ensures grammar explanations are displayed in sentence word order for optimal user experience.
        """
        if not word_explanations:
            return word_explanations

        # Create mapping of words to their positions in the sentence
        word_positions = {}
        sentence_words = sentence.split()

        for idx, sent_word in enumerate(sentence_words):
            # Clean the word for matching (remove punctuation)
            clean_sent_word = re.sub(r'[^\w\s]', '', sent_word).lower()
            word_positions[clean_sent_word] = idx

        # Sort explanations by their position in the sentence
        sorted_explanations = []
        for explanation in word_explanations:
            word = explanation.get('word', '').lower()
            # Clean word for matching
            clean_word = re.sub(r'[^\w\s]', '', word)
            position = word_positions.get(clean_word, 999)  # Default high position for unmatched words
            sorted_explanations.append((position, explanation))

        # Sort by position and return just the explanations
        sorted_explanations.sort(key=lambda x: x[0])
        return [exp for pos, exp in sorted_explanations]
        try:
            # Try to extract JSON from markdown code blocks first
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1)
                    parsed = json.loads(json_str)
                    parsed['sentence'] = sentence
                    logger.info(f"Spanish analyzer parsed JSON from markdown successfully: {len(parsed.get('words', []))} words")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Spanish analyzer (markdown): {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

            # Try to extract JSON from response - look for JSON object after text
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    parsed = json.loads(json_str)
                    parsed['sentence'] = sentence
                    logger.info(f"Spanish analyzer parsed JSON successfully: {len(parsed.get('words', []))} words")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Spanish analyzer: {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

            # Try direct JSON parsing
            try:
                parsed = json.loads(ai_response)
                parsed['sentence'] = sentence
                logger.info(f"Spanish analyzer direct JSON parse successful: {len(parsed.get('words', []))} words")
                return self._transform_to_standard_format(parsed, complexity)
            except json.JSONDecodeError as e:
                logger.error(f"Direct JSON parse error in Spanish analyzer: {e}")
                logger.error(f"Raw AI response: {ai_response[:500]}...")

            # Fallback: extract structured information from text
            logger.warning("Spanish analyzer falling back to text parsing")
            return self._parse_text_response(ai_response, sentence)

        except Exception as e:
            logger.error(f"Failed to parse {self.language_name} grammar response: {e}")
            return self._create_fallback_parse(ai_response, sentence)

    def _transform_to_standard_format(self, parsed_data: Dict[str, Any], complexity: str = 'beginner') -> Dict[str, Any]:
        """Transform Spanish analyzer output to standard BaseGrammarAnalyzer format"""
        try:
            # Extract original data
            words = parsed_data.get('words', [])
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            logger.info(f"Spanish analyzer transforming {len(words)} words")
            if words:
                sample_roles = [w.get('grammatical_role', 'MISSING') for w in words[:3]]
                logger.info(f"Sample grammatical roles: {sample_roles}")

            # Transform words into elements grouped by grammatical role
            elements = {}

            # Group words by their grammatical role
            for word_data in words:
                grammatical_role = word_data.get('grammatical_role', 'other')
                logger.debug(f"Processing word '{word_data.get('word', 'UNKNOWN')}' with role '{grammatical_role}'")
                if grammatical_role not in elements:
                    elements[grammatical_role] = []
                elements[grammatical_role].append(word_data)

            # Add word combinations as a special category
            if word_combinations:
                elements['word_combinations'] = word_combinations

            # Create word_explanations for HTML coloring: [word, pos, color, explanation]
            word_explanations = []
            colors = self.get_color_scheme(complexity)  # Use the actual complexity level

            logger.info(f"DEBUG Spanish Transform - Color scheme for complexity '{complexity}': {colors}")

            for word_data in words:
                word = word_data.get('word', '')
                grammatical_role = word_data.get('grammatical_role', 'other')
                individual_meaning = word_data.get('individual_meaning', '')
                pronunciation = word_data.get('pronunciation', '')
                
                # Ensure grammatical_role is a string
                if not isinstance(grammatical_role, str):
                    logger.warning(f"grammatical_role is not a string: {grammatical_role} (type: {type(grammatical_role)}), defaulting to 'other'")
                    grammatical_role = 'other'
                category = self._map_grammatical_role_to_category(grammatical_role)
                color = colors.get(category, '#888888')
                
                # Override with AI-provided color if available and standardize it
                ai_color = word_data.get('color')
                if ai_color:
                    color = self._standardize_color(ai_color, category)
                
                logger.info(f"DEBUG Spanish Transform - Word: '{word}', Role: '{grammatical_role}', Category: '{category}', Color: '{color}'")
                
                # Create explanation text from available data
                explanation_parts = []
                if individual_meaning:
                    explanation_parts.append(individual_meaning)
                if pronunciation:
                    explanation_parts.append(f"({pronunciation})")
                
                explanation = ", ".join(explanation_parts) if explanation_parts else f"{grammatical_role}"
                
                word_explanations.append([word, grammatical_role, color, explanation])
                logger.info(f"DEBUG Spanish Transform - Added word_explanation: {word_explanations[-1]}")

            logger.info(f"DEBUG Spanish Transform - Final word_explanations count: {len(word_explanations)}")

            # Return in standard format expected by BaseGrammarAnalyzer
            return {
                'elements': elements,
                'explanations': explanations,
                'word_explanations': word_explanations,
                'sentence': parsed_data.get('sentence', '')
            }

        except Exception as e:
            logger.error(f"Failed to transform Spanish analysis data: {e}")
            return {
                'elements': {},
                'explanations': {'error': 'Data transformation failed'},
                'word_explanations': [],
                'sentence': parsed_data.get('sentence', '')
            }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return vibrant, educational color scheme for Spanish grammatical elements"""
        schemes = {
            "beginner": {
                "pronouns": "#FF4444",         # Bright Red - People/references
                "verbs": "#44FF44",            # Bright Green - Actions/states
                "nouns": "#FFAA00",            # Orange - Things/objects
                "adjectives": "#FF44FF",       # Magenta - Descriptions
                "adverbs": "#44FFFF",          # Cyan - How/when/where
                "other": "#888888"             # Gray - Other/unknown
            },
            "intermediate": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "verb_conjugation": "#AAFF44",   # Lime Green - Time expressions
                "idiomatic_expressions": "#FF8844",    # Coral - Expressions
                "other": "#888888"             # Gray
            },
            "advanced": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "verb_conjugation": "#AAFF44",   # Lime Green
                "idiomatic_expressions": "#FF8844",    # Coral
                "sentence_structure": "#AA44FF",  # Purple - Tone/emotion
                "discourse_markers": "#88FFAA",    # Mint
                "other": "#888888"             # Gray
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Spanish word-level grammar analysis quality (85% threshold required)"""

        try:
            # Check if essential elements are present
            words = parsed_data.get('words', [])
            phrase_combinations = parsed_data.get('phrase_combinations', [])
            explanations = parsed_data.get('explanations', {})

            # Basic validation checks
            has_words = len(words) > 0
            has_combinations = len(phrase_combinations) > 0
            has_explanations = len(explanations) > 0

            # Check word coverage in sentence
            sentence_words = original_sentence.split()
            analyzed_words = [word_data.get('word', '') for word_data in words]

            word_coverage = len(set(sentence_words).intersection(set(analyzed_words))) / len(sentence_words) if sentence_words else 0

            # Calculate confidence score
            base_score = 0.9 if (has_words and has_explanations) else 0.6
            coverage_bonus = word_coverage * 0.1
            combination_bonus = 0.05 if has_combinations else 0

            confidence = min(base_score + coverage_bonus + combination_bonus, 1.0)

            return confidence

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 0.5  # Conservative fallback


    def _parse_text_response(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Parse text response when JSON extraction fails - extract Spanish word-level elements"""
        try:
            # Initialize empty structure
            words = []
            phrase_combinations = []
            explanations = {}

            # Extract sentence (first line or first 100 chars)
            sentence = ai_response.split('\n')[0].strip()
            if len(sentence) > 100:
                sentence = sentence[:100] + "..."

            # Look for word analysis patterns in text
            text_lower = ai_response.lower()

            # Extract individual Spanish words from the sentence
            spanish_words = re.findall(r'\b\w+\b', sentence)

            # Create basic word entries for ALL words in the sentence
            for word in spanish_words:  # Analyze ALL words, not just first 10
                words.append({
                    "word": word,
                    "individual_meaning": f"Word '{word}' (meaning needs analysis)",
                    "pronunciation": "unknown",
                    "grammatical_role": "unknown",
                    "combinations": [],
                    "importance": "Part of the sentence structure"
                })

            # Look for phrase combination patterns
            # Find sequences of 2-4 words that appear in the text
            for i in range(len(spanish_words) - 1):
                for j in range(i + 2, min(i + 5, len(spanish_words) + 1)):
                    phrase = ' '.join(spanish_words[i:j])
                    if phrase in ai_response:
                        phrase_combinations.append({
                            "phrase": phrase,
                            "words": spanish_words[i:j],
                            "combined_meaning": f"Phrase '{phrase}' (compound meaning)",
                            "grammatical_structure": "word combination",
                            "usage_notes": "Forms a meaningful unit in Spanish"
                        })

            # Generate explanations based on found elements
            if words:
                explanations["word_analysis"] = "Each Spanish word has its own meaning and can combine to form phrases"
            if phrase_combinations:
                explanations["phrase_combinations"] = "Words combine to create phrases with specific meanings"
            explanations["sentence_structure"] = "Spanish sentence structure relies on word combinations and grammatical particles"

            return {
                'sentence': sentence,
                'words': words,
                'phrase_combinations': phrase_combinations,
                'explanations': explanations
            }

        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            return self._create_fallback_parse(ai_response, sentence)


    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Spanish text with word-level coloring using colors from word_explanations (single source of truth)"""
        explanations = parsed_data.get('word_explanations', [])

        logger.info(f"DEBUG Spanish HTML Gen - Input explanations count: {len(explanations)}")
        logger.info(f"DEBUG Spanish HTML Gen - Input sentence: '{sentence}'")

        # Generate HTML by coloring each word individually using colors from grammar explanations
        import re

        # Create mapping of cleaned words to colors directly from word_explanations (authoritative source)
        word_to_color = {}
        for exp in explanations:
            if len(exp) >= 3:
                word, pos, color = exp[0], exp[1], exp[2]
                clean_key = re.sub(r'[^\w\s]', '', word)  # Clean the key for consistent matching
                word_to_color[clean_key] = color
                logger.info(f"DEBUG Spanish HTML Gen - Word '{word}' (clean: '{clean_key}') -> Color '{color}' (POS: '{pos}')")

        logger.info(f"DEBUG Spanish HTML Gen - Word-to-color mapping: {word_to_color}")

        words_in_sentence = re.findall(r'\S+', sentence)

        logger.info(f"DEBUG Spanish HTML Gen - Words found in sentence: {words_in_sentence}")

        html_parts = []
        for word in words_in_sentence:
            # Remove punctuation for matching but keep original word
            clean_word = re.sub(r'[^\w\s]', '', word)

            logger.info(f"DEBUG Spanish HTML Gen - Processing word '{word}' -> clean '{clean_word}'")

            if clean_word in word_to_color:
                color = word_to_color[clean_word]
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')
                logger.info(f"DEBUG Spanish HTML Gen - ✓ Colored word '{word}' with color '{color}'")
            else:
                # For words without analysis, use default color (should be rare with new architecture)
                html_parts.append(f'<span style="color: #888888;">{word}</span>')
                logger.warning(f"DEBUG Spanish HTML Gen - ✗ No color found for word '{word}' (clean: '{clean_word}'). Available words: {list(word_to_color.keys())}")

        result = ' '.join(html_parts)
        logger.info(f"DEBUG Spanish HTML Gen - Final HTML output length: {len(result)}")
        logger.info(f"DEBUG Spanish HTML Gen - Final HTML preview: {result[:300]}...")
        return result

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map grammatical role descriptions to color category names"""
        role_lower = grammatical_role.lower()

        # Map various grammatical roles to color categories
        # Order matters: more specific checks first
        if any(keyword in role_lower for keyword in ['pronoun', 'personal', 'demonstrative']):
            return 'pronouns'
        elif any(keyword in role_lower for keyword in ['verb', 'action', 'state']):
            return 'verbs'
        elif any(keyword in role_lower for keyword in ['noun', 'object', 'subject']):
            return 'nouns'
        elif any(keyword in role_lower for keyword in ['adjective', 'description', 'quality']):
            return 'adjectives'
        elif any(keyword in role_lower for keyword in ['adverb', 'manner', 'time', 'place']):
            return 'adverbs'
        elif any(keyword in role_lower for keyword in ['idiomatic', 'expression']):
            return 'idiomatic_expressions'
        else:
            return 'other'

    def _get_default_category_for_word(self, word: str) -> str:
        """Get a default grammatical category for words that don't have detailed analysis"""
        # This is a simple heuristic based on common Spanish word patterns
        # In a real implementation, this could use more sophisticated analysis

        # Common pronouns
        if word.lower() in ['yo', 'tú', 'él', 'ella', 'nosotros', 'nosotras', 'vosotros', 'vosotras', 'ellos', 'ellas', 'usted', 'ustedes']:
            return 'pronouns'

        # Common verbs (basic forms)
        if word.lower() in ['ser', 'estar', 'tener', 'hacer', 'ir', 'ver', 'dar', 'saber', 'querer', 'llegar', 'pasar', 'deber', 'poner', 'parecer', 'quedar', 'creer', 'hablar', 'llevar', 'dejar', 'seguir']:
            return 'verbs'

        # Common articles
        if word.lower() in ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas']:
            return 'nouns'  # Articles are often categorized with nouns

        # Common prepositions
        if word.lower() in ['de', 'en', 'a', 'por', 'para', 'con', 'sin', 'sobre', 'desde', 'hasta', 'entre', 'durante', 'contra', 'hacia']:
            return 'other'  # Prepositions might not have specific color

        # Default to 'other' for unknown words
        return 'other'

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return comprehensive color scheme for Spanish grammatical elements based on linguistic categories"""
        schemes = {
            "beginner": {
                # Content words (Palabras de contenido)
                "nouns": "#FFAA00",                    # Orange - Things/objects/people/places (sustantivos)
                "adjectives": "#FF44FF",               # Magenta - Describes nouns (adjetivos)
                "verbs": "#44FF44",                    # Green - Actions/states (verbos)
                "adverbs": "#44FFFF",                  # Cyan - Modifies verbs/adjectives (adverbios)
                "pronouns": "#FF4444",                 # Red - Replaces nouns (pronombres)

                # Function words (Palabras funcionales)
                "articles": "#FFD700",                 # Gold - Definite/indefinite (artículos)
                "prepositions": "#4444FF",             # Blue - Relationships (preposiciones)
                "conjunctions": "#888888",             # Gray - Connectors (conjunciones)
                "interjections": "#FFD700",            # Gold - Exclamations (interjecciones)
                "auxiliaries": "#44FF44",              # Green - Helping verbs (auxiliares)
                "reflexives": "#FF6347",               # Tomato - Reflexive pronouns (reflexivos)
                "other": "#AAAAAA"                     # Light gray - Other
            },
            "intermediate": {
                # Content words (Palabras de contenido)
                "nouns": "#FFAA00",
                "adjectives": "#FF44FF",
                "verbs": "#44FF44",
                "adverbs": "#44FFFF",
                "pronouns": "#FF4444",
                "personal_pronouns": "#FF4444",
                "demonstrative_pronouns": "#FF4444",
                "possessive_pronouns": "#FF4444",
                "interrogative_pronouns": "#FF4444",
                "relative_pronouns": "#FF4444",

                # Function words (Palabras funcionales)
                "articles": "#FFD700",
                "numerals": "#FFFF44",                 # Yellow - Numbers (numerales)
                "auxiliaries": "#44FF44",
                "prepositions": "#4444FF",
                "conjunctions": "#888888",
                "interjections": "#FFD700",
                "reflexives": "#FF6347",
                "other": "#AAAAAA"
            },
            "advanced": {
                # Content words (Palabras de contenido)
                "nouns": "#FFAA00",
                "adjectives": "#FF44FF",
                "verbs": "#44FF44",
                "adverbs": "#44FFFF",
                "pronouns": "#FF4444",
                "personal_pronouns": "#FF4444",
                "demonstrative_pronouns": "#FF4444",
                "possessive_pronouns": "#FF4444",
                "interrogative_pronouns": "#FF4444",
                "relative_pronouns": "#FF4444",

                # Function words (Palabras funcionales)
                "articles": "#FFD700",
                "numerals": "#FFFF44",
                "auxiliaries": "#44FF44",
                "prepositions": "#4444FF",
                "conjunctions": "#888888",
                "interjections": "#FFD700",
                "reflexives": "#FF6347",
                "clitics": "#FF6347",                  # Tomato - Clitic pronouns
                "gerunds": "#44FF44",                  # Green - Gerund forms
                "past_participles": "#44FF44",         # Green - Past participle forms
                "infinitives": "#44FF44",              # Green - Infinitive forms
                "other": "#AAAAAA"
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map grammatical role descriptions to color category names using Spanish grammar rules

        CHILDREN-FIRST HIERARCHICAL CATEGORIZATION (Phase 5.7)
        Order matters: Check specific/sub-categories first, then general/parent categories
        This prevents concept overlap in multi-category words
        """
        # Preprocess: Clean up common AI mistakes and normalize the input
        original_role = grammatical_role
        role_lower = grammatical_role.lower().strip()

        # Fix common AI hallucinations: correct malformed grammatical roles
        if role_lower == "art article":
            role_lower = "article"
        elif role_lower == "v verb":
            role_lower = "verb"
        elif role_lower == "adj adjective":
            role_lower = "adjective"
        elif role_lower == "adv adverb":
            role_lower = "adverb"
        elif role_lower == "conj conjunction":
            role_lower = "conjunction"
        elif role_lower == "prep preposition":
            role_lower = "preposition"
        elif role_lower == "aux auxiliary":
            role_lower = "auxiliary"
        elif role_lower == "ref reflexive":
            role_lower = "reflexive"
        # General cleanup: remove single character prefixes followed by space
        import re
        role_lower = re.sub(r'^\w\s+', '', role_lower)

        if original_role != role_lower:
            logger.info(f"DEBUG Role preprocessing: '{original_role}' -> '{role_lower}'")

        # CRITICAL HIERARCHY: Children-first categorization to prevent overlap
        # Order: specific subtypes → general parent categories

        # 1. Specific pronoun subtypes BEFORE general pronoun
        if any(keyword in role_lower for keyword in ['personal_pronoun', 'personal pronoun', 'personal']):
            return 'personal_pronouns'
        elif any(keyword in role_lower for keyword in ['demonstrative_pronoun', 'demonstrative pronoun', 'demonstrative']):
            return 'demonstrative_pronouns'
        elif any(keyword in role_lower for keyword in ['possessive_pronoun', 'possessive pronoun', 'possessive']):
            return 'possessive_pronouns'
        elif any(keyword in role_lower for keyword in ['interrogative_pronoun', 'interrogative pronoun', 'interrogative']):
            return 'interrogative_pronouns'
        elif any(keyword in role_lower for keyword in ['relative_pronoun', 'relative pronoun', 'relative']):
            return 'relative_pronouns'

        # 2. Auxiliary verbs BEFORE main verbs
        if any(keyword in role_lower for keyword in ['auxiliary', 'auxiliary_verb', 'auxiliary verb', 'aux verb']):
            return 'auxiliaries'

        # 3. Reflexive pronouns BEFORE general pronouns
        if any(keyword in role_lower for keyword in ['reflexive', 'reflexive_pronoun', 'reflexive pronoun']):
            return 'reflexives'

        # 4. Numerals BEFORE other categories
        if any(keyword in role_lower for keyword in ['numeral', 'numeral_adjective', 'numeral adjective']):
            return 'numerals'

        # 5. Clitics BEFORE other categories
        if any(keyword in role_lower for keyword in ['clitic']):
            return 'clitics'

        # 6. Gerunds, past participles, infinitives
        if any(keyword in role_lower for keyword in ['gerund']):
            return 'gerunds'
        elif any(keyword in role_lower for keyword in ['past_participle', 'past participle']):
            return 'past_participles'
        elif any(keyword in role_lower for keyword in ['infinitive']):
            return 'infinitives'

        # PARENT CATEGORIES (checked after all children to prevent overlap)

        # General pronouns (after specific pronoun subtypes)
        if any(keyword in role_lower for keyword in ['pronoun']):
            return 'pronouns'

        # General conjunctions
        if any(keyword in role_lower for keyword in ['conjunction', 'coordinating_conjunction', 'subordinating_conjunction']):
            return 'conjunctions'

        # General interjections
        if any(keyword in role_lower for keyword in ['interjection', 'exclamation']):
            return 'interjections'

        # Content words - general categories
        if any(keyword in role_lower for keyword in ['adverb', 'manner_adverb', 'time_adverb', 'place_adverb']):
            return 'adverbs'
        elif any(keyword in role_lower for keyword in ['adjective', 'descriptive_adjective']):
            return 'adjectives'
        elif any(keyword in role_lower for keyword in ['noun', 'proper_noun', 'common_noun']):
            return 'nouns'
        elif any(keyword in role_lower for keyword in ['verb', 'main_verb']):
            return 'verbs'

        # Function words
        if any(keyword in role_lower for keyword in ['article', 'definite_article', 'indefinite_article']):
            return 'articles'
        elif any(keyword in role_lower for keyword in ['preposition']):
            return 'prepositions'

        # AI-generated roles that need mapping
        if 'subject' in role_lower:
            return 'pronouns'  # Subjects are typically pronouns in Spanish
        elif 'negation' in role_lower or 'determiner' in role_lower:
            return 'other'  # Negation particles and determiners

        # Fallback for legacy categories or unrecognized roles
        elif 'other' in role_lower or 'unknown' in role_lower:
            return 'other'

        # Default fallback
        return 'other'

    def _clean_grammatical_role(self, grammatical_role: str) -> str:
        """Clean grammatical role for display purposes, fixing AI hallucinations"""
        role_lower = grammatical_role.lower().strip()

        # Fix common AI hallucinations: correct malformed grammatical roles
        if role_lower == "art article":
            return "article"
        elif role_lower == "v verb":
            return "verb"
        elif role_lower == "adj adjective":
            return "adjective"
        elif role_lower == "adv adverb":
            return "adverb"
        elif role_lower == "conj conjunction":
            return "conjunction"
        elif role_lower == "int interjection":
            return "interjection"
        elif role_lower == "prep preposition":
            return "preposition"
        elif role_lower == "aux auxiliary":
            return "auxiliary"
        elif role_lower == "ref reflexive":
            return "reflexive"

        # General cleanup: remove single character prefixes followed by spaces
        import re
        # Remove patterns like "n noun", "v verb", etc. with any amount of whitespace
        cleaned = re.sub(r'^\w+\s+', '', role_lower)

        # Return the cleaned role, or original if no cleaning was needed
        return cleaned if cleaned and cleaned != role_lower else grammatical_role

    def _perform_spanish_specific_checks(self, elements: Dict[str, Any], original_sentence: str) -> float:
        """
        Perform Spanish-specific validation checks to assess analysis quality.
        Returns a score from 0.0 to 1.0 based on Spanish linguistic accuracy.
        """
        score = 0.0
        checks_passed = 0
        total_checks = 0

        try:
            # Check 1: Gender agreement (common in Spanish)
            total_checks += 1
            adjectives = elements.get('adjectives', [])
            nouns = elements.get('nouns', [])
            if len(adjectives) > 0 and len(nouns) > 0:
                checks_passed += 1
                score += 0.2

            # Check 2: Verb conjugation patterns (Spanish has complex conjugations)
            total_checks += 1
            verbs = elements.get('verbs', [])
            has_verb_conjugations = any(
                isinstance(verb, dict) and verb.get('form') in ['present', 'preterite', 'imperfect', 'future', 'conditional', 'subjunctive']
                for verb in verbs
            )
            if has_verb_conjugations:
                checks_passed += 1
                score += 0.2

            # Check 3: Ser vs Estar usage
            total_checks += 1
            ser_estar_found = any(
                'ser' in original_sentence.lower() or 'estar' in original_sentence.lower()
                for word_data in elements.get('verbs', []) + elements.get('auxiliaries', [])
                if isinstance(word_data, dict)
            )
            if ser_estar_found:
                checks_passed += 1
                score += 0.2

            # Check 4: Clitic pronouns (me, te, se, lo, la, etc.)
            total_checks += 1
            clitics_found = any(
                word_data.get('word', '').lower() in ['me', 'te', 'se', 'nos', 'os', 'lo', 'la', 'los', 'las', 'le', 'les']
                for word_data in elements.get('reflexives', []) + elements.get('pronouns', [])
                if isinstance(word_data, dict)
            )
            if clitics_found:
                checks_passed += 1
                score += 0.2

            # Check 5: Latin alphabet with Spanish characters (á, é, í, ó, ú, ñ, ü, ¿, ¡)
            total_checks += 1
            has_spanish_chars = any(char in 'áéíóúñü¿¡' for char in original_sentence)
            if has_spanish_chars:
                checks_passed += 1
                score += 0.2

            # Normalize score based on checks passed
            if total_checks > 0:
                score = min(score, 1.0)

        except Exception as e:
            logger.warning(f"Spanish-specific checks failed: {e}")
            return 0.0

        return score

    def _reorder_explanations_by_sentence_position(self, sentence: str, word_explanations: List[List]) -> List[List]:
        """
        Reorder word explanations to match the order they appear in the sentence.
        This ensures grammar explanations are displayed in sentence word order for better user experience.
        """
        if not word_explanations or not sentence:
            return word_explanations

        # Create a list to track word positions
        positioned_explanations = []

        for explanation in word_explanations:
            if len(explanation) >= 4:
                word = explanation[0]  # word is at index 0 in the list format
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

                    # Use the first occurrence position, or a high number if not found
                    position = positions[0] if positions else float('inf')
                    positioned_explanations.append((position, explanation))

        # Sort by position in sentence
        positioned_explanations.sort(key=lambda x: x[0])

        # Extract just the explanations
        sorted_explanations = [exp for _, exp in positioned_explanations]

        logger.debug(f"Reordered {len(sorted_explanations)} Spanish explanations by sentence position")
        return sorted_explanations

    def _create_fallback_parse(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Create fallback parsing when main parsing fails"""
        return {
            'sentence': sentence,
            'elements': {},
            'explanations': {
                'parsing_error': 'Unable to parse AI response, using fallback analysis'
            }
        }

# Register analyzer
def create_analyzer():
    """Factory function to create Spanish analyzer"""
    return EsAnalyzer()