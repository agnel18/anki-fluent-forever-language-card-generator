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
        base_prompt = """Analyze EVERY CHARACTER in this Chinese sentence: SENTENCE_PLACEHOLDER

For EACH character, provide:
- Individual meaning and pronunciation
- Grammatical role (use appropriate Chinese categories)
- Character combinations and word formation
- Color code for visualization
- Importance for learners

CHINESE GRAMMATICAL ROLES (词类) - Based on comprehensive Chinese linguistics:

CONTENT WORDS (实词):
- noun (名词): 书、桌子、北京、水、人、爱情 - Names people, things, places, concepts
- pronoun (代词): 我、你、他、这、那、谁、什么、大家 - Replaces nouns
- verb (动词): 是、吃、跑、爱、想、知道、可以 - Actions, states, changes, existence
- adjective (形容词): 大、红、好、漂亮、快乐、雪白 - Describes quality, property, state
- distinguishing_adjective (区别词): 男、女、公、私、单、双、大型 - Only used attributively
- numeral (数词): 一、二、三、第一、半、几、许多 - Expresses quantity or order
- measure_word (量词): 个、本、只、张、杯、次、群、辆 - Used with numbers to count nouns
- adverb (副词): 很、都、也、不、已经、正在、非常、马上 - Modifies verbs, adjectives, adverbs
- time_word (时间词): 今天、现在、昨天、早上、星期三 - Special nouns indicating time
- locality_word (方位词): 上面、里面、东、左、前、附近 - Special nouns indicating location/direction
- interjection (叹词): 啊、哦、哎呀、哇、嗯、嘿 - Expresses strong emotion
- onomatopoeia (拟声词): 砰、哗哗、汪汪、咚咚、叮咚 - Imitates natural sounds

FUNCTION WORDS (虚词):
- preposition (介词): 在、从、把、被、对于、关于、向、跟 - Introduces prepositional phrases
- conjunction (连词): 和、但是、因为、所以、如果、虽然、或者 - Connects words, phrases, clauses
- structural_particle (结构助词): 的、地、得、所 - Structural particles
- aspect_particle (动态助词): 了、着、过 - Aspect markers (completion, ongoing, experience)
- plural_particle (们): 们 - Plural marker
- modal_particle (语气助词): 吗、呢、吧、啊、呀、咯、喽 - Expresses mood, question, tone
- other (其他): if truly doesn't fit above

COLOR CODING (区分实词和虚词):
- noun: #FFAA00
- pronoun: #FF4444
- verb: #44FF44
- adjective: #FF44FF
- distinguishing_adjective: #FF66FF
- numeral: #FFFF44
- measure_word: #AA44FF
- adverb: #44FFFF
- time_word: #FFA500
- locality_word: #FF8C00
- preposition: #F5A623
- conjunction: #888888
- structural_particle: #9013FE
- aspect_particle: #8A2BE2
- plural_particle: #9932CC
- modal_particle: #DA70D6
- interjection: #888888
- onomatopoeia: #FFD700
- other: #AAAAAA

Pay special attention to: TARGET_PLACEHOLDER

Return JSON with character-by-character analysis:
{
  "elements": [
    {
      "word": "这",
      "individual_meaning": "this",
      "pronunciation": "zhè",
      "grammatical_role": "pronoun",
      "color": "#FF4444",
      "combinations": ["这个 - this", "这里 - here"],
      "importance": "Demonstrative pronoun for proximity"
    }
  ],
  "word_combinations": [
    {
      "word": "这本书",
      "characters": ["这", "本", "书"],
      "combined_meaning": "this book",
      "structure": "demonstrative + measure word + noun"
    }
  ],
  "explanations": {
    "character_analysis": "Each character has meaning and combines to form words",
    "particles": "Grammatical particles modify meaning and structure",
    "measure_words": "Required between numbers and nouns"
  }
}

ANALYZE EVERY CHARACTER in the sentence."""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt with character-level analysis"""
        base_prompt = """MANDATORY REQUIREMENT: Analyze EVERY SINGLE CHARACTER in this Chinese sentence - NO EXCEPTIONS!

Analyze this Chinese (Simplified) sentence CHARACTER BY CHARACTER for intermediate concepts: SENTENCE_PLACEHOLDER

Provide detailed analysis including:
- Aspect markers and tense expressions (aspect_particle)
- Particle functions and discourse relationships (modal_particle, structural_particle)
- Measure word usage and quantification (measure_word)
- Complex character combinations and compound words
- Topic-comment structure patterns

IMPORTANT: Use specific grammatical categories from the Chinese linguistics system:
- aspect_particle: 了, 着, 过 (aspect markers)
- modal_particle: 吗, 呢, 吧, 啊, 呀 (tone/mood particles)
- structural_particle: 的, 地, 得, 所 (structural particles)
- measure_word: 个, 本, 杯, 次, 张, 只 (measure/classifier words)

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with comprehensive analysis:
{
  "elements": [
    {
      "word": "正",
      "individual_meaning": "just/right/correct",
      "pronunciation": "zhèng",
      "grammatical_role": "aspect_particle",
      "color": "#8A2BE2",
      "combinations": ["正在 (zhèngzài) - progressive aspect 'is doing'", "正 (zhèng) - just/now"],
      "aspect_function": "Part of progressive aspect marker indicating ongoing action"
    },
    {
      "word": "在",
      "individual_meaning": "at/in/on (location particle)",
      "pronunciation": "zài",
      "grammatical_role": "preposition",
      "color": "#F5A623",
      "combinations": ["正在 (zhèngzài) - progressive aspect", "在北京 (zài běijīng) - in Beijing"],
      "importance": "Essential particle for location and progressive aspect"
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
    "aspect_system": "Aspect markers show how actions unfold over time",
    "particle_types": "Structural (的), aspect (了/着/过), modal (吗/呢), plural (们)",
    "measure_words": "Required between numbers and nouns",
    "content_vs_function": "实词 (content) vs 虚词 (function) words"
  }
}

Focus on grammatical relationships and character combinations."""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt with complex morphological features"""
        base_prompt = """MANDATORY REQUIREMENT: Analyze EVERY SINGLE CHARACTER in this Chinese sentence - NO EXCEPTIONS!

Perform ADVANCED morphological and syntactic analysis of this Chinese (Simplified) sentence: SENTENCE_PLACEHOLDER

Analyze complex features including:
- Modal and discourse particles (modal_particle)
- Complex aspectual and pragmatic functions (aspect_particle)
- Structural particles and disposal constructions (structural_particle)
- Topic-comment structure and information flow
- Advanced measure word usage and quantification (measure_word)

IMPORTANT: Use specific grammatical categories from the Chinese linguistics system:
- structural_particle: 的, 地, 得, 所, 把, 被 (structural particles, disposal constructions)
- aspect_particle: 了, 着, 过 (aspect markers for completion, duration, experience)
- modal_particle: 吗, 呢, 吧, 啊, 呀, 咯, 喽 (tone, mood, discourse particles)
- measure_word: 个, 本, 杯, 次, 张, 只, 群, 辆 (measure/classifier words)

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with advanced grammatical analysis:
{
  "elements": [
    {
      "word": "把",
      "individual_meaning": "to hold/grasp",
      "pronunciation": "bǎ",
      "grammatical_role": "structural_particle",
      "color": "#9013FE",
      "combinations": ["把字句 (bǎzìjù) - 'ba' construction for disposal/formal objects"],
      "pragmatic_function": "Introduces formal object in disposal constructions",
      "importance": "Creates topic-comment structure with object fronting"
    },
    {
      "word": "了",
      "individual_meaning": "particle indicating completion/aspect",
      "pronunciation": "le",
      "grammatical_role": "aspect_particle",
      "color": "#8A2BE2",
      "combinations": ["吃了 (chīle) - ate (completed action)", "去了 (qùle) - went (completed)"],
      "aspect_function": "Perfective aspect particle indicating completed action",
      "importance": "Essential for aspect marking and sentence completion"
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
    "modal_particles": "Express speaker attitude and discourse functions (吗, 呢, 吧, 啊, 呀)",
    "structural_particles": "Organize complex sentence grammar (的, 地, 得, 把, 被, 所)",
    "aspect_particles": "Mark completion, duration, experience (了, 着, 过)",
    "particle_subtypes": "Structural, aspect, modal, plural particles with distinct functions",
    "disposal_constructions": "把 (bǎ) and 被 (bèi) constructions for object fronting",
    "content_vs_function": "实词 (content words) vs 虚词 (function words) distinction"
  }
}

ANALYZE EVERY CHARACTER in the sentence."""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Parse AI response into structured Chinese character-level grammar analysis"""
        try:
            # Try to extract JSON from markdown code blocks first
            json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(1)
                    parsed = json.loads(json_str)
                    # Add the sentence to the parsed data
                    parsed['sentence'] = sentence
                    logger.info(f"Chinese analyzer parsed JSON from markdown successfully: {len(parsed.get('characters', []))} characters")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Chinese analyzer (markdown): {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

            # Try to extract JSON from response - look for JSON object after text
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    parsed = json.loads(json_str)
                    # Add the sentence to the parsed data
                    parsed['sentence'] = sentence
                    logger.info(f"Chinese analyzer parsed JSON successfully: {len(parsed.get('characters', []))} characters")
                    return self._transform_to_standard_format(parsed, complexity)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error in Chinese analyzer: {e}")
                    logger.error(f"Extracted JSON string: {json_str[:500]}...")

            # Try direct JSON parsing
            try:
                parsed = json.loads(ai_response)
                parsed['sentence'] = sentence
                logger.info(f"Chinese analyzer direct JSON parse successful: {len(parsed.get('characters', []))} characters")
                return self._transform_to_standard_format(parsed, complexity)
            except json.JSONDecodeError:
                pass

            # Fallback: extract structured information from text
            logger.warning("Chinese analyzer falling back to text parsing")
            fallback_parsed = self._parse_text_response(ai_response, sentence)
            return self._transform_to_standard_format(fallback_parsed, complexity)

        except Exception as e:
            logger.error(f"Failed to parse {self.language_name} grammar response: {e}")
            fallback_parsed = self._create_fallback_parse(ai_response, sentence)
            return self._transform_to_standard_format(fallback_parsed, complexity)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return comprehensive color scheme for Chinese grammatical elements based on linguistic categories"""
        schemes = {
            "beginner": {
                # Content words (实词)
                "noun": "#FFAA00",                    # Orange - Things/objects
                "pronoun": "#FF4444",                 # Red - People/references
                "verb": "#44FF44",                    # Green - Actions/states
                "adjective": "#FF44FF",               # Magenta - Descriptions
                "distinguishing_adjective": "#FF66FF", # Light Magenta - Special adjectives
                "numeral": "#FFFF44",                 # Yellow - Numbers
                "measure_word": "#AA44FF",            # Purple - Quantity words
                "adverb": "#44FFFF",                  # Cyan - How/when/where
                "time_word": "#FFA500",               # Orange-red - Time
                "locality_word": "#FF8C00",           # Dark orange - Location/direction
                "interjection": "#FFD700",            # Gold - Emotion
                "onomatopoeia": "#FFD700",            # Gold - Sound imitation

                # Function words (虚词)
                "preposition": "#F5A623",             # Orange - Prepositions
                "conjunction": "#888888",             # Gray - Connectors
                "structural_particle": "#9013FE",     # Purple - Structure
                "aspect_particle": "#8A2BE2",         # Blue-violet - Aspect
                "plural_particle": "#9932CC",         # Dark orchid - Plural
                "modal_particle": "#DA70D6",          # Plum - Modal
                "other": "#AAAAAA"                    # Light gray - Other
            },
            "intermediate": {
                # Content words (实词)
                "noun": "#FFAA00",
                "pronoun": "#FF4444",
                "verb": "#44FF44",
                "adjective": "#FF44FF",
                "distinguishing_adjective": "#FF66FF",
                "numeral": "#FFFF44",
                "measure_word": "#AA44FF",
                "adverb": "#44FFFF",
                "time_word": "#FFA500",
                "locality_word": "#FF8C00",
                "interjection": "#FFD700",
                "onomatopoeia": "#FFD700",

                # Function words (虚词)
                "preposition": "#F5A623",
                "conjunction": "#888888",
                "structural_particle": "#9013FE",
                "aspect_particle": "#8A2BE2",
                "plural_particle": "#9932CC",
                "modal_particle": "#DA70D6",
                "other": "#AAAAAA"
            },
            "advanced": {
                # Content words (实词)
                "noun": "#FFAA00",
                "pronoun": "#FF4444",
                "verb": "#44FF44",
                "adjective": "#FF44FF",
                "distinguishing_adjective": "#FF66FF",
                "numeral": "#FFFF44",
                "measure_word": "#AA44FF",
                "adverb": "#44FFFF",
                "time_word": "#FFA500",
                "locality_word": "#FF8C00",
                "interjection": "#FFD700",
                "onomatopoeia": "#FFD700",

                # Function words (虚词) - more distinctions
                "preposition": "#F5A623",
                "conjunction": "#888888",
                "structural_particle": "#9013FE",
                "aspect_particle": "#8A2BE2",
                "plural_particle": "#9932CC",
                "modal_particle": "#DA70D6",
                "other": "#AAAAAA"
            }
        }

        if complexity not in schemes:
            complexity = "beginner"

        return schemes[complexity]

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Chinese character-level grammar analysis quality (85% threshold required)"""

        try:
            # Check if essential elements are present
            elements = parsed_data.get('elements', [])
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            # Basic validation checks
            has_elements = len(elements) > 0
            has_combinations = len(word_combinations) > 0
            has_explanations = len(explanations) > 0

            # Handle both dict format (from test) and list format (from actual parsing)
            element_items = []
            if isinstance(elements, dict):
                # Dict format: {'nouns': [...], 'verbs': [...]}
                for category_items in elements.values():
                    if isinstance(category_items, list):
                        element_items.extend(category_items)
            elif isinstance(elements, list):
                # List format: [{'word': '...', ...}, ...]
                element_items = elements

            # CRITICAL: Check that EVERY Chinese character in the sentence is analyzed
            chinese_chars_in_sentence = set(re.findall(r'[\u4e00-\u9fff]', original_sentence))
            analyzed_chars = set()

            for element_data in element_items:
                word = element_data.get('word', '')
                # Add all characters from the word
                for char in word:
                    if char in chinese_chars_in_sentence:
                        analyzed_chars.add(char)

            # For Chinese, we REQUIRE 100% character coverage - every character must be analyzed
            char_coverage = len(chinese_chars_in_sentence.intersection(analyzed_chars)) / len(chinese_chars_in_sentence) if chinese_chars_in_sentence else 1.0

            # If sentence has no Chinese characters, return low confidence
            if not chinese_chars_in_sentence:
                return 0.1

            # If not all characters are analyzed, this is a critical failure
            if char_coverage < 1.0:
                logger.warning(f"CRITICAL: Only {char_coverage:.1%} of Chinese characters analyzed. Missing: {chinese_chars_in_sentence - analyzed_chars}")
                return 0.3  # Very low score for incomplete character analysis

            # Calculate confidence score
            base_score = 0.9 if (has_elements and has_explanations) else 0.6
            coverage_bonus = char_coverage * 0.1  # Bonus for complete coverage
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
        """Generate HTML output for Chinese text with character-level coloring using colors from word_explanations (single source of truth)"""
        explanations = parsed_data.get('word_explanations', [])

        logger.info(f"DEBUG Chinese HTML Gen - Input explanations count: {len(explanations)}")
        logger.info(f"DEBUG Chinese HTML Gen - Input sentence: '{sentence}'")

        # Create mapping of characters to colors directly from word_explanations (authoritative source)
        char_to_color = {}
        for exp in explanations:
            if len(exp) >= 3:
                char, pos, color = exp[0], exp[1], exp[2]
                char_to_color[char] = color
                logger.info(f"DEBUG Chinese HTML Gen - Character '{char}' -> Color '{color}' (POS: '{pos}')")

        logger.info(f"DEBUG Chinese HTML Gen - Character-to-color mapping: {char_to_color}")

        # Generate HTML by coloring each character individually using colors from grammar explanations
        html_parts = []
        for char in sentence:
            if char in char_to_color:
                color = char_to_color[char]
                html_parts.append(f'<span style="color: {color}; font-weight: bold;">{char}</span>')
                logger.info(f"DEBUG Chinese HTML Gen - ✓ Colored character '{char}' with color '{color}'")
            elif char.strip():  # Only add non-whitespace characters without color
                # For characters without analysis, use default color (should be rare with new architecture)
                html_parts.append(f'<span style="color: #888888;">{char}</span>')
                logger.warning(f"DEBUG Chinese HTML Gen - ✗ No color found for character '{char}' (clean: '{char}'). Available characters: {list(char_to_color.keys())}")
            else:
                # Preserve whitespace
                html_parts.append(char)

        result = ''.join(html_parts)
        logger.info(f"DEBUG Chinese HTML Gen - Final HTML output length: {len(result)}")
        logger.info(f"DEBUG Chinese HTML Gen - Final HTML preview: {result[:300]}...")
        return result

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map grammatical role descriptions to color category names using Chinese grammar rules"""
        role_lower = grammatical_role.lower()

        # Chinese-specific grammatical role mapping - updated for 16-category system
        # Content words (实词) - primary categories - ORDER MATTERS: more specific first
        if any(keyword in role_lower for keyword in ['pronoun', 'demonstrative', 'personal', 'reflexive']):
            return 'pronoun'
        elif any(keyword in role_lower for keyword in ['noun', 'object', 'subject', 'thing', 'place', 'name']):
            return 'noun'
        elif any(keyword in role_lower for keyword in ['verb', 'linking', 'action', 'state', 'predicate']) and 'noun' not in role_lower:
            return 'verb'
        elif any(keyword in role_lower for keyword in ['adjective', 'description', 'quality', 'attribute']):
            return 'adjective'
        elif any(keyword in role_lower for keyword in ['distinguishing_adjective', 'differentiating', 'distinguishing']):
            return 'distinguishing_adjective'
        elif any(keyword in role_lower for keyword in ['numeral', 'number', 'cardinal', 'ordinal']):
            return 'numeral'
        elif any(keyword in role_lower for keyword in ['measure_word', 'measure', 'classifier', 'counter']):
            return 'measure_word'
        elif any(keyword in role_lower for keyword in ['adverb', 'manner', 'degree', 'frequency']):
            return 'adverb'
        elif any(keyword in role_lower for keyword in ['time_word', 'time', 'temporal', 'duration']):
            return 'time_word'
        elif any(keyword in role_lower for keyword in ['locality_word', 'locality', 'location', 'direction', 'spatial']):
            return 'locality_word'
        elif any(keyword in role_lower for keyword in ['interjection', 'exclamation', 'emotion', 'feeling']):
            return 'interjection'
        elif any(keyword in role_lower for keyword in ['onomatopoeia', 'sound', 'imitative', 'mimicry']):
            return 'onomatopoeia'

        # Function words (虚词) - secondary categories
        elif any(keyword in role_lower for keyword in ['preposition', 'prepositional']):
            return 'preposition'
        elif any(keyword in role_lower for keyword in ['conjunction', 'connective', 'coordinating', 'subordinating']):
            return 'conjunction'
        elif any(keyword in role_lower for keyword in ['structural_particle', 'structural', 'possessive', 'attributive']):
            return 'structural_particle'
        elif any(keyword in role_lower for keyword in ['aspect_particle', 'aspect', 'progressive', 'perfective', 'experiential']):
            return 'aspect_particle'
        elif any(keyword in role_lower for keyword in ['plural_particle', 'plural', 'collective']):
            return 'plural_particle'
        elif any(keyword in role_lower for keyword in ['modal_particle', 'modal', 'tone', 'emphasis', 'question']):
            return 'modal_particle'

        # Fallback for legacy categories or unrecognized roles
        elif any(keyword in role_lower for keyword in ['particle', 'marker']) and not any(specific in role_lower for specific in ['aspect', 'modal', 'structural', 'plural']):
            return 'structural_particle'  # Default particle type
        elif 'other' in role_lower or 'unknown' in role_lower:
            return 'other'

        # Default fallback
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

    def _standardize_color(self, ai_color: str, category: str) -> str:
        """Standardize AI-provided color to ensure consistency with the defined color scheme"""
        # Define the exact color mapping that should be used (including Chinese-specific extensions)
        standard_colors = {
            "pronouns": "#FF4444",         # Red
            "nouns": "#FFAA00",            # Orange
            "verbs": "#44FF44",            # Green
            "adjectives": "#FF44FF",       # Magenta
            "adverbs": "#44FFFF",          # Cyan
            "postpositions": "#4444FF",    # Blue
            "conjunctions": "#888888",     # Gray
            "interjections": "#888888",    # Gray
            "particles": "#AA44FF",        # Purple (Chinese-specific)
            "measure_words": "#AA44FF",    # Purple (Chinese-specific)
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

    def _transform_to_standard_format(self, parsed_data: Dict[str, Any], complexity: str = 'beginner') -> Dict[str, Any]:
        """Transform Chinese analyzer output to standard BaseGrammarAnalyzer format
        
        CRITICAL: For Chinese, EVERY character in the sentence MUST be analyzed and included.
        This is essential for character-based languages where each character carries meaning.
        """
        try:
            # Extract original data
            characters = parsed_data.get('characters', [])
            word_combinations = parsed_data.get('word_combinations', [])
            explanations = parsed_data.get('explanations', {})

            logger.info(f"Chinese analyzer transforming {len(characters)} characters")
            if characters:
                sample_roles = [c.get('grammatical_role', 'MISSING') for c in characters[:3]]
                logger.info(f"Sample grammatical roles: {sample_roles}")

            # CRITICAL VALIDATION: Ensure all characters from the sentence are present
            sentence = parsed_data.get('sentence', '')
            chinese_chars_in_sentence = set(re.findall(r'[\u4e00-\u9fff]', sentence))
            analyzed_chars = set(c.get('character', '') for c in characters)
            
            missing_chars = chinese_chars_in_sentence - analyzed_chars
            if missing_chars:
                logger.error(f"CRITICAL: Missing character analysis for: {missing_chars}")
                # Add missing characters with 'other' role
                for missing_char in missing_chars:
                    characters.append({
                        'character': missing_char,
                        'individual_meaning': f'Character {missing_char} (analysis incomplete)',
                        'pronunciation': 'unknown',
                        'grammatical_role': 'other',
                        'combinations': [],
                        'importance': 'Automatically added - analysis was incomplete'
                    })
                    logger.warning(f"Added missing character '{missing_char}' with 'other' role")

            # Transform characters into elements grouped by grammatical role
            elements = {}

            # Group characters by their grammatical role
            for char_data in characters:
                grammatical_role = char_data.get('grammatical_role', 'other')
                logger.debug(f"Processing character '{char_data.get('character', 'UNKNOWN')}' with role '{grammatical_role}'")
                if grammatical_role not in elements:
                    elements[grammatical_role] = []
                elements[grammatical_role].append(char_data)

            # Add word combinations as a special category
            if word_combinations:
                elements['word_combinations'] = word_combinations

            # Create word_explanations for HTML coloring: [character, pos, color, explanation]
            word_explanations = []
            colors = self.get_color_scheme(complexity)  # Use the actual complexity level

            logger.info(f"DEBUG Chinese Transform - Color scheme for complexity '{complexity}': {colors}")

            for char_data in characters:
                character = char_data.get('character', '')
                grammatical_role = char_data.get('grammatical_role', 'other')
                individual_meaning = char_data.get('individual_meaning', '')
                pronunciation = char_data.get('pronunciation', '')
                
                # Ensure grammatical_role is a string
                if not isinstance(grammatical_role, str):
                    logger.warning(f"grammatical_role is not a string: {grammatical_role} (type: {type(grammatical_role)}), defaulting to 'other'")
                    grammatical_role = 'other'
                category = self._map_grammatical_role_to_category(grammatical_role)
                color = colors.get(category, '#888888')
                
                # Override with AI-provided color if available and standardize it
                ai_color = char_data.get('color')
                if ai_color:
                    color = self._standardize_color(ai_color, category)
                
                logger.info(f"DEBUG Chinese Transform - Character: '{character}', Role: '{grammatical_role}', Category: '{category}', Color: '{color}'")
                
                # Create explanation text from available data
                explanation_parts = []
                if individual_meaning:
                    explanation_parts.append(individual_meaning)
                if pronunciation:
                    explanation_parts.append(f"({pronunciation})")
                
                explanation = ", ".join(explanation_parts) if explanation_parts else f"{grammatical_role}"
                
                word_explanations.append([character, grammatical_role, color, explanation])
                logger.info(f"DEBUG Chinese Transform - Added character_explanation: {word_explanations[-1]}")

            logger.info(f"DEBUG Chinese Transform - Final word_explanations count: {len(word_explanations)}")

            # Return in standard format expected by BaseGrammarAnalyzer
            return {
                'elements': elements,
                'explanations': explanations,
                'word_explanations': word_explanations,
                'sentence': parsed_data.get('sentence', '')
            }

        except Exception as e:
            logger.error(f"Failed to transform Chinese analysis data: {e}")
            return {
                'elements': {},
                'explanations': {'error': 'Data transformation failed'},
                'word_explanations': [],
                'sentence': parsed_data.get('sentence', '')
            }

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
