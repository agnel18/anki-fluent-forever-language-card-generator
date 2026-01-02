# French Grammar Analyzer
# Auto-generated analyzer for French (français)
# Language Family: Romance
# Script Type: alphabetic
# Complexity Rating: medium

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

logger = logging.getLogger(__name__)

class FrAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for French (français).

    Key Features: ['verb_conjugation', 'noun_gender', 'adjective_agreement', 'pronoun_usage', 'sentence_structure']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "fr"
    LANGUAGE_NAME = "French"

    def __init__(self):
        config = LanguageConfig(
            code="fr",
            name="French",
            native_name="français",
            family="Romance",
            script_type="alphabetic",
            complexity_rating="medium",
            key_features=['verb_conjugation', 'noun_gender', 'adjective_agreement', 'pronoun_usage', 'sentence_structure'],
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
        """Generate AI prompt for French grammar analysis"""
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
        base_prompt = """Analyze this ENTIRE French sentence WORD BY WORD: SENTENCE_PLACEHOLDER

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
      "word": "le",
      "individual_meaning": "the (masculine definite article)",
      "pronunciation": "/lə/",
      "grammatical_role": "article",
      "combinations": ["le livre (the book)"],
      "importance": "Essential for indicating specificity"
    },
    {
      "word": "livre",
      "individual_meaning": "book",
      "pronunciation": "/liːvʁ/",
      "grammatical_role": "noun",
      "combinations": ["le livre (the book)"],
      "importance": "Common noun in French"
    }
  ],
  "word_combinations": [
    {
      "word": "le livre",
      "words": ["le", "livre"],
      "combined_meaning": "the book",
      "grammatical_structure": "article + noun",
      "usage_notes": "Article agrees with noun in gender and number"
    }
  ],
  "explanations": {
    "noun_gender": "French nouns have grammatical gender (masculine/feminine)",
    "adjective_agreement": "Adjectives agree with nouns in gender and number",
    "sentence_structure": "French sentence structure is Subject-Verb-Object"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt with word-level analysis"""
        base_prompt = """Analyze this ENTIRE French sentence WORD BY WORD for intermediate concepts: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL WORD in the sentence, provide:
- Word meaning, pronunciation, and grammatical role
- How it functions in phrases and sentences
- Verb conjugation and tense
- Adjective agreement and noun modification

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "parle",
      "individual_meaning": "speaks",
      "pronunciation": "/paʁl/",
      "grammatical_role": "verb",
      "combinations": ["il parle (he speaks)"],
      "verb_conjugation": "present tense, third person singular"
    }
  ],
  "word_combinations": [
    {
      "word": "il parle",
      "words": ["il", "parle"],
      "combined_meaning": "he speaks",
      "grammatical_structure": "pronoun + verb",
      "usage_notes": "Verb agrees with subject in person and number"
    }
  ],
  "explanations": {
    "verb_conjugation": "French verbs conjugate for tense, mood, and person",
    "pronoun_usage": "Pronouns replace nouns in sentences",
    "sentence_structure": "Intermediate sentence structure with verb conjugation and adjective agreement"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt with word-level analysis"""
        base_prompt = """Perform advanced grammatical analysis of this ENTIRE French sentence WORD BY WORD: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL WORD in the sentence, analyze:
- Modal and discourse functions
- Complex verb conjugation and tense
- Word-level contributions to sentence meaning
- Advanced grammatical combinations and transformations

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "pourrait",
      "individual_meaning": "could",
      "pronunciation": "/puʁə/",
      "grammatical_role": "verb",
      "combinations": ["il pourrait (he could)"],
      "modal_function": "expresses possibility or ability"
    }
  ],
  "word_combinations": [
    {
      "word": "il pourrait",
      "words": ["il", "pourrait"],
      "combined_meaning": "he could",
      "grammatical_structure": "pronoun + verb",
      "usage_notes": "Verb expresses modal function"
    }
  ],
  "explanations": {
    "modal_verbs": "Modal verbs express possibility, necessity, or obligation",
    "discourse_markers": "Discourse markers connect ideas and show relationships",
    "sentence_structure": "Advanced sentence structure with modal verbs and complex verb conjugation"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured French word-level grammar analysis"""
        try:
            # Try to extract JSON from markdown code blocks first
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1)
                    parsed = json.loads(json_str)
                    # Add the sentence to the parsed data
                    parsed['sentence'] = sentence
                    return parsed
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in French analyzer (markdown): {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

            # Try to extract JSON from response - look for JSON object after text
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    parsed = json.loads(json_str)
                    # Add the sentence to the parsed data
                    parsed['sentence'] = sentence
                    return parsed
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in French analyzer: {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

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
        """Return vibrant, educational color scheme for French grammatical elements"""
        schemes = {
            "beginner": {
                "pronouns": "#FF4444",         # Bright Red - People/references
                "verbs": "#44FF44",            # Bright Green - Actions/states
                "articles": "#4444FF",        # Bright Blue - Grammar helpers
                "nouns": "#FFAA00",            # Orange - Things/objects
                "adjectives": "#FF44FF",       # Magenta - Descriptions
                "adverbs": "#44FFFF",          # Cyan - How/when/where
                "other": "#888888"             # Gray - Other/unknown
            },
            "intermediate": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "articles": "#4444FF",        # Bright Blue
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "verb_conjugation": "#AAFF44",   # Lime Green - Time expressions
                "adjective_agreement": "#FF8844",    # Coral - Agreement
                "other": "#888888"             # Gray
            },
            "advanced": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "articles": "#4444FF",        # Bright Blue
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "verb_conjugation": "#AAFF44",   # Lime Green
                "adjective_agreement": "#FF8844",    # Coral
                "modal_verbs": "#AA44FF",  # Purple - Tone/emotion
                "discourse_markers": "#88FFAA",    # Mint
                "sentence_final_particles": "#FFFF44", # Yellow
                "other": "#888888"             # Gray
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate French word-level grammar analysis quality (85% threshold required)"""

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
            sentence_words = original_sentence.split()
            analyzed_words = [word.get('word', '') for word in words]

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
        """Parse text response when JSON extraction fails - extract French word-level elements"""
        try:
            # Initialize empty structure
            words = []
            word_combinations = []
            explanations = {}

            # Extract sentence (first line or first 100 chars)
            sentence = ai_response.split('\n')[0].strip()
            if len(sentence) > 100:
                sentence = sentence[:100] + "..."

            # Look for word analysis patterns in text
            text_lower = ai_response.lower()

            # Extract individual words from the sentence
            sentence_words = sentence.split()

            # Create basic word entries for ALL words in the sentence
            for word in sentence_words:  # Analyze ALL words, not just first 10
                words.append({
                    "word": word,
                    "individual_meaning": f"Word '{word}' (meaning needs analysis)",
                    "pronunciation": "unknown",
                    "grammatical_role": "unknown",
                    "combinations": [],
                    "importance": "Part of the sentence structure"
                })

            # Look for word combination patterns
            # Find sequences of 2-4 words that appear in the text
            for i in range(len(sentence_words) - 1):
                for j in range(i + 2, min(i + 5, len(sentence_words) + 1)):
                    word = ' '.join(sentence_words[i:j])
                    if word in ai_response:
                        word_combinations.append({
                            "word": word,
                            "words": sentence_words[i:j],
                            "combined_meaning": f"Word '{word}' (compound meaning)",
                            "grammatical_structure": "word combination",
                            "usage_notes": "Forms a meaningful unit in French"
                        })

            # Generate explanations based on found elements
            if words:
                explanations["word_analysis"] = "Each French word has its own meaning and can combine to form phrases"
            if word_combinations:
                explanations["word_combinations"] = "Words combine to create phrases with specific meanings"
            explanations["sentence_structure"] = "French sentence structure relies on word combinations and grammatical functions"

            return {
                'sentence': sentence,
                'words': words,
                'word_combinations': word_combinations,
                'explanations': explanations
            }

        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            return self._create_fallback_parse(ai_response, sentence)


    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for French text with word-level coloring"""
        colors = self.get_color_scheme(complexity)
        words = parsed_data.get('words', [])
        word_combinations = parsed_data.get('word_combinations', [])
        sentence = parsed_data.get('sentence', '')

        # Create a mapping of each word to its grammatical category
        word_to_category = {}

        # Build word-to-category mapping from individual words
        # NOTE: We prioritize individual word colors over word combination colors
        # to ensure word-level analysis is preserved in the Colored Sentence
        for word_data in words:
            word = word_data.get('word', '')
            grammatical_role = word_data.get('grammatical_role', '')

            # Map grammatical roles to color categories
            if word and grammatical_role:
                category = self._map_grammatical_role_to_category(grammatical_role)
                word_to_category[word] = category

        # NOTE: Word combinations are handled in explanations, not in Colored Sentence HTML
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
        if any(keyword in role_lower for keyword in ['article', 'determiner']):
            return 'articles'
        elif any(keyword in role_lower for keyword in ['pronoun', 'personal', 'possessive']):
            return 'pronouns'
        elif any(keyword in role_lower for keyword in ['verb', 'action', 'state']):
            return 'verbs'
        elif any(keyword in role_lower for keyword in ['noun', 'object', 'subject']):
            return 'nouns'
        elif any(keyword in role_lower for keyword in ['adjective', 'description', 'quality']):
            return 'adjectives'
        elif any(keyword in role_lower for keyword in ['adverb', 'manner', 'time', 'place']):
            return 'adverbs'
        elif any(keyword in role_lower for keyword in ['modal', 'auxiliary']):
            return 'verb_conjugation'
        else:
            return 'other'

    def _get_default_category_for_word(self, word: str) -> str:
        """Get a default grammatical category for words that don't have detailed analysis"""
        # This is a simple heuristic based on common French word patterns
        # In a real implementation, this could use more sophisticated analysis

        """Get a default grammatical category for words that don't have detailed analysis"""
        # This is a simple heuristic based on common French word patterns
        # In a real implementation, this could use more sophisticated analysis

        # Common pronouns
        if word.lower() in ['je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles']:
            return 'pronouns'

        # Common verbs (basic forms)
        if word.lower() in ['être', 'avoir', 'faire', 'aller', 'venir', 'voir', 'savoir', 'pouvoir', 'vouloir', 'dire', 'venir', 'prendre', 'mettre', 'donner']:
            return 'verbs'

        # Common articles
        if word.lower() in ['le', 'la', 'les', 'un', 'une', 'des']:
            return 'articles'

        # Common prepositions
        if word.lower() in ['de', 'à', 'en', 'par', 'pour', 'avec', 'sans', 'sur', 'dans', 'chez', 'vers', 'contre']:
            return 'other'

        # Default to 'other' for unknown words
        return 'other'

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
    """Factory function to create French analyzer"""
    return FrAnalyzer()