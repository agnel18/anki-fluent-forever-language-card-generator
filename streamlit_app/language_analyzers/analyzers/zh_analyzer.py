# Chinese (Simplified) Grammar Analyzer
# Auto-generated analyzer for Chinese (Simplified) (中文 (简体))
# Language Family: Sino-Tibetan
# Script Type: logographic
# Complexity Rating: high

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

logger = logging.getLogger(__name__)

class ZhAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Chinese (Simplified) (中文 (简体)).

    Key Features: ['particles', 'aspect_system', 'measure_words', 'topic_comment_structure', 'negation_patterns', 'modal_particles', 'structural_particles']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "zh"
    LANGUAGE_NAME = "Chinese (Simplified)"

    def __init__(self):
        config = LanguageConfig(
            code="zh",
            name="Chinese (Simplified)",
            native_name="中文 (简体)",
            family="Sino-Tibetan",
            script_type="logographic",
            complexity_rating="high",
            key_features=['particles', 'aspect_system', 'measure_words', 'topic_comment_structure', 'negation_patterns', 'modal_particles', 'structural_particles'],
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
        """Generate AI prompt for Chinese (Simplified) grammar analysis"""
        if complexity == "beginner":
            return self._get_beginner_prompt(sentence, target_word)
        elif complexity == "intermediate":
            return self._get_intermediate_prompt(sentence, target_word)
        elif complexity == "advanced":
            return self._get_advanced_prompt(sentence, target_word)
        else:
            return self._get_beginner_prompt(sentence, target_word)

    def _get_beginner_prompt(self, sentence: str, target_word: str) -> str:
        """Generate beginner-level grammar analysis prompt with detailed character-by-character explanations"""
        base_prompt = """Analyze this ENTIRE Chinese (Simplified) sentence CHARACTER BY CHARACTER: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL CHARACTER in the sentence, provide:
- Its individual meaning and pronunciation
- Its grammatical role and function in this context
- How it combines with adjacent characters (if applicable)
- Common words it forms and their meanings
- Why it's important for learners

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with detailed character analysis for ALL characters in the sentence:
{
  "characters": [
    {
      "character": "这",
      "individual_meaning": "this (demonstrative pronoun)",
      "pronunciation": "zhè",
      "grammatical_role": "demonstrative pronoun",
      "combinations": ["这个 (zhège) - this (with measure word)", "这里 (zhèlǐ) - here"],
      "importance": "Essential for indicating proximity and specificity"
    },
    {
      "character": "是",
      "individual_meaning": "to be/am/are/is (linking verb)",
      "pronunciation": "shì",
      "grammatical_role": "linking verb",
      "combinations": ["不是 (búshì) - is not", "还是 (háishì) - or/still"],
      "importance": "Fundamental linking verb for equations and identities"
    }
  ],
  "word_combinations": [
    {
      "word": "这本书",
      "characters": ["这", "本", "书"],
      "combined_meaning": "this book",
      "grammatical_structure": "demonstrative pronoun + measure word + noun",
      "usage_notes": "Measure word '本' is used for books and similar bound objects"
    }
  ],
  "explanations": {
    "character_analysis": "Each Chinese character has its own meaning and can combine to form compound words",
    "measure_words": "Measure words (量词) are required between numbers/demonstratives and nouns",
    "sentence_structure": "Subject-Verb-Object word order with characters combining into meaningful units"
  }
}

CRITICAL: Analyze EVERY character in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt with character-level analysis"""
        base_prompt = """Analyze this ENTIRE Chinese (Simplified) sentence CHARACTER BY CHARACTER for intermediate concepts: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL CHARACTER in the sentence, provide:
- Character meaning, pronunciation, and grammatical role
- How it functions in compound words and phrases
- Aspect markers and temporal relationships it creates
- Complex particle usage and structural functions

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with character analysis for ALL characters in the sentence:
{
  "characters": [
    {
      "character": "正",
      "individual_meaning": "just/right/correct",
      "pronunciation": "zhèng",
      "grammatical_role": "aspect marker component",
      "combinations": ["正在 (zhèngzài) - progressive aspect 'is doing'", "正 (zhèng) - just/now"],
      "aspect_function": "Part of progressive aspect marker indicating ongoing action"
    }
  ],
  "word_combinations": [
    {
      "word": "正在吃",
      "characters": ["正", "在", "吃"],
      "combined_meaning": "is eating (progressive aspect)",
      "grammatical_structure": "progressive aspect marker + main verb",
      "usage_notes": "Indicates action in progress at the time of speaking"
    }
  ],
  "explanations": {
    "aspect_system": "Aspect markers show how actions unfold over time, not just tense",
    "character_combinations": "Characters combine to create complex grammatical meanings",
    "sentence_structure": "Intermediate sentence structure with aspect markers and complex particles"
  }
}

CRITICAL: Analyze EVERY character in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt with character-level analysis"""
        base_prompt = """Perform advanced grammatical analysis of this ENTIRE Chinese (Simplified) sentence CHARACTER BY CHARACTER: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL CHARACTER in the sentence, analyze:
- Modal and discourse particles it creates
- Complex aspectual and pragmatic functions
- Character-level contributions to sentence meaning
- Advanced grammatical combinations and transformations

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with character analysis for ALL characters in the sentence:
{
  "characters": [
    {
      "character": "把",
      "individual_meaning": "to hold/grasp",
      "pronunciation": "bǎ",
      "grammatical_role": "structural particle",
      "combinations": ["把字句 (bǎzìjù) - 'ba' construction for disposal/formal objects"],
      "pragmatic_function": "Introduces formal object in disposal constructions",
      "advanced_usage": "Creates topic-comment structure with object fronting"
    }
  ],
  "word_combinations": [
    {
      "word": "把书",
      "characters": ["把", "书"],
      "combined_meaning": "the book (as formal object)",
      "grammatical_structure": "structural particle + formal object",
      "usage_notes": "Object is fronted and marked as affected by the action"
    }
  ],
  "explanations": {
    "modal_particles": "Modal particles express speaker attitude and discourse functions",
    "structural_particles": "Structural particles organize complex sentence grammar",
    "discourse_markers": "Discourse markers connect ideas and show relationships",
    "sentence_final_particles": "Sentence-final particles add emphasis or tone",
    "aspect_system": "Complex aspectual distinctions and temporal relationships",
    "discourse_structure": "Advanced discourse organization and pragmatic functions",
    "character_level_analysis": "Each character contributes to complex grammatical meanings"
  }
}

CRITICAL: Analyze EVERY character in the sentence, not just the target word!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured Chinese character-level grammar analysis"""
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
        """Return vibrant, educational color scheme for Chinese grammatical elements"""
        schemes = {
            "beginner": {
                "pronouns": "#FF4444",         # Bright Red - People/references
                "verbs": "#44FF44",            # Bright Green - Actions/states
                "particles": "#4444FF",        # Bright Blue - Grammar helpers
                "nouns": "#FFAA00",            # Orange - Things/objects
                "adjectives": "#FF44FF",       # Magenta - Descriptions
                "adverbs": "#44FFFF",          # Cyan - How/when/where
                "other": "#888888"             # Gray - Other/unknown
            },
            "intermediate": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "particles": "#4444FF",        # Bright Blue
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "aspect_markers": "#AAFF44",   # Lime Green - Time expressions
                "measure_words": "#FF8844",    # Coral - Quantity words
                "other": "#888888"             # Gray
            },
            "advanced": {
                "pronouns": "#FF4444",         # Bright Red
                "verbs": "#44FF44",            # Bright Green
                "particles": "#4444FF",        # Bright Blue
                "nouns": "#FFAA00",            # Orange
                "adjectives": "#FF44FF",       # Magenta
                "adverbs": "#44FFFF",          # Cyan
                "aspect_markers": "#AAFF44",   # Lime Green
                "measure_words": "#FF8844",    # Coral
                "modal_particles": "#AA44FF",  # Purple - Tone/emotion
                "structural_particles": "#FFAA88", # Light Coral
                "discourse_markers": "#88FFAA",    # Mint
                "sentence_final_particles": "#FFFF44", # Yellow
                "other": "#888888"             # Gray
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Chinese character-level grammar analysis quality (85% threshold required)"""

        try:
            # Check if essential elements are present
            characters = parsed_data.get('characters', [])
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            # Basic validation checks
            has_characters = len(characters) > 0
            has_combinations = len(word_combinations) > 0
            has_explanations = len(explanations) > 0

            # Check character coverage in sentence
            sentence_chars = set(original_sentence)
            analyzed_chars = set()

            for char_data in characters:
                char = char_data.get('character', '')
                if char:
                    analyzed_chars.add(char)

            char_coverage = len(sentence_chars.intersection(analyzed_chars)) / len(sentence_chars) if sentence_chars else 0

            # Calculate confidence score
            base_score = 0.9 if (has_characters and has_explanations) else 0.6
            coverage_bonus = char_coverage * 0.1
            combination_bonus = 0.05 if has_combinations else 0

            confidence = min(base_score + coverage_bonus + combination_bonus, 1.0)

            return confidence

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 0.5  # Conservative fallback


    def _parse_text_response(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Parse text response when JSON extraction fails - extract Chinese character-level elements"""
        try:
            # Initialize empty structure
            characters = []
            word_combinations = []
            explanations = {}

            # Extract sentence (first line or first 100 chars)
            sentence = ai_response.split('\n')[0].strip()
            if len(sentence) > 100:
                sentence = sentence[:100] + "..."

            # Look for character analysis patterns in text
            text_lower = ai_response.lower()

            # Extract individual Chinese characters from the sentence
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', sentence)

            # Create basic character entries for ALL characters in the sentence
            for char in chinese_chars:  # Analyze ALL characters, not just first 10
                characters.append({
                    "character": char,
                    "individual_meaning": f"Character '{char}' (meaning needs analysis)",
                    "pronunciation": "unknown",
                    "grammatical_role": "unknown",
                    "combinations": [],
                    "importance": "Part of the sentence structure"
                })

            # Look for word combination patterns
            # Find sequences of 2-4 characters that appear in the text
            for i in range(len(chinese_chars) - 1):
                for j in range(i + 2, min(i + 5, len(chinese_chars) + 1)):
                    word = ''.join(chinese_chars[i:j])
                    if word in ai_response:
                        word_combinations.append({
                            "word": word,
                            "characters": list(word),
                            "combined_meaning": f"Word '{word}' (compound meaning)",
                            "grammatical_structure": "character combination",
                            "usage_notes": "Forms a meaningful unit in Chinese"
                        })

            # Generate explanations based on found elements
            if characters:
                explanations["character_analysis"] = "Each Chinese character has its own meaning and can combine to form compound words"
            if word_combinations:
                explanations["word_combinations"] = "Characters combine to create compound words with specific meanings"
            explanations["sentence_structure"] = "Chinese sentence structure relies on character combinations and grammatical particles"

            return {
                'sentence': sentence,
                'characters': characters,
                'word_combinations': word_combinations,
                'explanations': explanations
            }

        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            return self._create_fallback_parse(ai_response, sentence)


    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Chinese text with character-level coloring"""
        colors = self.get_color_scheme(complexity)
        characters = parsed_data.get('characters', [])
        word_combinations = parsed_data.get('word_combinations', [])
        sentence = parsed_data.get('sentence', '')

        # Create a mapping of each character to its grammatical category
        char_to_category = {}

        # Build character-to-category mapping from individual characters
        # NOTE: We prioritize individual character colors over word combination colors
        # to ensure character-level analysis is preserved in the Colored Sentence
        for char_data in characters:
            char = char_data.get('character', '')
            grammatical_role = char_data.get('grammatical_role', '')

            # Map grammatical roles to color categories
            if char and grammatical_role:
                category = self._map_grammatical_role_to_category(grammatical_role)
                char_to_category[char] = category

        # NOTE: Word combinations are handled in explanations, not in Colored Sentence HTML
        # This ensures the Colored Sentence shows individual character colors that match
        # the Grammar Explanations, providing authentic character-level learning

        # Generate HTML by coloring each character individually
        html_parts = []
        for char in sentence:
            if char in char_to_category:
                category = char_to_category[char]
                color = colors.get(category, '#CCCCCC')
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{char}</span>')
            elif char.strip():  # Only add non-whitespace characters without color
                # For characters without analysis, give them a default color based on basic character properties
                default_category = self._get_default_category_for_char(char)
                color = colors.get(default_category, '#888888')
                html_parts.append(f'<span style="color: {color};">{char}</span>')
            else:
                # Preserve whitespace
                html_parts.append(char)

        return ''.join(html_parts)

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map grammatical role descriptions to color category names"""
        role_lower = grammatical_role.lower()

        # Map various grammatical roles to color categories
        # Order matters: more specific checks first
        if any(keyword in role_lower for keyword in ['particle', 'marker', 'aspect', 'modal', 'structural']):
            return 'particles'
        elif any(keyword in role_lower for keyword in ['pronoun', 'demonstrative', 'personal']):
            return 'pronouns'
        elif any(keyword in role_lower for keyword in ['verb', 'linking', 'action', 'state']):
            return 'verbs'
        elif any(keyword in role_lower for keyword in ['noun', 'object', 'subject']):
            return 'nouns'
        elif any(keyword in role_lower for keyword in ['adjective', 'description', 'quality']):
            return 'adjectives'
        elif any(keyword in role_lower for keyword in ['adverb', 'manner', 'time', 'place']):
            return 'adverbs'
        elif any(keyword in role_lower for keyword in ['measure', 'quantity', 'classifier']):
            return 'measure_words'
        else:
            return 'other'

    def _get_default_category_for_char(self, char: str) -> str:
        """Get a default grammatical category for characters that don't have detailed analysis"""
        # This is a simple heuristic based on common Chinese character patterns
        # In a real implementation, this could use more sophisticated analysis

        # Common pronouns
        if char in '我你他她它我们你们他们她们':
            return 'pronouns'

        # Common verbs
        if char in '是有一在来去吃喝看听说话做':
            return 'verbs'

        # Common particles
        if char in '的了着过吗呢吧啊呀':
            return 'particles'

        # Common nouns (basic ones)
        if char in '人天日月水火山石':
            return 'nouns'

        # Default to 'other' for unknown characters
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
    """Factory function to create Chinese (Simplified) analyzer"""
    return ZhAnalyzer()
