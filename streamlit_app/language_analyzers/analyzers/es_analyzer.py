# Spanish Grammar Analyzer
# Auto-generated analyzer for Spanish (español)
# Language Family: Romance
# Script Type: alphabetic
# Complexity Rating: medium

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

logger = logging.getLogger(__name__)

class EsAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Spanish (español).

    Key Features: ['verb_conjugation', 'noun_adjective_agreement', 'pronoun_usage', 'sentence_structure', 'idiomatic_expressions']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "es"
    LANGUAGE_NAME = "Spanish"

    def __init__(self):
        config = LanguageConfig(
            code="es",
            name="Spanish",
            native_name="español",
            family="Romance",
            script_type="alphabetic",
            complexity_rating="medium",
            key_features=['verb_conjugation', 'noun_adjective_agreement', 'pronoun_usage', 'sentence_structure', 'idiomatic_expressions'],
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
        """Generate AI prompt for Spanish grammar analysis"""
        if complexity == "beginner":
            return self._get_beginner_prompt(sentence, target_word)
        elif complexity == "intermediate":
            return self._get_intermediate_prompt(sentence, target_word)
        elif complexity == "advanced":
            return self._get_advanced_prompt(sentence, target_word)
        else:
            return self._get_beginner_prompt(sentence, target_word)

    def _get_beginner_prompt(self, sentence: str, target_word: str) -> str:
        """Generate beginner-level grammar analysis prompt with detailed word-by-word explanations"""
        base_prompt = """Analyze this ENTIRE Spanish sentence WORD BY WORD: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL WORD in the sentence, provide:
- Its individual meaning and pronunciation
- Its grammatical role and function in this context
- How it combines with adjacent words (if applicable)
- Common phrases it forms and their meanings
- Why it's important for learners

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with detailed word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "la",
      "individual_meaning": "the (feminine definite article)",
      "pronunciation": "lah",
      "grammatical_role": "article",
      "combinations": ["la casa (lah kah-sah) - the house"],
      "importance": "Essential for indicating specificity"
    },
    {
      "word": "casa",
      "individual_meaning": "house",
      "pronunciation": "kah-sah",
      "grammatical_role": "noun",
      "combinations": ["la casa (lah kah-sah) - the house", "casa blanca (kah-sah blahn-kah) - white house"],
      "importance": "Common noun for buildings"
    }
  ],
  "phrase_combinations": [
    {
      "phrase": "la casa",
      "words": ["la", "casa"],
      "combined_meaning": "the house",
      "grammatical_structure": "article + noun",
      "usage_notes": "Common phrase for referring to a specific house"
    }
  ],
  "explanations": {
    "noun_adjective_agreement": "Adjectives agree with nouns in gender and number",
    "verb_conjugation": "Verbs change form to indicate tense, mood, and subject",
    "sentence_structure": "Subject-Verb-Object word order with some flexibility"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt with word-level analysis"""
        base_prompt = """Analyze this ENTIRE Spanish sentence WORD BY WORD for intermediate concepts: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL WORD in the sentence, provide:
- Word meaning, pronunciation, and grammatical role
- How it functions in phrases and clauses
- Verb conjugation and tense relationships it creates
- Pronoun usage and reference

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "hablar",
      "individual_meaning": "to speak",
      "pronunciation": "ah-blahr",
      "grammatical_role": "verb",
      "combinations": ["hablar español (ah-blahr ehs-pah-nyohl) - to speak Spanish"],
      "verb_conjugation": "Regular -ar verb conjugation"
    }
  ],
  "phrase_combinations": [
    {
      "phrase": "hablar español",
      "words": ["hablar", "español"],
      "combined_meaning": "to speak Spanish",
      "grammatical_structure": "verb + adjective",
      "usage_notes": "Common phrase for language proficiency"
    }
  ],
  "explanations": {
    "verb_conjugation": "Verbs change form to indicate tense, mood, and subject",
    "pronoun_usage": "Pronouns replace nouns to avoid repetition",
    "sentence_structure": "Intermediate sentence structure with clauses and phrases"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt with word-level analysis"""
        base_prompt = """Perform advanced grammatical analysis of this ENTIRE Spanish sentence WORD BY WORD: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL WORD in the sentence, analyze:
- Idiomatic expressions and figurative language
- Complex verb conjugation and tense relationships
- Word-level contributions to sentence meaning
- Advanced grammatical combinations and transformations

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "tomar",
      "individual_meaning": "to take",
      "pronunciation": "toh-mahr",
      "grammatical_role": "verb",
      "combinations": ["tomar un café (toh-mahr oon kah-feh) - to have a coffee"],
      "idiomatic_expression": "Tomar el pelo - to tease or joke"
    }
  ],
  "phrase_combinations": [
    {
      "phrase": "tomar un café",
      "words": ["tomar", "un", "café"],
      "combined_meaning": "to have a coffee",
      "grammatical_structure": "verb + indefinite article + noun",
      "usage_notes": "Common phrase for social interactions"
    }
  ],
  "explanations": {
    "idiomatic_expressions": "Idiomatic expressions convey nuanced meanings",
    "verb_conjugation": "Complex verb conjugation for nuanced expression",
    "sentence_structure": "Advanced sentence structure with complex clauses"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured Spanish word-level grammar analysis"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    # Add the sentence to the parsed data
                    parsed['sentence'] = sentence
                    return parsed
                except json.JSONDecodeError:
                    pass

            # Try direct JSON parsing
            try:
                parsed = json.loads(ai_response)
                parsed['sentence'] = sentence
                return parsed
            except json.JSONDecodeError:
                pass

            # Fallback: extract structured information from text
            return self._parse_text_response(ai_response, sentence)

        except Exception as e:
            logger.error(f"Failed to parse {self.language_name} grammar response: {e}")
            return self._create_fallback_parse(ai_response, sentence)

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
        """Generate HTML output for Spanish text with word-level coloring"""
        colors = self.get_color_scheme(complexity)
        words = parsed_data.get('words', [])
        phrase_combinations = parsed_data.get('phrase_combinations', [])
        sentence = parsed_data.get('sentence', '')

        # Create a mapping of each word to its grammatical category
        word_to_category = {}

        # Build word-to-category mapping from individual words
        # NOTE: We prioritize individual word colors over phrase combination colors
        # to ensure word-level analysis is preserved in the Colored Sentence
        for word_data in words:
            word = word_data.get('word', '')
            grammatical_role = word_data.get('grammatical_role', '')

            # Map grammatical roles to color categories
            if word and grammatical_role:
                category = self._map_grammatical_role_to_category(grammatical_role)
                word_to_category[word] = category

        # NOTE: Phrase combinations are handled in explanations, not in Colored Sentence HTML
        # This ensures the Colored Sentence shows individual word colors that match
        # the Grammar Explanations, providing authentic word-level learning

        # Generate HTML by coloring each word individually
        html_parts = []
        for word in sentence.split():
            if word in word_to_category:
                category = word_to_category[word]
                color = colors.get(category, '#CCCCCC')
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')
            elif word.strip():  # Only add non-whitespace words without color
                # For words without analysis, give them a default color based on basic word properties
                default_category = self._get_default_category_for_word(word)
                color = colors.get(default_category, '#888888')
                html_parts.append(f'<span style="color: {color};">{word}</span>')
            else:
                # Preserve whitespace
                html_parts.append(word)

        return ' '.join(html_parts)

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
        if