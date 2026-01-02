# German Grammar Analyzer
# Auto-generated analyzer for German (Deutsch)
# Language Family: Germanic
# Script Type: alphabetic
# Complexity Rating: high

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

logger = logging.getLogger(__name__)

class DeAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for German (Deutsch).

    Key Features: ['case_system', 'verb_conjugation', 'sentence_structure', 'modal_particles', 'separable_prefixes']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "de"
    LANGUAGE_NAME = "German"

    def __init__(self):
        config = LanguageConfig(
            code="de",
            name="German",
            native_name="Deutsch",
            family="Germanic",
            script_type="alphabetic",
            complexity_rating="high",
            key_features=['case_system', 'verb_conjugation', 'sentence_structure', 'modal_particles', 'separable_prefixes'],
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
        """Generate AI prompt for German grammar analysis"""
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
        base_prompt = """Analyze this ENTIRE German sentence WORD BY WORD: SENTENCE_PLACEHOLDER

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
      "word": "der",
      "individual_meaning": "the (masculine definite article)",
      "pronunciation": "dehr",
      "grammatical_role": "article",
      "combinations": ["der Mann (the man)"],
      "importance": "Essential for indicating noun gender and case"
    },
    {
      "word": "Hund",
      "individual_meaning": "dog",
      "pronunciation": "hoont",
      "grammatical_role": "noun",
      "combinations": ["der Hund (the dog)"],
      "importance": "Common noun in German"
    }
  ],
  "phrase_combinations": [
    {
      "phrase": "der Hund",
      "words": ["der", "Hund"],
      "combined_meaning": "the dog",
      "grammatical_structure": "article + noun",
      "usage_notes": "Common phrase in German"
    }
  ],
  "explanations": {
    "case_system": "German has a complex case system with four cases: nominative, accusative, genitive, and dative",
    "sentence_structure": "German sentence structure typically follows the subject-verb-object word order"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt with word-level analysis"""
        base_prompt = """Analyze this ENTIRE German sentence WORD BY WORD for intermediate concepts: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL WORD in the sentence, provide:
- Word meaning, pronunciation, and grammatical role
- How it functions in compound words and phrases
- Verb conjugation and tense
- Complex sentence structure

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "gehen",
      "individual_meaning": "to go",
      "pronunciation": "gah-en",
      "grammatical_role": "verb",
      "combinations": ["ich gehe (I go)"],
      "verb_conjugation": "first person singular present tense"
    }
  ],
  "phrase_combinations": [
    {
      "phrase": "ich gehe",
      "words": ["ich", "gehe"],
      "combined_meaning": "I go",
      "grammatical_structure": "subject + verb",
      "usage_notes": "Common phrase in German"
    }
  ],
  "explanations": {
    "verb_conjugation": "German verbs are conjugated based on tense, mood, and person",
    "sentence_structure": "Intermediate sentence structure with complex verb conjugation and word order"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt with word-level analysis"""
        base_prompt = """Perform advanced grammatical analysis of this ENTIRE German sentence WORD BY WORD: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL WORD in the sentence, analyze:
- Modal and discourse particles it creates
- Complex grammatical combinations and transformations
- Word-level contributions to sentence meaning
- Advanced grammatical structures

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with word analysis for ALL words in the sentence:
{
  "words": [
    {
      "word": "würde",
      "individual_meaning": "would (conditional mood)",
      "pronunciation": "vur-deh",
      "grammatical_role": "auxiliary verb",
      "combinations": ["ich würde gehen (I would go)"],
      "modal_particle": "conditional mood"
    }
  ],
  "phrase_combinations": [
    {
      "phrase": "ich würde gehen",
      "words": ["ich", "würde", "gehen"],
      "combined_meaning": "I would go",
      "grammatical_structure": "subject + auxiliary verb + main verb",
      "usage_notes": "Common phrase in German"
    }
  ],
  "explanations": {
    "modal_particles": "Modal particles express speaker attitude and discourse functions",
    "sentence_structure": "Advanced sentence structure with complex grammatical combinations and transformations"
  }
}

CRITICAL: Analyze EVERY word in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured German word-level grammar analysis"""
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
                    logger.error(f"JSON decode error in German analyzer (markdown): {e}")
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
                    logger.error(f"JSON decode error in German analyzer: {e}")
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
        """Return vibrant, educational color scheme for German grammatical elements"""
        schemes = {
            "beginner": {
                "articles": "#FF4444",         # Bright Red - Articles
                "nouns": "#44FF44",            # Bright Green - Nouns
                "verbs": "#4444FF",            # Bright Blue - Verbs
                "adjectives": "#FFAA00",            # Orange - Adjectives
                "adverbs": "#44FFFF",          # Cyan - Adverbs
                "other": "#888888"             # Gray - Other/unknown
            },
            "intermediate": {
                "articles": "#FF4444",         # Bright Red
                "nouns": "#44FF44",            # Bright Green
                "verbs": "#4444FF",            # Bright Blue
                "adjectives": "#FFAA00",            # Orange
                "adverbs": "#44FFFF",          # Cyan
                "verb_conjugation": "#AAFF44",   # Lime Green - Verb conjugation
                "sentence_structure": "#FF8844",    # Coral - Sentence structure
                "other": "#888888"             # Gray
            },
            "advanced": {
                "articles": "#FF4444",         # Bright Red
                "nouns": "#44FF44",            # Bright Green
                "verbs": "#4444FF",            # Bright Blue
                "adjectives": "#FFAA00",            # Orange
                "adverbs": "#44FFFF",          # Cyan
                "verb_conjugation": "#AAFF44",   # Lime Green
                "sentence_structure": "#FF8844",    # Coral
                "modal_particles": "#AA44FF",  # Purple - Modal particles
                "separable_prefixes": "#FFAA88", # Light Coral
                "discourse_markers": "#88FFAA",    # Mint
                "other": "#888888"             # Gray
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate German word-level grammar analysis quality (85% threshold required)"""

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
        """Parse text response when JSON extraction fails - extract German word-level elements"""
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

            # Extract individual German words from the sentence
            german_words = re.findall(r'\b\w+\b', sentence)

            # Create basic word entries for ALL words in the sentence
            for word in german_words:  # Analyze ALL words, not just first 10
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
            for i in range(len(german_words) - 1):
                for j in range(i + 2, min(i + 5, len(german_words) + 1)):
                    phrase = ' '.join(german_words[i:j])
                    if phrase in ai_response:
                        phrase_combinations.append({
                            "phrase": phrase,
                            "words": german_words[i:j],
                            "combined_meaning": f"Phrase '{phrase}' (compound meaning)",
                            "grammatical_structure": "word combination",
                            "usage_notes": "Forms a meaningful unit in German"
                        })

            # Generate explanations based on found elements
            if words:
                explanations["word_analysis"] = "Each German word has its own meaning and can combine to form compound words"
            if phrase_combinations:
                explanations["phrase_combinations"] = "Words combine to create compound phrases with specific meanings"
            explanations["sentence_structure"] = "German sentence structure relies on word order and grammatical particles"

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
        """Generate HTML output for German text with word-level coloring"""
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
        if any(keyword in role_lower for keyword in ['article', 'der', 'die', 'das']):
            return 'articles'
        elif any(keyword in role_lower for keyword in ['noun', 'substantiv']):
            return 'nouns'
        elif any(keyword in role_lower for keyword in ['verb', 'aktion', 'zustand']):
            return 'verbs'
        elif any(keyword in role_lower for keyword in ['adjective', 'eigenschaft', 'beschreibung']):
            return 'adjectives'
        elif any(keyword in role_lower for keyword in ['adverb', 'umstand', 'zeit', 'ort']):
            return 'adverbs'
        elif any(keyword in role_lower for keyword in ['modal', 'möglichkeit', 'notwendigkeit']):
            return 'modal_particles'
        else:
            return 'other'

    def _get_default_category_for_word(self, word: str) -> str:
        """Get a default grammatical category for words that don't have detailed analysis"""
        # This is a simple heuristic based on common German word patterns
        # In a real implementation, this could use more sophisticated analysis

        # Common articles
        if word in ['der', 'die', 'das']:
            return 'articles'

        # Common nouns
        if word in ['Hund', 'Katze', 'Haus']:
            return 'nouns'

        # Common verbs
        if word in ['gehen', 'laufen', 'essen']:
            return 'verbs'

        # Default to 'other' for unknown words
        return 'other'


    def _create_fallback_parse(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Create minimal fallback analysis when all parsing fails"""
        return {
            'elements': {},
            'explanations': {'error': 'Grammar analysis temporarily unavailable'},
            'sentence': sentence
        }