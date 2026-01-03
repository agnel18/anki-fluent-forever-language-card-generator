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
        base_prompt = """MANDATORY REQUIREMENT: Analyze EVERY SINGLE CHARACTER in this Chinese sentence - NO EXCEPTIONS!

Analyze this ENTIRE Chinese (Simplified) sentence CHARACTER BY CHARACTER: SENTENCE_PLACEHOLDER

For EACH AND EVERY INDIVIDUAL CHARACTER in the sentence, provide:
- Its individual meaning and pronunciation
- Its grammatical role and function in this context (USE ONLY: pronoun, noun, verb, adjective, adverb, postposition, conjunction, interjection, particles, measure_words, other)
- How it combines with adjacent characters (if applicable)
- Common words it forms and their meanings
- Why it's important for learners

IMPORTANT: In Chinese, particles (的, 了, 着, 过, 们, etc.) should be classified as "particles".
Measure words (个, 本, 杯, etc.) should be classified as "measure_words".
Prepositions are not used in Chinese - use "other" for any spatial/temporal markers.

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with detailed character analysis for ALL characters in the sentence:
{
  "characters": [
    {
      "character": "这",
      "individual_meaning": "this (demonstrative pronoun)",
      "pronunciation": "zhè",
      "grammatical_role": "pronoun",
      "color": "#FF4444",
      "combinations": ["这个 (zhège) - this (with measure word)", "这里 (zhèlǐ) - here"],
      "importance": "Essential for indicating proximity and specificity"
    },
    {
      "character": "是",
      "individual_meaning": "to be/am/are/is (linking verb)",
      "pronunciation": "shì",
      "grammatical_role": "verb",
      "color": "#44FF44",
      "combinations": ["不是 (búshì) - is not", "还是 (háishì) - or/still"],
      "importance": "Fundamental linking verb for equations and identities"
    },
    {
      "character": "个",
      "individual_meaning": "measure word for general objects",
      "pronunciation": "gè",
      "grammatical_role": "measure_words",
      "color": "#AA44FF",
      "combinations": ["一个 (yīgè) - one (general)", "这个 (zhège) - this (general)"],
      "importance": "Essential measure word used with numbers and demonstratives"
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
    "particles": "Particles (助词) add grammatical functions like possession, aspect, and plurality",
    "sentence_structure": "Subject-Verb-Object word order with characters combining into meaningful units"
  }
}

CRITICAL: Analyze EVERY SINGLE CHARACTER in the sentence - NO EXCEPTIONS!
CRITICAL: grammatical_role MUST be EXACTLY one of these 11 values with NO variations: "pronoun", "noun", "verb", "adjective", "adverb", "postposition", "conjunction", "interjection", "particles", "measure_words", "other"
CRITICAL: For EACH character, include the EXACT color hex code from this mapping:
- pronoun: #FF4444 (red)
- noun: #FFAA00 (orange)
- verb: #44FF44 (green)
- adjective: #FF44FF (magenta)
- adverb: #44FFFF (cyan)
- postposition: #4444FF (blue)
- conjunction: #888888 (gray)
- interjection: #888888 (gray)
- particles: #AA44FF (purple)
- measure_words: #AA44FF (purple)
- other: #888888 (gray)
CRITICAL: Do NOT use descriptions like "demonstrative pronoun" or "linking verb" - use ONLY the exact words above!
CRITICAL: If unsure, use "other" rather than making up a new category!"""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_intermediate_prompt(self, sentence: str, target_word: str) -> str:
        """Generate intermediate-level grammar analysis prompt with character-level analysis"""
        base_prompt = """MANDATORY REQUIREMENT: Analyze EVERY SINGLE CHARACTER in this Chinese sentence - NO EXCEPTIONS!

Analyze this Chinese (Simplified) sentence CHARACTER BY CHARACTER for intermediate concepts: SENTENCE_PLACEHOLDER

Provide detailed analysis including:
- Aspect markers and tense expressions
- Particle functions and discourse relationships
- Measure word usage and quantification
- Complex character combinations and compound words
- Topic-comment structure patterns

IMPORTANT: Particles (的, 了, 着, 过, 们, etc.) should be classified as "particles".
Measure words (个, 本, 杯, etc.) should be classified as "measure_words".

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with comprehensive analysis:
{
  "characters": [
    {
      "character": "正",
      "individual_meaning": "just/right/correct",
      "pronunciation": "zhèng",
      "grammatical_role": "particles",
      "color": "#AA44FF",
      "combinations": ["正在 (zhèngzài) - progressive aspect 'is doing'", "正 (zhèng) - just/now"],
      "aspect_function": "Part of progressive aspect marker indicating ongoing action"
    },
    {
      "character": "在",
      "individual_meaning": "at/in/on (location particle)",
      "pronunciation": "zài",
      "grammatical_role": "particles",
      "color": "#AA44FF",
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
    "aspect_system": "Aspect markers show how actions unfold over time, not just tense",
    "particles": "Particles add grammatical functions like aspect, possession, and plurality",
    "measure_words": "Measure words quantify nouns and are required in many constructions",
    "character_combinations": "Characters combine to create complex grammatical meanings",
    "topic_comment": "Topic-comment structure where old information comes first"
  }
}

CRITICAL: grammatical_role MUST be EXACTLY one of these 11 values with NO variations: "pronoun", "noun", "verb", "adjective", "adverb", "postposition", "conjunction", "interjection", "particles", "measure_words", "other"
CRITICAL: For EACH character, include the EXACT color hex code from this mapping:
- pronoun: #FF4444 (red)
- noun: #FFAA00 (orange)
- verb: #44FF44 (green)
- adjective: #FF44FF (magenta)
- adverb: #44FFFF (cyan)
- postposition: #4444FF (blue)
- conjunction: #888888 (gray)
- interjection: #888888 (gray)
- particles: #AA44FF (purple)
- measure_words: #AA44FF (purple)
- other: #888888 (gray)
CRITICAL: Do NOT use descriptions like "aspect marker component" or "location particle" - use ONLY the exact words above!

Focus on grammatical relationships and morphological patterns."""
        return base_prompt.replace("SENTENCE_PLACEHOLDER", sentence).replace("TARGET_PLACEHOLDER", target_word)

    def _get_advanced_prompt(self, sentence: str, target_word: str) -> str:
        """Generate advanced-level grammar analysis prompt with complex morphological features"""
        base_prompt = """MANDATORY REQUIREMENT: Analyze EVERY SINGLE CHARACTER in this Chinese sentence - NO EXCEPTIONS!

Perform ADVANCED morphological and syntactic analysis of this Chinese (Simplified) sentence: SENTENCE_PLACEHOLDER

Analyze complex features including:
- Modal and discourse particles
- Complex aspectual and pragmatic functions
- Structural particles and disposal constructions
- Topic-comment structure and information flow
- Advanced measure word usage and quantification

IMPORTANT: Particles (的, 了, 着, 过, 们, 把, 被, etc.) should be classified as "particles".
Measure words should be classified as "measure_words".

Pay special attention to the target word: TARGET_PLACEHOLDER

Return a JSON object with advanced grammatical analysis:
{
  "characters": [
    {
      "character": "把",
      "individual_meaning": "to hold/grasp",
      "pronunciation": "bǎ",
      "grammatical_role": "particles",
      "color": "#AA44FF",
      "combinations": ["把字句 (bǎzìjù) - 'ba' construction for disposal/formal objects"],
      "pragmatic_function": "Introduces formal object in disposal constructions",
      "importance": "Creates topic-comment structure with object fronting"
    },
    {
      "character": "了",
      "individual_meaning": "particle indicating completion/aspect",
      "pronunciation": "le",
      "grammatical_role": "particles",
      "color": "#AA44FF",
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
    "modal_particles": "Modal particles express speaker attitude and discourse functions",
    "structural_particles": "Structural particles organize complex sentence grammar (把, 被, etc.)",
    "aspect_particles": "Aspect particles mark completion, duration, and experience (了, 着, 过)",
    "discourse_markers": "Discourse markers connect ideas and show relationships",
    "topic_comment_structure": "Topic-comment structure where topic precedes comment",
    "disposal_constructions": "把 (bǎ) and 被 (bèi) constructions for object manipulation",
    "measure_words": "Complex measure word system for precise quantification",
    "character_level_analysis": "Each character contributes to complex grammatical meanings"
  }
}

CRITICAL: grammatical_role MUST be EXACTLY one of these 11 values with NO variations: "pronoun", "noun", "verb", "adjective", "adverb", "postposition", "conjunction", "interjection", "particles", "measure_words", "other"
CRITICAL: For EACH character, include the EXACT color hex code from this mapping:
- pronoun: #FF4444 (red)
- noun: #FFAA00 (orange)
- verb: #44FF44 (green)
- adjective: #FF44FF (magenta)
- adverb: #44FFFF (cyan)
- postposition: #4444FF (blue)
- conjunction: #888888 (gray)
- interjection: #888888 (gray)
- particles: #AA44FF (purple)
- measure_words: #AA44FF (purple)
- other: #888888 (gray)
CRITICAL: Analyze EVERY SINGLE CHARACTER in the sentence - NO EXCEPTIONS!"""
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

            # CRITICAL: Check that EVERY Chinese character in the sentence is analyzed
            chinese_chars_in_sentence = set(re.findall(r'[\u4e00-\u9fff]', original_sentence))
            analyzed_chars = set()

            for char_data in characters:
                char = char_data.get('character', '')
                if char and char in chinese_chars_in_sentence:
                    analyzed_chars.add(char)

            # For Chinese, we REQUIRE 100% character coverage - every character must be analyzed
            char_coverage = len(chinese_chars_in_sentence.intersection(analyzed_chars)) / len(chinese_chars_in_sentence) if chinese_chars_in_sentence else 1.0

            # If not all characters are analyzed, this is a critical failure
            if char_coverage < 1.0:
                logger.warning(f"CRITICAL: Only {char_coverage:.1%} of Chinese characters analyzed. Missing: {chinese_chars_in_sentence - analyzed_chars}")
                return 0.3  # Very low score for incomplete character analysis

            # Calculate confidence score
            base_score = 0.9 if (has_characters and has_explanations) else 0.6
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

        # Chinese-specific grammatical role mapping
        # Order matters: primary categories before secondary descriptors
        if any(keyword in role_lower for keyword in ['particle', 'marker', 'aspect', 'modal', 'structural']):
            return 'particles'
        elif any(keyword in role_lower for keyword in ['pronoun', 'demonstrative', 'personal']):
            return 'pronouns'
        elif any(keyword in role_lower for keyword in ['verb', 'linking', 'action', 'state']) and 'noun' not in role_lower:
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
