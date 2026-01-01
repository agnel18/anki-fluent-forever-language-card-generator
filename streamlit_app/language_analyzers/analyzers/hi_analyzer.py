# Hindi Grammar Analyzer
# Auto-generated analyzer for Hindi (हिंदी)
# Language Family: Indo-European
# Script Type: abugida
# Complexity Rating: medium

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

logger = logging.getLogger(__name__)

class HiAnalyzer(BaseGrammarAnalyzer):
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
- Its grammatical role and function in this context
- How it shows gender agreement (masculine/feminine)
- Postpositions and case markings it uses
- Why it's important for learners

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with detailed word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "मैं",
      "individual_meaning": "I (first person singular pronoun)",
      "pronunciation": "mɛ̃",
      "grammatical_role": "subject pronoun",
      "gender_agreement": "masculine (default for pronouns)",
      "case_marking": "nominative case",
      "postpositions": [],
      "importance": "Essential personal pronoun for self-reference"
    },
    {
      "word": "खाना",
      "individual_meaning": "food/meal",
      "pronunciation": "kʰaːnaː",
      "grammatical_role": "direct object noun",
      "gender_agreement": "masculine",
      "case_marking": "accusative case (implied)",
      "postpositions": [],
      "importance": "Common noun for food and eating"
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

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
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

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with comprehensive analysis:
{
  "words": [
    {
      "word": "राम",
      "individual_meaning": "Ram (proper name)",
      "pronunciation": "raːm",
      "grammatical_role": "subject noun",
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

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with advanced grammatical analysis:
{
  "words": [
    {
      "word": "करवाया",
      "individual_meaning": "caused to do/had done",
      "pronunciation": "kərʋaːjaː",
      "grammatical_role": "causative verb",
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

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured Hindi word-level grammar analysis"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    # Add the sentence to the parsed data
                    parsed['sentence'] = sentence
                    return self._transform_to_standard_format(parsed)
                except json.JSONDecodeError:
                    pass

            # Try direct JSON parsing
            try:
                parsed = json.loads(ai_response)
                parsed['sentence'] = sentence
                return self._transform_to_standard_format(parsed)
            except json.JSONDecodeError:
                pass

            # Fallback: extract structured information from text
            return self._parse_text_response(ai_response, sentence)

        except Exception as e:
            logger.error(f"Failed to parse {self.language_name} grammar response: {e}")
            return self._create_fallback_parse(ai_response, sentence)

    def _parse_text_response(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Fallback text parsing when JSON fails"""
        try:
            # Basic text parsing - extract words from sentence and create minimal analysis
            words = sentence.split()
            elements = {
                'other': [{'word': word, 'grammatical_role': 'other'} for word in words]
            }

            return {
                'elements': elements,
                'explanations': {'fallback': 'Basic word-level analysis due to parsing failure'},
                'sentence': sentence
            }
        except Exception as e:
            logger.error(f"Text parsing fallback failed: {e}")
            return self._create_fallback_parse(ai_response, sentence)

    def _create_fallback_parse(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Create minimal fallback analysis when all parsing fails"""
        return {
            'elements': {},
            'explanations': {'error': 'Grammar analysis temporarily unavailable'},
            'sentence': sentence
        }

    def _transform_to_standard_format(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Hindi analyzer output to standard BaseGrammarAnalyzer format"""
        try:
            # Extract original data
            words = parsed_data.get('words', [])
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            # Transform words into elements grouped by grammatical role
            elements = {}

            # Group words by their grammatical role
            for word_data in words:
                grammatical_role = word_data.get('grammatical_role', 'other')
                if grammatical_role not in elements:
                    elements[grammatical_role] = []
                elements[grammatical_role].append(word_data)

            # Add word combinations as a special category
            if word_combinations:
                elements['word_combinations'] = word_combinations

            # Return in standard format expected by BaseGrammarAnalyzer
            return {
                'elements': elements,
                'explanations': explanations,
                'sentence': parsed_data.get('sentence', '')
            }

        except Exception as e:
            logger.error(f"Failed to transform Hindi analysis data: {e}")
            return {
                'elements': {},
                'explanations': {'error': 'Data transformation failed'},
                'sentence': parsed_data.get('sentence', '')
            }

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return vibrant, educational color scheme for Hindi grammatical elements"""
        schemes = {
            "beginner": {
                "pronouns": "red",             # Red - People/references
                "verbs": "green",              # Green - Actions/states
                "postpositions": "blue",       # Blue - Grammar helpers
                "nouns": "orange",             # Orange - Things/objects
                "adjectives": "magenta",       # Magenta - Descriptions
                "adverbs": "cyan",             # Cyan - How/when/where
                "other": "gray"                # Gray - Other/unknown
            },
            "intermediate": {
                "pronouns": "red",             # Bright Red
                "verbs": "green",              # Bright Green
                "postpositions": "blue",       # Bright Blue
                "nouns": "orange",             # Orange
                "adjectives": "magenta",       # Magenta
                "adverbs": "cyan",             # Cyan
                "aspect_markers": "lime",      # Lime Green - Time expressions
                "case_markers": "coral",       # Coral - Case markings
                "other": "gray"                # Gray
            },
            "advanced": {
                "pronouns": "red",             # Bright Red
                "verbs": "green",              # Bright Green
                "postpositions": "blue",       # Bright Blue
                "nouns": "orange",             # Orange
                "adjectives": "magenta",       # Magenta
                "adverbs": "cyan",             # Cyan
                "aspect_markers": "lime",      # Lime Green
                "case_markers": "coral",       # Coral
                "honorifics": "purple",        # Purple - Respect markers
                "causative_markers": "pink",   # Light Coral
                "discourse_particles": "teal", # Mint
                "compound_verbs": "yellow",    # Yellow
                "other": "gray"                # Gray
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Hindi word-level grammar analysis quality (85% threshold required)"""

        try:
            # Check if essential elements are present
            words = parsed_data.get('words', [])
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            # Basic validation checks
            has_words = len(words) > 0
            has_combinations = len(word_combinations) > 0
            has_explanations = len(explanations) > 0

            # Check word coverage in sentence
            sentence_words = set(original_sentence.split())
            analyzed_words = set()

            for word_data in words:
                word = word_data.get('word', '')
                if word:
                    analyzed_words.add(word)

            word_coverage = len(sentence_words.intersection(analyzed_words)) / len(sentence_words) if sentence_words else 0

            # Calculate confidence score
            base_score = 0.9 if (has_words and has_explanations) else 0.6
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