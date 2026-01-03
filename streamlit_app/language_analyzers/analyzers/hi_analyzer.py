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

    def _get_beginner_prompt(self, sentence: str, target_word: str) -> str:
        """Generate beginner-level grammar analysis prompt with word-by-word explanations"""
        base_prompt = """Analyze this ENTIRE Hindi sentence WORD BY WORD: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL WORD in the sentence, provide:
- Its individual meaning and pronunciation (in IPA)
- Its grammatical role and function in this context (USE ONLY: pronoun, noun, verb, adjective, adverb, postposition, conjunction, interjection, other)
- How it shows gender agreement (masculine/feminine)
- Postpositions and case markings it uses
- Why it's important for learners

IMPORTANT: In Hindi, postpositions (like में, से, को, का, पर, तक) should be classified as "postposition", NOT as "other" or "preposition".
Common Hindi postpositions include: में (in), से (from/with/by), को (to), का (of), पर (on), तक (until), के (of), ने (by), etc.

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with detailed word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "मैं",
      "individual_meaning": "I (first person singular pronoun)",
      "pronunciation": "mɛ̃",
      "grammatical_role": "pronoun",
      "color": "#FF4444",
      "gender_agreement": "masculine (default for pronouns)",
      "case_marking": "nominative case",
      "postpositions": [],
      "importance": "Essential personal pronoun for self-reference"
    },
    {
      "word": "खाना",
      "individual_meaning": "food/meal",
      "pronunciation": "kʰaːnaː",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "gender_agreement": "masculine",
      "case_marking": "accusative case (implied)",
      "postpositions": [],
      "importance": "Common noun for food and eating"
    },
    {
      "word": "में",
      "individual_meaning": "in (postposition indicating location)",
      "pronunciation": "mɛ̃",
      "grammatical_role": "postposition",
      "color": "#4444FF",
      "gender_agreement": "n/a",
      "case_marking": "locative case",
      "postpositions": [],
      "importance": "Essential postposition for indicating location or time"
    }
  ],
  "word_combinations": [
    {
      "word": "खाना खाता",
      "words": ["खाना", "खाता"],
      "combined_meaning": "eats food",
      "grammatical_structure": "object + verb",
      "usage_notes": "Simple subject-verb-object construction"
    }
  ],
  "explanations": {
    "postpositions": "Hindi uses postpositions instead of prepositions (को, में, से, का)",
    "gender_agreement": "Adjectives and verbs agree with noun gender",
    "case_marking": "Nouns change form to show grammatical relationships",
    "word_order": "Subject-Object-Verb (SOV) word order",
    "pronunciation": "Devanagari script with complex consonant clusters"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!
CRITICAL: grammatical_role MUST be EXACTLY one of these 9 values with NO variations: "pronoun", "noun", "verb", "adjective", "adverb", "postposition", "conjunction", "interjection", "other"
CRITICAL: For EACH word, include the EXACT color hex code from this mapping:
- pronoun: #FF4444 (red)
- noun: #FFAA00 (orange)
- verb: #44FF44 (green)
- adjective: #FF44FF (magenta)
- adverb: #44FFFF (cyan)
- postposition: #4444FF (blue)
- conjunction: #888888 (gray)
- interjection: #888888 (gray)
- other: #888888 (gray)
CRITICAL: Do NOT use descriptions like "personal pronoun" or "action verb" - use ONLY the exact words above!
CRITICAL: If unsure, use "other" rather than making up a new category!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt with aspect and case marking"""
        base_prompt = """Analyze this Hindi sentence with INTERMEDIATE grammar focus: SENTENCE_PLACEHOLDER

Provide detailed analysis including:
- Aspect markers and tense expressions
- Case markings and postpositions
- Gender agreement patterns
- Verb conjugations and forms
- Word combinations and compounds

IMPORTANT: In Hindi, postpositions (like में, से, को, का, पर, तक) should be classified as "postposition", NOT as "other" or "preposition".

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with comprehensive analysis:
{
  "words": [
    {
      "word": "राम",
      "individual_meaning": "Ram (proper name)",
      "pronunciation": "raːm",
      "grammatical_role": "noun",
      "color": "#FFAA00",
      "gender_agreement": "masculine",
      "case_marking": "nominative case",
      "postpositions": [],
      "aspect_markers": [],
      "importance": "Proper noun as sentence subject"
    }
  ],
  "word_combinations": [
    {
      "word": "स्कूल जाता",
      "words": ["स्कूल", "जाता"],
      "combined_meaning": "goes to school",
      "grammatical_structure": "location + motion verb",
      "postposition_usage": "को (to) implied",
      "usage_notes": "Common motion verb construction"
    }
  ],
  "explanations": {
    "aspect_markers": "रहा है (continuous), चुका है (perfect), etc.",
    "case_system": "Nominative, accusative, dative, genitive, locative, ablative cases",
    "postpositions": "Complex postposition system replacing prepositions",
    "verb_conjugation": "Person, number, gender, tense, aspect agreement",
    "compound_verbs": "Light verb constructions (करना देना लेना)"
  }
}

CRITICAL: grammatical_role MUST be EXACTLY one of these 9 values with NO variations: "pronoun", "noun", "verb", "adjective", "adverb", "postposition", "conjunction", "interjection", "other"
CRITICAL: For EACH word, include the EXACT color hex code from this mapping:
- pronoun: #FF4444 (red)
- noun: #FFAA00 (orange)
- verb: #44FF44 (green)
- adjective: #FF44FF (magenta)
- adverb: #44FFFF (cyan)
- postposition: #4444FF (blue)
- conjunction: #888888 (gray)
- interjection: #888888 (gray)
- other: #888888 (gray)
CRITICAL: Do NOT use descriptions like "personal pronoun" or "action verb" - use ONLY the exact words above!

Focus on grammatical relationships and morphological patterns."""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt with complex morphological features"""
        base_prompt = """Perform ADVANCED morphological and syntactic analysis of this Hindi sentence: SENTENCE_PLACEHOLDER

Analyze complex features including:
- Causative constructions (वाना/वाना)
- Honorific verb forms
- Discourse particles and connectors
- Compound verb formations
- Embedded clauses and complex structures

IMPORTANT: In Hindi, postpositions (like में, से, को, का, पर, तक) should be classified as "postposition", NOT as "other" or "preposition".

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with advanced grammatical analysis:
{
  "words": [
    {
      "word": "करवाया",
      "individual_meaning": "caused to do/had done",
      "pronunciation": "kərʋaːjaː",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "gender_agreement": "masculine (past participle)",
      "case_marking": "perfective aspect",
      "postpositions": [],
      "causative_markers": ["वा"],
      "importance": "Shows indirect causation"
    }
  ],
  "word_combinations": [
    {
      "word": "काम करवाया",
      "words": ["काम", "करवाया"],
      "combined_meaning": "had the work done",
      "grammatical_structure": "object + causative verb",
      "honorific_usage": "Shows indirect causation",
      "usage_notes": "Causative construction indicating someone else performed the action"
    }
  ],
  "explanations": {
    "causative_forms": "Causative verbs show indirect causation (वाना/वाना)",
    "honorific_system": "Honorifics show respect through verb forms and pronouns",
    "compound_verbs": "Complex verb constructions with auxiliaries and light verbs",
    "discourse_particles": "Particles that show speaker attitude and discourse functions",
    "aspect_tense": "Complex aspectual and temporal distinctions",
    "morphological_complexity": "Words can have multiple layers of morphological marking",
    "sentence_structure": "Advanced sentence structure with complex verb forms and embedded clauses"
  }
}

CRITICAL: grammatical_role MUST be EXACTLY one of these 9 values with NO variations: "pronoun", "noun", "verb", "adjective", "adverb", "postposition", "conjunction", "interjection", "other"
CRITICAL: For EACH word, include the EXACT color hex code from this mapping:
- pronoun: #FF4444 (red)
- noun: #FFAA00 (orange)
- verb: #44FF44 (green)
- adjective: #FF44FF (magenta)
- adverb: #44FFFF (cyan)
- postposition: #4444FF (blue)
- conjunction: #888888 (gray)
- interjection: #888888 (gray)
- other: #888888 (gray)
CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured Hindi word-level grammar analysis"""
        try:
            # Try to extract JSON from markdown code blocks first
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1)
                    parsed = json.loads(json_str)
                    parsed['sentence'] = sentence
                    logger.info(f"Hindi analyzer parsed JSON from markdown successfully: {len(parsed.get('words', []))} words")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Hindi analyzer (markdown): {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

            # Try to extract JSON from response - look for JSON object after text
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    parsed = json.loads(json_str)
                    parsed['sentence'] = sentence
                    logger.info(f"Hindi analyzer parsed JSON successfully: {len(parsed.get('words', []))} words")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Hindi analyzer: {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

            # Try direct JSON parsing
            try:
                parsed = json.loads(ai_response)
                parsed['sentence'] = sentence
                logger.info(f"Hindi analyzer direct JSON parse successful: {len(parsed.get('words', []))} words")
                return self._transform_to_standard_format(parsed, complexity)
            except json.JSONDecodeError as e:
                logger.error(f"Direct JSON parse error in Hindi analyzer: {e}")
                logger.error(f"Raw AI response: {ai_response[:500]}...")

            # Fallback: extract structured information from text
            logger.warning("Hindi analyzer falling back to text parsing")
            return self._parse_text_response(ai_response, sentence)

        except Exception as e:
            logger.error(f"Failed to parse {self.language_name} grammar response: {e}")
            return self._create_fallback_parse(ai_response, sentence)

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
                
                # Create explanation text from available data
                explanation_parts = []
                if individual_meaning:
                    explanation_parts.append(individual_meaning)
                if pronunciation:
                    explanation_parts.append(f"({pronunciation})")
                
                explanation = ", ".join(explanation_parts) if explanation_parts else f"{grammatical_role}"
                
                word_explanations.append([word, grammatical_role, color, explanation])

            logger.info(f"Created {len(word_explanations)} word explanations, sample: {word_explanations[:2] if word_explanations else 'None'}")

            # Return in standard format expected by BaseGrammarAnalyzer
            return {
                'elements': elements,
                'explanations': explanations,
                'word_explanations': word_explanations,
                'sentence': parsed_data.get('sentence', '')
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
        """Return vibrant, educational color scheme for Hindi grammatical elements"""
        schemes = {
            "beginner": {
                "pronouns": "#FF4444",         # Red - People/references
                "verbs": "#44FF44",            # Green - Actions/states
                "postpositions": "#4444FF",    # Blue - Grammar helpers
                "nouns": "#FFAA00",            # Orange - Things/objects
                "adjectives": "#FF44FF",       # Magenta - Descriptions
                "adverbs": "#44FFFF",          # Cyan - How/when/where
                "other": "#888888"             # Gray - Other/unknown
            },
            "intermediate": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "postpositions": "#4444FF",    # Bright Blue
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "aspect_markers": "#AAFF44",   # Lime Green - Time expressions
                "case_markers": "#FF8844",     # Coral - Case markings
                "other": "#888888"             # Gray
            },
            "advanced": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "postpositions": "#4444FF",    # Bright Blue
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "aspect_markers": "#AAFF44",   # Lime Green
                "case_markers": "#FF8844",     # Coral
                "honorifics": "#AA44FF",       # Purple - Respect markers
                "causative_markers": "#FFAA88", # Light Coral
                "discourse_particles": "#88FFAA", # Mint
                "compound_verbs": "#FFFF44",   # Yellow
                "other": "#888888"             # Gray
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]



    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map grammatical role descriptions to color category names"""
        role_lower = grammatical_role.lower().strip()

        # Log the input for debugging
        logger.debug(f"Mapping grammatical role: '{grammatical_role}' -> '{role_lower}'")

        # Map various grammatical roles to color category names
        # CRITICAL: Order matters - check most specific patterns first
        # Use exact word boundaries where possible to avoid false matches

        # Pronouns (check first - most specific)
        if 'pronoun' in role_lower or 'subject' in role_lower:
            logger.debug(f"Mapped '{grammatical_role}' to 'pronouns'")
            return 'pronouns'

        # Adverbs (check before verbs since "adverb" contains "verb")
        elif 'adverb' in role_lower or ('time' in role_lower and 'noun' not in role_lower):
            logger.debug(f"Mapped '{grammatical_role}' to 'adverbs'")
            return 'adverbs'

        # Verbs (check for verb but not adverb)
        elif 'verb' in role_lower and 'adverb' not in role_lower:
            logger.debug(f"Mapped '{grammatical_role}' to 'verbs'")
            return 'verbs'

        # Nouns (check for noun but not verb/pronoun/adjective)
        elif 'noun' in role_lower and not any(word in role_lower for word in ['verb', 'pronoun', 'adjective']):
            logger.debug(f"Mapped '{grammatical_role}' to 'nouns'")
            return 'nouns'

        # Adjectives
        elif 'adjective' in role_lower:
            logger.debug(f"Mapped '{grammatical_role}' to 'adjectives'")
            return 'adjectives'

        # Postpositions
        elif 'postposition' in role_lower:
            logger.debug(f"Mapped '{grammatical_role}' to 'postpositions'")
            return 'postpositions'

        # Other specific categories
        elif any(keyword in role_lower for keyword in ['particle', 'interrogative', 'question', 'negation', 'determiner']):
            logger.debug(f"Mapped '{grammatical_role}' to 'other' (particle/negation)")
            return 'other'
        elif any(keyword in role_lower for keyword in ['article', 'indefinite', 'definite']):
            logger.debug(f"Mapped '{grammatical_role}' to 'other' (article)")
            return 'other'
        elif any(keyword in role_lower for keyword in ['conjunction', 'connect', 'subordinating']):
            logger.debug(f"Mapped '{grammatical_role}' to 'other' (conjunction)")
            return 'other'
        elif any(keyword in role_lower for keyword in ['interjection', 'exclamation']):
            logger.debug(f"Mapped '{grammatical_role}' to 'other' (interjection)")
            return 'other'
        else:
            logger.warning(f"No mapping found for grammatical role: '{grammatical_role}', mapping to 'other'")
            return 'other'

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
        # Define the exact color mapping that should be used
        standard_colors = {
            "pronouns": "#FF4444",         # Red
            "nouns": "#FFAA00",            # Orange
            "verbs": "#44FF44",            # Green
            "adjectives": "#FF44FF",       # Magenta
            "adverbs": "#44FFFF",          # Cyan
            "postpositions": "#4444FF",    # Blue
            "other": "#888888"             # Gray
        }

        # If AI provided a color, check if it matches the standard for this category
        if ai_color and ai_color.startswith('#'):
            expected_color = standard_colors.get(category, "#888888")
            # If AI color doesn't match expected, use the standard color
            if ai_color.upper() != expected_color.upper():
                logger.debug(f"AI provided color {ai_color} for category '{category}', standardizing to {expected_color}")
                return expected_color
            else:
                return ai_color  # AI got it right

        # If no AI color or invalid format, use standard color
        return standard_colors.get(category, "#888888")

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