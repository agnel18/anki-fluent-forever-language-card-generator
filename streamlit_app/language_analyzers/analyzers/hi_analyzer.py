# Hindi Grammar Analyzer
# Auto-generated analyzer for Hindi (हिंदी)
# Language Family: Indo-European
# Script Type: abugida
# Complexity Rating: medium

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..family_base_analyzers.indo_european_analyzer import IndoEuropeanAnalyzer
from ..base_analyzer import GrammarAnalysis, LanguageConfig

logger = logging.getLogger(__name__)

class HiAnalyzer(IndoEuropeanAnalyzer):
    """
    Grammar analyzer for Hindi (हिंदी).

    Key Features: ['postpositions', 'gender_agreement', 'case_marking', 'verb_conjugation', 'aspect_tense', 'honorifics']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "hi"
    LANGUAGE_NAME = "Hindi"

    def __init__(self):
        config = LanguageConfig(
            code="hi",
            name="Hindi",
            native_name="हिंदी",
            family="Indo-European",
            script_type="abugida",
            complexity_rating="medium",
            key_features=['postpositions', 'gender_agreement', 'case_marking', 'verb_conjugation', 'aspect_tense', 'honorifics'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

        # Language-specific patterns and rules
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize language-specific patterns and rules"""
        # Override in language-specific implementations
        pass

    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Generate AI prompt for Hindi grammar analysis"""
        if complexity == "beginner":
            return self._get_beginner_prompt(sentence, target_word)
        elif complexity == "intermediate":
            return self._get_intermediate_prompt(sentence, target_word)
        elif complexity == "advanced":
            return self._get_advanced_prompt(sentence, target_word)
        else:
            return self._get_beginner_prompt(sentence, target_word)

    def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
        """Generate Hindi-specific AI prompt for batch grammar analysis"""
        sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        return f"""Analyze the grammar of these Hindi sentences and provide detailed word-by-word analysis for each one.

Target word: "{target_word}"
Language: Hindi
Complexity level: {complexity}
Analysis should be in {native_language}

Sentences to analyze:
{sentences_text}

For EACH word in EVERY sentence, provide:
- word: the exact word as it appears in the sentence
- individual_meaning: the English translation/meaning of this specific word (MANDATORY - do not leave empty)
- grammatical_role: EXACTLY ONE category from this list: noun, adjective, verb, adverb, pronoun, postposition, conjunction, particle, auxiliary_verb, interjection, other

CRITICAL REQUIREMENTS:
- individual_meaning MUST be provided for EVERY word
- grammatical_role MUST be EXACTLY one word from the allowed list (no spaces, no prefixes, no suffixes)
- Examples of correct grammatical_role:
  - "noun" (not "common noun" or "n noun")
  - "postposition" (not "po ostposition" or "postpositional")
  - "verb" (not "v verb" or "main verb")
  - "auxiliary_verb" (not "aux verb" or "auxiliary verb")
  - "pronoun" (not "personal pronoun")
  - "other" for anything not in the list

Examples:
- "रबर" → individual_meaning: "rubber", grammatical_role: "noun"
- "की" → individual_meaning: "of", grammatical_role: "postposition"
- "है" → individual_meaning: "is", grammatical_role: "auxiliary_verb"
- "प्रति" → individual_meaning: "per/towards", grammatical_role: "postposition"

Return JSON in this exact format:
{{
  "batch_results": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "words": [
        {{
          "word": "रबर",
          "individual_meaning": "rubber",
          "grammatical_role": "noun"
        }},
        {{
          "word": "की",
          "individual_meaning": "of",
          "grammatical_role": "postposition"
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

    def _get_beginner_prompt(self, sentence: str, target_word: str) -> str:
        """Generate beginner-level grammar analysis prompt with condensed descriptions"""
        base_prompt = """Analyze this ENTIRE Hindi sentence WORD BY WORD: SENTENCE_PLACEHOLDER

For EACH word, provide:
- Individual meaning (English translation)
- Grammatical role (use exact ENUM values from the list below)

HINDI GRAMMATICAL ROLES - Use these exact ENUM values:

CONTENT WORDS:
- noun: people/places/things, gender/number/case inflection
- adjective: describes nouns/pronouns, declinable/indeclinable
- verb: actions/states, tense/aspect/mood/gender/number/person
- adverb: modifies verbs/adjectives/adverbs, manner/time/place/degree
- onomatopoeia: imitates sounds, semi-open class
- ideophone: sensory imitations, semi-open class
- echo_word: reduplicated forms, approximation/plurality

PRONOUNS:
- pronoun: replaces nouns, personal/demonstrative/relative/interrogative/indefinite/reflexive
- personal_pronoun: speaker/addressee/others, case inflection, honorifics
- demonstrative_pronoun: proximity-based reference, number/case inflection
- interrogative_pronoun: questions, case inflection
- relative_pronoun: relative clauses, correlative constructions
- indefinite_pronoun: non-specific reference, case inflection
- reflexive_pronoun: subject reference, possessive/indeclinable

FUNCTION WORDS:
- numeral_adjective: quantity/order, cardinal/ordinal
- auxiliary_verb: supports main verbs, tense/aspect/mood/voice
- postposition: relationships, oblique case, simple/compound
- conjunction: connects clauses, coordinating/subordinating
- interjection: emotions/exclamations, indeclinable
- particle: emphasis/nuance/modality, indeclinable/clitic

Pay special attention to: TARGET_PLACEHOLDER

Return JSON with word-by-word analysis:
{
  "words": [
    {
      "word": "मैं",
      "individual_meaning": "I",
      "grammatical_role": "pronoun"
    },
    {
      "word": "खाना",
      "individual_meaning": "food",
      "grammatical_role": "noun"
    }
  ]
}

VALIDATION REQUIREMENTS:
- EVERY word in the sentence MUST have an "individual_meaning" field
- individual_meaning MUST be the actual English meaning/translation of the word (not grammatical labels)
- If you cannot provide a meaning, use the word's basic dictionary definition
- Do NOT leave individual_meaning empty or use grammatical roles as meanings
- Examples: "मुर्गा" → "rooster/hen", "खाना" → "food", "है" → "is/am/are", "में" → "in"
"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt with condensed descriptions"""
        base_prompt = """Analyze this Hindi sentence with INTERMEDIATE grammar focus: SENTENCE_PLACEHOLDER

Provide detailed analysis including:
- Aspect markers and tense expressions (verb conjugations)
- Case markings and postpositions (postposition usage)
- Gender agreement patterns (adjective/noun agreement)
- Verb conjugations and forms (person/number/gender/tense/aspect)
- Word combinations and compounds (noun+postposition, verb+particle)
- Pronoun subtypes and their functions (personal, demonstrative, relative, etc.)

IMPORTANT: Use specific grammatical categories from the Hindi linguistics system:
- postposition: में (meṁ - in), से (se - from), को (ko - to), का (kā - of), पर (par - on), तक (tak - until), के (ke - of), ने (ne - ergative)
- particle: ही (hī - only), तो (to - then), भी (bhī - also), नहीं (nahī̃ - not), तक (tak - even)
- conjunction: और (aur - and), लेकिन (lekin - but), कि (ki - that), क्योंकि (kyõki - because), या (yā - or)
- auxiliary_verb: होना (honā - to be), रहना (rahnā - progressive), जाना (jānā - passive), देना (denā - benefactive)
- personal_pronoun: मैं (maiṁ - I), तुम (tum - you familiar), आप (āp - you formal), वह (vah - he/she)
- demonstrative_pronoun: यह (yah - this), वह (vah - that), ये (ye - these), वे (ve - those)
- relative_pronoun: जो (jo - who/which), जिस (jis - whose), जितना (jitnā - as much as)
- interrogative_pronoun: कौन (kaun - who), क्या (kyā - what), कहाँ (kahā̃ - where)
- indefinite_pronoun: कोई (koī - someone), कुछ (kuch - something), कहीं (kahī̃ - somewhere)
- reflexive_pronoun: अपना (apnā - own), खुद (khud - self), स्वयं (svayam - oneself)
- numeral_adjective: एक (ek - one), दो (do - two), पहला (pahlā - first), दूसरा (dūsrā - second)

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with comprehensive analysis:
{
  "words": [
    {
      "word": "राम",
      "individual_meaning": "Ram (proper name)",
      "grammatical_role": "noun"
    },
    {
      "word": "ने",
      "individual_meaning": "ergative postposition (by/agent)",
      "grammatical_role": "postposition"
    }
  ]
}
"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt with condensed descriptions"""
        base_prompt = """Perform ADVANCED morphological and syntactic analysis of this Hindi sentence: SENTENCE_PLACEHOLDER

Analyze complex features including:
- Causative constructions (वाना/वाना) - verb morphology
- Honorific verb forms - respect marking
- Discourse particles and connectors (particle usage)
- Compound verb formations (verb + particle combinations)
- Embedded clauses and complex structures (conjunction usage)
- Pronoun agreement and case marking in complex sentences
- Numeral quantification and distributive constructions
- Ideophones and echo constructions for expressiveness

IMPORTANT: Use specific grammatical categories from the Hindi linguistics system:
- particle: ही (hī - emphasis), तो (to - discourse), भी (bhī - additive), तक (tak - even), तक (tak - extent), नहीं (nahī̃ - negation)
- conjunction: और (aur - and), लेकिन (lekin - but), कि (ki - complementizer), क्योंकि (kyõki - because), जबकि (jabki - while), अगर (agar - if)
- postposition: ने (ne - ergative), से (se - ablative/instrumental), को (ko - dative), का (kā - genitive), में (meṁ - locative), पर (par - on), तक (tak - until)
- auxiliary_verb: होना (honā - to be), रहना (rahnā - progressive), जाना (jānā - passive), देना (denā - benefactive), लेना (lenā - perfective)
- personal_pronoun: मैं (maiṁ - I), तुम (tum - you familiar), आप (āp - you formal), यह (yah - he/she proximal), वह (vah - he/she distal)
- demonstrative_pronoun: यह (yah - this), वह (vah - that), ये (ye - these), वे (ve - those), इतना (itnā - this much), उतना (utnā - that much)
- relative_pronoun: जो (jo - who/which), जिस (jis - whose), जितना (jitnā - as much as), जैसा (jaisā - like)
- interrogative_pronoun: कौन (kaun - who), क्या (kyā - what), कहाँ (kahā̃ - where), कैसे (kaise - how), क्यों (kyõ - why)
- indefinite_pronoun: कोई (koī - someone), कुछ (kuch - something), कहीं (kahī̃ - somewhere), कभी (kabī - sometime)
- reflexive_pronoun: अपना (apnā - own), खुद (khud - self), स्वयं (svayam - oneself)
- numeral_adjective: एक (ek - one), दो (do - two), पहला (pahlā - first), दूसरा (dūsrā - second), दोनों (donõ - both)
- onomatopoeia: खटखट (khaṭkhaṭ - knock), धड़ाम (dhaṛām - thud), टनटन (ṭanṭan - tingling)
- ideophone: चमचम (camcam - sparkling), फटाफट (phaṭāphaṭ - quickly), धीरे-धीरे (dhīre-dhīre - slowly)
- echo_word: किताब-विताब (kitāb-vitāb - books etc.), चाय-वाय (cāy-vāy - tea and stuff)

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with advanced grammatical analysis:
{
  "words": [
    {
      "word": "करवाया",
      "individual_meaning": "caused to do/had done",
      "grammatical_role": "verb"
    },
    {
      "word": "ही",
      "individual_meaning": "only/indeed/emphasis particle",
      "grammatical_role": "particle"
    }
  ]
}
"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured Hindi word-level grammar analysis - JSON ONLY"""
        try:
            # Try to extract JSON from markdown code blocks first
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1)
                    parsed = json.loads(json_str)
                    # Handle batch item format
                    if 'sentence_index' in parsed:
                        # This is a batch item, extract the relevant data
                        parsed = {
                            'words': parsed.get('words', []),
                            'word_combinations': parsed.get('word_combinations', []),
                            'explanations': parsed.get('explanations', {})
                        }
                    parsed['sentence'] = sentence
                    logger.info(f"Hindi analyzer parsed JSON from markdown successfully: {len(parsed.get('words', []))} words")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Hindi analyzer (markdown): {e}")
                    raise ValueError(f"Invalid JSON in markdown block: {e}")

            # Try to extract JSON from response - look for JSON object after text
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    parsed = json.loads(json_str)
                    # Handle batch item format
                    if 'sentence_index' in parsed:
                        # This is a batch item, extract the relevant data
                        parsed = {
                            'words': parsed.get('words', []),
                            'word_combinations': parsed.get('word_combinations', []),
                            'explanations': parsed.get('explanations', {})
                        }
                    parsed['sentence'] = sentence
                    logger.info(f"Hindi analyzer parsed JSON successfully: {len(parsed.get('words', []))} words")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Hindi analyzer: {e}")
                    raise ValueError(f"Invalid JSON in response: {e}")

            # Try direct JSON parsing
            try:
                parsed = json.loads(ai_response)
                # Handle batch item format
                if 'sentence_index' in parsed:
                    # This is a batch item, extract the relevant data
                    parsed = {
                        'words': parsed.get('words', []),
                        'word_combinations': parsed.get('word_combinations', []),
                        'explanations': parsed.get('explanations', {})
                    }
                parsed['sentence'] = sentence
                logger.info(f"Hindi analyzer direct JSON parse successful: {len(parsed.get('words', []))} words")
                return self._transform_to_standard_format(parsed, complexity)
            except json.JSONDecodeError as e:
                logger.error(f"Direct JSON parse error in Hindi analyzer: {e}")
                raise ValueError(f"Response is not valid JSON: {e}")

        except Exception as e:
            logger.error(f"Failed to parse {self.language_name} grammar response: {e}")
            # JSON-only parsing - no text fallbacks allowed
            raise ValueError(f"Grammar analysis failed - response must be valid JSON: {e}")

    def _parse_text_response(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Enhanced fallback text parsing when JSON fails - extracts grammatical roles from AI response"""
        try:
            # Try to extract word-role pairs from the AI response text
            word_role_pairs = self._extract_word_roles_from_text(ai_response)

            # Split sentence into words for matching
            sentence_words = sentence.split()

            # Create elements dictionary with proper categorization
            elements = {}
            word_explanations = []

            for word in sentence_words:
                # Find matching role from extracted pairs (case-insensitive partial match)
                role = 'other'  # default
                for extracted_word, extracted_role in word_role_pairs:
                    if extracted_word.lower() in word.lower() or word.lower() in extracted_word.lower():
                        role = extracted_role
                        break

                # Map role to category
                category = self._map_grammatical_role_to_category(role)

                # Add to elements
                if category not in elements:
                    elements[category] = []
                elements[category].append({
                    'word': word,
                    'grammatical_role': role
                })

                # Create word explanation
                color = self._get_color_for_category(category)
                word_explanations.append([word, role, color, f'Extracted from text analysis: {role}'])

            return {
                'elements': elements,
                'word_explanations': word_explanations,
                'explanations': {'fallback': f'Enhanced text analysis extracted {len(word_role_pairs)} word-role pairs'},
                'sentence': sentence
            }

        except Exception as e:
            logger.error(f"Enhanced text parsing fallback failed: {e}")
            # Fall back to basic parsing
            words = sentence.split()
            elements = {
                'other': [{'word': word, 'grammatical_role': 'other'} for word in words]
            }
            return {
                'elements': elements,
                'explanations': {'fallback': 'Basic word-level analysis due to parsing failure'},
                'sentence': sentence
            }

    def _create_fallback_parse(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Create minimal fallback analysis when all parsing fails"""
        return {
            'elements': {},
            'explanations': {'error': 'Grammar analysis temporarily unavailable'},
            'sentence': sentence
        }

    def _transform_to_standard_format(self, parsed_data: Dict[str, Any], complexity: str = 'beginner') -> Dict[str, Any]:
        """Transform Hindi analyzer output to standard BaseGrammarAnalyzer format"""
        try:
            # Extract original data
            words = parsed_data.get('words', [])
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            logger.info(f"Hindi analyzer transforming {len(words)} words")
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

            for word_data in words:
                word = word_data.get('word', '')
                grammatical_role = word_data.get('grammatical_role', 'other')
                individual_meaning = word_data.get('individual_meaning', '')
                
                # Ensure grammatical_role is a string
                if not isinstance(grammatical_role, str):
                    logger.warning(f"grammatical_role is not a string: {grammatical_role} (type: {type(grammatical_role)}), defaulting to 'other'")
                    grammatical_role = 'other'
                
                # Clean the grammatical_role for display purposes
                cleaned_role = self._clean_grammatical_role(grammatical_role)
                
                category = self._map_grammatical_role_to_category(grammatical_role)
                color = colors.get(category, '#888888')
                
                # Create explanation text with grammatical context for better educational value
                explanation_parts = []
                if individual_meaning and individual_meaning.strip():
                    # Enhance basic translations with grammatical context for better learning
                    base_meaning = individual_meaning.strip()
                    
                    # Add educational context based on grammatical role
                    educational_enhancements = {
                        'noun': f"{base_meaning} (thing/object)",
                        'pronoun': f"{base_meaning} (replaces a noun)",
                        'adjective': f"{base_meaning} (describes a noun)",
                        'verb': f"{base_meaning} (action/state)",
                        'adverb': f"{base_meaning} (modifies verb/adjective)",
                        'postposition': f"{base_meaning} (shows relationship/location)",
                        'conjunction': f"{base_meaning} (connects ideas)",
                        'particle': f"{base_meaning} (adds emphasis/nuance)",
                        'auxiliary_verb': f"{base_meaning} (helps main verb)",
                        'interjection': f"{base_meaning} (expresses emotion)"
                    }
                    
                    enhanced_meaning = educational_enhancements.get(category, base_meaning)
                    explanation_parts.append(enhanced_meaning)
                else:
                    # Provide fallback with grammatical context
                    logger.warning(f"Missing individual_meaning for word '{word}' with grammatical role '{grammatical_role}'")
                    fallback_explanations = {
                        'noun': f'{grammatical_role} (thing/object)',
                        'pronoun': f'{grammatical_role} (replaces noun)',
                        'adjective': f'{grammatical_role} (describes noun)',
                        'verb': f'{grammatical_role} (action/state)',
                        'adverb': f'{grammatical_role} (modifies verb/adjective)',
                        'postposition': f'{grammatical_role} (shows relationship)',
                        'conjunction': f'{grammatical_role} (connects clauses)',
                        'interjection': f'{grammatical_role} (expresses emotion)',
                        'particle': f'{grammatical_role} (adds nuance/emphasis)',
                        'auxiliary_verb': f'{grammatical_role} (supports main verb)'
                    }
                    explanation_parts.append(fallback_explanations.get(category, f'{grammatical_role}'))
                
                explanation = ", ".join(explanation_parts)
                
                word_explanations.append([word, cleaned_role, color, explanation])

            logger.info(f"Created {len(word_explanations)} word explanations, sample: {word_explanations[:2] if word_explanations else 'None'}")

            # Return in standard format expected by BaseGrammarAnalyzer
            return {
                'elements': elements,
                'explanations': explanations,
                'word_explanations': word_explanations,
                'sentence': parsed_data.get('sentence', ''),
                'grammar_summary': explanations.get('sentence_structure', '') if explanations else ''
            }

        except Exception as e:
            logger.error(f"Failed to transform Hindi analysis data: {e}")
            return {
                'elements': {},
                'explanations': {'error': 'Data transformation failed'},
                'word_explanations': [],
                'sentence': parsed_data.get('sentence', '')
            }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return comprehensive color scheme for Hindi grammatical elements based on linguistic categories"""
        schemes = {
            "beginner": {
                # Content words (सार्थक शब्द)
                "noun": "#FFAA00",                    # Orange - Things/objects/people/places
                "adjective": "#FF44FF",               # Magenta - Describes nouns
                "verb": "#44FF44",                    # Green - Actions/states
                "adverb": "#44FFFF",                  # Cyan - Modifies verbs/adjectives
                "onomatopoeia": "#FFD700",            # Gold - Sound imitation
                "ideophone": "#FFD700",               # Gold - Sensory imitation
                "echo_word": "#FFD700",               # Gold - Reduplicated forms

                # Pronouns (सर्वनाम)
                "pronoun": "#FF4444",                 # Red - Replaces nouns
                "personal_pronoun": "#FF4444",        # Red - I, you, he/she
                "demonstrative_pronoun": "#FF4444",   # Red - This, that
                "interrogative_pronoun": "#FF4444",   # Red - Who, what
                "relative_pronoun": "#FF4444",        # Red - Who/which (relative)
                "indefinite_pronoun": "#FF4444",      # Red - Someone, something
                "reflexive_pronoun": "#FF4444",       # Red - Own, self

                # Function words (असार्थक शब्द)
                "numeral_adjective": "#FFFF44",       # Yellow - Numbers, ordinals
                "auxiliary_verb": "#44FF44",          # Green - Support main verbs
                "postposition": "#4444FF",            # Blue - Relationships (postpositions)
                "conjunction": "#888888",             # Gray - Connectors
                "interjection": "#FFD700",            # Gold - Emotions/exclamations
                "particle": "#AA44FF",                # Purple - Emphasis/nuance
                "other": "#AAAAAA"                    # Light gray - Other
            },
            "intermediate": {
                # Content words (सार्थक शब्द)
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "onomatopoeia": "#FFD700",
                "ideophone": "#FFD700",
                "echo_word": "#FFD700",

                # Pronouns (सर्वनाम)
                "pronoun": "#FF4444",
                "personal_pronoun": "#FF4444",
                "demonstrative_pronoun": "#FF4444",
                "interrogative_pronoun": "#FF4444",
                "relative_pronoun": "#FF4444",
                "indefinite_pronoun": "#FF4444",
                "reflexive_pronoun": "#FF4444",

                # Function words (असार्थक शब्द)
                "numeral_adjective": "#FFFF44",
                "auxiliary_verb": "#44FF44",
                "postposition": "#4444FF",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "particle": "#AA44FF",
                "other": "#AAAAAA"
            },
            "advanced": {
                # Content words (सार्थक शब्द)
                "noun": "#FFAA00",
                "adjective": "#FF44FF",
                "verb": "#44FF44",
                "adverb": "#44FFFF",
                "onomatopoeia": "#FFD700",
                "ideophone": "#FFD700",
                "echo_word": "#FFD700",

                # Pronouns (सर्वनाम) - more distinctions
                "pronoun": "#FF4444",
                "personal_pronoun": "#FF4444",
                "demonstrative_pronoun": "#FF4444",
                "interrogative_pronoun": "#FF4444",
                "relative_pronoun": "#FF4444",
                "indefinite_pronoun": "#FF4444",
                "reflexive_pronoun": "#FF4444",

                # Function words (असार्थक शब्द) - more distinctions
                "numeral_adjective": "#FFFF44",
                "auxiliary_verb": "#44FF44",
                "postposition": "#4444FF",
                "conjunction": "#888888",
                "interjection": "#FFD700",
                "particle": "#AA44FF",
                "other": "#AAAAAA"
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]



    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map grammatical role descriptions to color category names using Hindi grammar rules

        CHILDREN-FIRST HIERARCHICAL CATEGORIZATION (Phase 5.7)
        Order matters: Check specific/sub-categories first, then general/parent categories
        This prevents concept overlap in multi-category words
        """
        # Preprocess: Clean up common AI mistakes and normalize the input
        original_role = grammatical_role
        role_lower = grammatical_role.lower().strip()
        
        # Fix common AI hallucinations: correct malformed grammatical roles
        # Examples: "po ostposition" -> "postposition", "v verb" -> "verb"
        if role_lower == "po ostposition":
            role_lower = "postposition"
        elif role_lower == "v verb":
            role_lower = "verb"
        elif role_lower == "adj adjective":
            role_lower = "adjective"
        elif role_lower == "adv adverb":
            role_lower = "adverb"
        elif role_lower == "conj conjunction":
            role_lower = "conjunction"
        elif role_lower == "int interjection":
            role_lower = "interjection"
        elif role_lower == "part particle":
            role_lower = "particle"
        elif role_lower == "aux auxiliary_verb":
            role_lower = "auxiliary_verb"
        # General cleanup: remove single character prefixes followed by space
        import re
        role_lower = re.sub(r'^\w\s+', '', role_lower)
        
        if original_role != role_lower:
            logger.info(f"DEBUG Role preprocessing: '{original_role}' -> '{role_lower}'")

        # CRITICAL HIERARCHY: Children-first categorization to prevent overlap
        # Order: specific subtypes → general parent categories

        # 1. Auxiliary verbs BEFORE main verbs (auxiliary_verb → verb)
        # Example: "होना" as auxiliary "is" vs main verb "become"
        if any(keyword in role_lower for keyword in ['सहायक क्रिया', 'sahāyak kriyā', 'auxiliary_verb', 'auxiliary verb', 'auxiliary']):
            return 'auxiliary_verb'

        # 2. Specific pronoun subtypes BEFORE general pronoun (personal/demonstrative/interrogative/relative/indefinite/reflexive → pronoun)
        if any(keyword in role_lower for keyword in ['व्यक्तिवाचक सर्वनाम', 'vyaktivācak sarvanām', 'personal_pronoun', 'personal pronoun', 'personal']):
            return 'personal_pronoun'
        elif any(keyword in role_lower for keyword in ['निदर्शक सर्वनाम', 'nidarśak sarvanām', 'demonstrative_pronoun', 'demonstrative pronoun', 'demonstrative']):
            return 'demonstrative_pronoun'
        elif any(keyword in role_lower for keyword in ['प्रश्नवाचक सर्वनाम', 'praśnavācak sarvanām', 'interrogative_pronoun', 'interrogative pronoun', 'interrogative']):
            return 'interrogative_pronoun'
        elif any(keyword in role_lower for keyword in ['संबंधवाचक सर्वनाम', 'sambandhavācak sarvanām', 'relative_pronoun', 'relative pronoun', 'relative']):
            return 'relative_pronoun'
        elif any(keyword in role_lower for keyword in ['अनिश्चयवाचक सर्वनाम', 'aniścayavācak sarvanām', 'indefinite_pronoun', 'indefinite pronoun', 'indefinite']):
            return 'indefinite_pronoun'
        elif any(keyword in role_lower for keyword in ['निजवाचक सर्वनाम', 'nijavācak sarvanām', 'reflexive_pronoun', 'reflexive pronoun', 'reflexive']):
            return 'reflexive_pronoun'

        # 3. Postpositions BEFORE prepositions (postposition → preposition)
        # Example: "से" as postposition "from" vs potential prepositional use
        if any(keyword in role_lower for keyword in ['संबंधबोधक', 'sambandh bodhak', 'postposition', 'postpositional']):
            return 'postposition'

        # 4. Particles BEFORE conjunctions (particle → conjunction)
        # Example: "तो" as particle "then" vs conjunction "so"
        if any(keyword in role_lower for keyword in ['निपात', 'nipāt', 'particle', 'emphasis_particle', 'modal_particle']):
            return 'particle'

        # 5. Ideophones BEFORE interjections (ideophone → interjection)
        # Example: "धड़ाम" as ideophone "thud" vs interjection
        if any(keyword in role_lower for keyword in ['अनुकरण शब्द', 'anukaraṇ śabd', 'ideophone']):
            return 'ideophone'

        # 6. Echo words BEFORE general categories
        if any(keyword in role_lower for keyword in ['दोहराव शब्द', 'doharāv śabd', 'echo_word', 'echo']):
            return 'echo_word'

        # 7. Onomatopoeia BEFORE interjections
        if any(keyword in role_lower for keyword in ['ध्वन्यात्मक शब्द', 'dhvanyātmak śabd', 'onomatopoeia', 'onomatopoeic']):
            return 'onomatopoeia'

        # 8. Numeral adjectives BEFORE general adjectives
        if any(keyword in role_lower for keyword in ['संख्यावाचक विशेषण', 'saṅkhyāvācak viśeṣaṇ', 'numeral_adjective', 'numeral adjective', 'numeral']):
            return 'numeral_adjective'

        # PARENT CATEGORIES (checked after all children to prevent overlap)

        # General pronouns (after specific pronoun subtypes)
        if any(keyword in role_lower for keyword in ['सर्वनाम', 'sarvanām', 'pronoun']):
            return 'pronoun'

        # General conjunctions (after particles)
        if any(keyword in role_lower for keyword in ['समुच्चयबोधक', 'samuccayabodhak', 'conjunction', 'coordinating_conjunction', 'subordinating_conjunction']):
            return 'conjunction'

        # General interjections (after ideophones and onomatopoeia)
        if any(keyword in role_lower for keyword in ['विस्मयादिबोधक', 'vismayādibodhak', 'interjection', 'exclamation']):
            return 'interjection'

        # Content words - general categories
        if any(keyword in role_lower for keyword in ['क्रिया विशेषण', 'kriyā viśeṣaṇ', 'adverb', 'manner_adverb', 'time_adverb', 'place_adverb']):
            return 'adverb'
        elif any(keyword in role_lower for keyword in ['विशेषण', 'viśeṣaṇ', 'adjective', 'descriptive_adjective']):
            return 'adjective'
        elif any(keyword in role_lower for keyword in ['संज्ञा', 'saṅgyā', 'noun', 'proper_noun', 'common_noun']):
            return 'noun'
        elif any(keyword in role_lower for keyword in ['क्रिया', 'kriyā', 'verb', 'main_verb']):
            return 'verb'

        # AI-generated roles that need mapping
        if 'subject' in role_lower:
            return 'pronoun'  # Subjects are typically pronouns in Hindi
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
        if role_lower == "po ostposition":
            return "postposition"
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
        elif role_lower == "part particle":
            return "particle"
        elif role_lower == "aux auxiliary_verb":
            return "auxiliary_verb"
        
        # General cleanup: remove single character prefixes followed by spaces
        import re
        # Remove patterns like "n noun", "v verb", etc. with any amount of whitespace
        cleaned = re.sub(r'^\w+\s+', '', role_lower)
        
        # Return the cleaned role, or original if no cleaning was needed
        return cleaned if cleaned and cleaned != role_lower else grammatical_role

    def _map_grammatical_structure_to_category(self, grammatical_structure: str) -> str:
        """Map grammatical structure descriptions to color categories"""
        structure_lower = grammatical_structure.lower()

        if 'postposition' in structure_lower:
            return 'postpositions'
        elif 'verb' in structure_lower:
            return 'verbs'
        elif 'noun' in structure_lower:
            return 'nouns'
        elif 'adjective' in structure_lower:
            return 'adjectives'
        else:
            return 'other'

    def _get_default_category_for_word(self, word: str) -> str:
        """Get a default grammatical category for words that don't have detailed analysis"""
        # Simple heuristics based on common Hindi word patterns
        word_lower = word.lower()

        # Common pronouns
        if word in ['मैं', 'तुम', 'यह', 'वह', 'हम', 'तुम्हें', 'उन्हें']:
            return 'pronouns'

        # Common verbs (basic forms)
        if word in ['है', 'हो', 'करो', 'करना', 'खाना', 'पीना', 'देखना']:
            return 'verbs'

        # Common postpositions
        if word in ['का', 'की', 'के', 'को', 'से', 'में', 'पर', 'ने']:
            return 'postpositions'

        # Default to 'other' for unknown words
        return 'other'

    def _standardize_color(self, ai_color: str, category: str) -> str:
        """Standardize AI-provided color to ensure consistency with the defined color scheme"""
        # Get the actual color scheme for the current complexity (default to intermediate)
        color_scheme = self.get_color_scheme('intermediate')

        # If AI provided a color, check if it matches the expected color for this category
        if ai_color and ai_color.startswith('#'):
            expected_color = color_scheme.get(category, "#888888")
            # If AI color doesn't match expected, use the expected color
            if ai_color.upper() != expected_color.upper():
                logger.debug(f"AI provided color {ai_color} for category '{category}', standardizing to {expected_color}")
                return expected_color
            else:
                return ai_color  # AI got it right

        # If no AI color or invalid format, use the color from the scheme
        return color_scheme.get(category, "#888888")

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Hindi word-level grammar analysis quality (85% threshold required)"""

        try:
            # Check if essential elements are present
            elements = parsed_data.get('elements', {})
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            # Basic validation checks
            has_elements = len(elements) > 0
            has_combinations = len(word_combinations) > 0
            has_explanations = len(explanations) > 0

            # Check word coverage in sentence
            sentence_words = set(original_sentence.split())
            analyzed_words = set()

            for role, word_list in elements.items():
                if role != 'word_combinations':
                    for word_data in word_list:
                        if isinstance(word_data, dict):
                            word = word_data.get('word', '')
                            if word:
                                analyzed_words.add(word)

            word_coverage = len(sentence_words.intersection(analyzed_words)) / len(sentence_words) if sentence_words else 0

            # Calculate confidence score
            base_score = 0.9 if (has_elements and has_explanations) else 0.6
            coverage_bonus = word_coverage * 0.1
            combination_bonus = 0.05 if has_combinations else 0

            confidence = min(base_score + coverage_bonus + combination_bonus, 1.0)

            return confidence

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 0.5  # Conservative fallback

# Register analyzer
def create_analyzer():
    """Factory function to create Hindi analyzer"""
    return HiAnalyzer()