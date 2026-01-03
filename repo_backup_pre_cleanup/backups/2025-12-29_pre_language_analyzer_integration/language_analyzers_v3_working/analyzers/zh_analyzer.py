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
        """Generate beginner-level grammar analysis prompt with detailed explanations"""
        base_prompt = """Analyze this Chinese (Simplified) sentence in detail: SENTENCE_PLACEHOLDER

For EACH character/word, provide:
- Its grammatical role and function
- What it means in this context
- How it's used in Chinese grammar
- Common alternate uses or forms
- Why it's important for learners

Focus on the target word: TARGET_PLACEHOLDER

Return a JSON object with detailed analysis:
{
  "elements": {
    "pronouns": [{"word": "你", "function": "subject pronoun", "meaning": "you (singular)", "usage": "Used as sentence subject", "alternates": "您(formal), 你们(plural)"}],
    "verbs": [{"word": "是", "function": "linking verb", "meaning": "to be/am/are/is", "usage": "Links subject to description", "alternates": "等于(equals), 成为(become)"}],
    "particles": [{"word": "的", "function": "possessive particle", "meaning": "possessive marker", "usage": "Shows ownership/relationship", "alternates": "地(adverbial), 得(complement)"}],
    "nouns": [{"word": "朋友", "function": "object noun", "meaning": "friend", "usage": "Direct object of sentence", "alternates": "好友(close friend), 老友(old friend)"}]
  },
  "explanations": {
    "pronouns": "Pronouns replace nouns and show person/number. '你' is the informal 'you' used with peers",
    "verbs": "Verbs show actions or states. '是' links subjects to their identities/descriptions",
    "particles": "Particles modify relationships. '的' shows possession but has multiple uses",
    "nouns": "Nouns name people/places/things. Learn measure words and plural forms",
    "sentence_structure": "Subject-Verb-Object word order with particles showing relationships"
  }
}

Provide specific, educational explanations for language learning!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt"""
        base_prompt = """Analyze this Chinese (Simplified) sentence for intermediate grammatical concepts: SENTENCE_PLACEHOLDER

Focus on:
        - Aspect markers and temporal relationships
        - Complex particle usage

Return a JSON object with:
{
  "elements": {
    "topics": [{"word": "我", "function": "topic/subject"}],
    "predicates": [{"word": "吃", "function": "main verb"}],
    "possessive_particles": [{"word": "的", "function": "possessive particle"}],
    "aspect_markers": [{"word": "正在", "function": "progressive aspect"}],
    "perfective_markers": [{"word": "了", "function": "perfective aspect"}],
    "question_particles": [{"word": "吗", "function": "question particle"}]
  },
  "explanations": {
    "topics": "Topics (主题) are the core elements being discussed in the sentence",
    "predicates": "Predicates (谓语) express actions or states about the topics",
    "possessive_particles": "Possessive particles (的) show relationships and ownership",
    "aspect_markers": "Aspect markers indicate how actions unfold over time",
    "perfective_markers": "Perfective markers indicate completed actions",
    "question_particles": "Question particles (吗/呢) turn statements into questions",
    "sentence_structure": "Intermediate sentence structure with aspect markers"
  }
}

Be precise and focus on the target word: TARGET_PLACEHOLDER"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt"""
        base_prompt = """Perform advanced grammatical analysis of this Chinese (Simplified) sentence: SENTENCE_PLACEHOLDER

Analyze:
        - Modal and discourse particles
        - Complex aspectual and pragmatic functions

Return a JSON object with:
{
  "elements": {
    "topics": [{"word": "我", "function": "topic/subject"}],
    "predicates": [{"word": "吃", "function": "main verb"}],
    "possessive_particles": [{"word": "的", "function": "attributive particle"}],
    "aspect_markers": [{"word": "正在", "function": "progressive aspect"}],
    "perfective_markers": [{"word": "了", "function": "perfective aspect"}],
    "modal_particles": [{"word": "吧", "function": "suggestion particle"}],
    "structural_particles": [{"word": "把", "function": "structural particle"}],
    "discourse_markers": [{"word": "但是", "function": "contrast marker"}],
    "sentence_final_particles": [{"word": "呢", "function": "emphasis particle"}]
  },
  "explanations": {
    "topics": "Topics (主题) are the core elements being discussed in the sentence",
    "predicates": "Predicates (谓语) express actions or states about the topics",
    "possessive_particles": "Possessive particles (的) show relationships and ownership",
    "aspect_markers": "Aspect markers indicate how actions unfold over time",
    "perfective_markers": "Perfective markers indicate completed actions",
    "modal_particles": "Modal particles express speaker attitude and discourse functions",
    "structural_particles": "Structural particles organize sentence grammar",
    "discourse_markers": "Discourse markers connect ideas and show relationships",
    "sentence_final_particles": "Sentence-final particles add emphasis or tone",
    "aspect_system": "Complex aspectual distinctions and temporal relationships",
    "discourse_structure": "Advanced discourse organization and pragmatic functions"
  }
}

Be precise and focus on the target word: TARGET_PLACEHOLDER"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured Chinese (Simplified) grammar analysis"""
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
        """Validate Chinese (Simplified) grammar analysis quality (85% threshold required)"""

        try:
            # Check if essential elements are present
            elements = parsed_data.get('elements', {})
            explanations = parsed_data.get('explanations', {})

            # Basic validation checks
            has_elements = len(elements) > 0
            has_explanations = len(explanations) > 0

            # Check if target word appears in analysis
            sentence_words = set(original_sentence.lower().split())
            analyzed_words = set()

            for element_list in elements.values():
                for item in element_list:
                    if isinstance(item, dict) and 'word' in item:
                        analyzed_words.add(item['word'].lower())

            word_coverage = len(sentence_words.intersection(analyzed_words)) / len(sentence_words)

            # Calculate confidence score
            base_score = 0.9 if (has_elements and has_explanations) else 0.6
            coverage_bonus = word_coverage * 0.1

            confidence = min(base_score + coverage_bonus, 1.0)

            return confidence

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return 0.5  # Conservative fallback


    def _parse_text_response(self, ai_response: str, sentence: str) -> Dict[str, Any]:
        """Parse text response when JSON extraction fails - extract Chinese grammatical elements"""
        try:
            # Initialize empty structure
            elements = {}
            explanations = {}

            # Extract sentence (first line or first 100 chars)
            sentence = ai_response.split('\n')[0].strip()
            if len(sentence) > 100:
                sentence = sentence[:100] + "..."

            # Look for grammatical element patterns in text
            text_lower = ai_response.lower()

            # Map Chinese grammatical functions to categories
            category_mappings = {
                "topics": ["topic", "subject", "主语", "主题"],
                "predicates": ["predicate", "verb", "predicate", "谓语", "动词"],
                "possessive_particles": ["possessive", "的", "de", "attributive", "定语"],
                "aspect_markers": ["aspect", "progressive", "perfective", "着", "了", "过"],
                "question_particles": ["question", "吗", "呢", "吧", "interrogative"],
                "modal_particles": ["modal", "呢", "吧", "嘛", "呀", "attitude"],
                "structural_particles": ["structural", "把", "被", "给", "structural"],
                "discourse_markers": ["discourse", "但是", "而且", "所以", "不过", "connective"],
                "sentence_final_particles": ["sentence final", "sentence-final", "final particle", "语气词"]
            }

            # Extract elements by looking for patterns
            for category, keywords in category_mappings.items():
                category_elements = []
                for keyword in keywords:
                    if keyword in text_lower:
                        # Try to find associated words near the keyword
                        keyword_index = text_lower.find(keyword)
                        if keyword_index >= 0:
                            # Extract surrounding context (simple approach)
                            start = max(0, keyword_index - 50)
                            end = min(len(ai_response), keyword_index + 50)
                            context = ai_response[start:end]

                            # Look for Chinese characters in context
                            chinese_chars = re.findall(r'[\u4e00-\u9fff]+', context)
                            if chinese_chars:
                                for char in chinese_chars[:2]:  # Limit to 2 per category
                                    if len(char) >= 1:  # At least 1 character
                                        category_elements.append({
                                            "word": char,
                                            "function": f"{keyword} ({category})"
                                        })

                if category_elements:
                    elements[category] = category_elements

            # Generate explanations based on found elements
            if elements:
                for category in elements.keys():
                    if category == "topics":
                        explanations[category] = "Topics (主题) are the core elements being discussed in the sentence"
                    elif category == "predicates":
                        explanations[category] = "Predicates (谓语) express actions or states about the topics"
                    elif category == "possessive_particles":
                        explanations[category] = "Possessive particles (的) show relationships and ownership"
                    elif category == "aspect_markers":
                        explanations[category] = "Aspect markers indicate how actions unfold over time"
                    elif category == "question_particles":
                        explanations[category] = "Question particles (吗/呢) turn statements into questions"
                    elif category == "modal_particles":
                        explanations[category] = "Modal particles express speaker attitude and tone"
                    elif category == "structural_particles":
                        explanations[category] = "Structural particles organize sentence grammar"
                    elif category == "discourse_markers":
                        explanations[category] = "Discourse markers connect ideas and show relationships"
                    elif category == "sentence_final_particles":
                        explanations[category] = "Sentence-final particles add emphasis or tone"

            return {
                'sentence': sentence,
                'elements': elements,
                'explanations': explanations
            }

        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            return self._create_fallback_parse(ai_response, sentence)


    def _generate_html_output(self, parsed_data: Dict[str, Any], sentence: str, complexity: str) -> str:
        """Generate HTML output for Chinese text with character-level coloring"""
        colors = self.get_color_scheme(complexity)
        elements = parsed_data.get('elements', {})
        sentence = parsed_data.get('sentence', '')

        # Create a mapping of each character to its grammatical category
        char_to_category = {}

        # Build character-to-category mapping
        for element_type, element_list in elements.items():
            for element in element_list:
                word = element.get('word', '')
                if word:
                    # For Chinese, each character in a word gets the same category
                    for char in word:
                        if char.strip():  # Skip empty characters
                            char_to_category[char] = element_type

        # Generate HTML by coloring each character individually
        html_parts = []
        for char in sentence:
            if char in char_to_category:
                category = char_to_category[char]
                color = colors.get(category, '#CCCCCC')
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{char}</span>')
            elif char.strip():  # Only add non-whitespace characters without color
                html_parts.append(char)

        return ''.join(html_parts)


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
