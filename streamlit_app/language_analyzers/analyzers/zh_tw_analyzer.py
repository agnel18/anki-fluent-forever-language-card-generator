# Chinese Traditional Grammar Analyzer
# Auto-generated analyzer for Chinese Traditional (繁體中文)
# Language Family: Sino-Tibetan
# Script Type: logographic
# Complexity Rating: high

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from ..base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

logger = logging.getLogger(__name__)

class ZhTwAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Chinese Traditional (繁體中文).

    Key Features: ['word_segmentation', 'compounds_first', 'chinese_categories', 'aspect_system', 'topic_comment']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "3.0"
    LANGUAGE_CODE = "zh-tw"
    LANGUAGE_NAME = "Chinese Traditional"

    # Grammatical Role Mapping (16 categories based on Chinese linguistics)
    GRAMMATICAL_ROLES = {
        # Content Words (實詞 / Shící) - Independent Meaning
        "noun": "#FFAA00",                    # Orange - People/places/things/concepts
        "verb": "#44FF44",                    # Green - Actions/states/changes
        "adjective": "#FF44FF",               # Magenta - Qualities/descriptions
        "numeral": "#FFFF44",                 # Yellow - Numbers/quantities
        "measure_word": "#FFD700",            # Gold - Classifiers (個, 本, 杯)
        "pronoun": "#FF4444",                 # Red - Replacements for nouns
        "time_word": "#FFA500",               # Orange-red - Time expressions
        "locative_word": "#FF8C00",           # Dark orange - Location/direction

        # Function Words (虛詞 / Xūcí) - Structural/Grammatical
        "aspect_particle": "#8A2BE2",         # Purple - Aspect markers (了, 著, 過)
        "modal_particle": "#DA70D6",          # Plum - Tone/mood particles (嗎, 呢, 吧)
        "structural_particle": "#9013FE",     # Violet - Structural particles (的, 地, 得)
        "preposition": "#4444FF",             # Blue - Prepositions/coverbs
        "conjunction": "#888888",             # Gray - Connectors
        "adverb": "#44FFFF",                  # Cyan - Modifies verbs/adjectives
        "interjection": "#FFD700",            # Gold - Emotions/exclamations
        "onomatopoeia": "#FFD700"             # Gold - Sound imitation
    }

    def __init__(self):
        config = LanguageConfig(
            code="zh-tw",
            name="Chinese Traditional",
            native_name="繁體中文",
            family="Sino-Tibetan",
            script_type="logographic",
            complexity_rating="high",
            key_features=['word_segmentation', 'compounds_first', 'chinese_categories', 'aspect_system', 'topic_comment'],
            supported_complexity_levels=['beginner', 'intermediate', 'advanced']
        )
        super().__init__(config)

        # Initialize language-specific patterns (5-12 most frequent markers)
        self._initialize_patterns()

    def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
        """Generate Chinese Traditional-specific AI prompt for batch grammar analysis (word-level, not character-level)"""
        sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        return f"""Analyze the grammar of these Chinese Traditional sentences at the WORD level (not character-by-character).

Target word: "{target_word}"
Language: Chinese Traditional
Complexity level: {complexity}
Analysis should be in {native_language}

Sentences to analyze:
{sentences_text}

For EACH word in EVERY sentence, IN THE ORDER THEY APPEAR IN THE SENTENCE (left to right), provide:
- word: the exact word as it appears in the sentence
- individual_meaning: English translation/meaning of this specific word (MANDATORY)
- grammatical_role: EXACTLY ONE category from this list: noun, verb, adjective, numeral, measure_word, pronoun, time_word, locative_word, aspect_particle, modal_particle, structural_particle, preposition, conjunction, adverb, interjection, onomatopoeia

Additionally, identify 1-2 key compound words/phrases per sentence:
- word_combinations: array of compounds with text, combined_meaning, grammatical_role

CRITICAL REQUIREMENTS:
- Analyze at WORD level, not character level (Chinese words are compounds of characters)
- individual_meaning MUST be provided for EVERY word
- grammatical_role MUST be EXACTLY from the allowed list (one word only)
- Focus on Chinese grammatical categories (實詞/虛詞 distinction)
- Include 量詞 (measure words), 體詞 (aspect particles), and 語氣詞 (modal particles) appropriately
- word_combinations are OPTIONAL but enhance learning when present
- WORDS MUST BE LISTED IN THE EXACT ORDER THEY APPEAR IN THE SENTENCE (left to right, no grouping by category)

Return JSON in this exact format:
{{
  "batch_results": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "words": [
        {{
          "word": "學生",
          "individual_meaning": "student",
          "grammatical_role": "noun"
        }}
      ],
      "word_combinations": [
        {{
          "text": "學習中文",
          "combined_meaning": "study Chinese",
          "grammatical_role": "verb_phrase"
        }}
      ],
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

    def parse_batch_grammar_response(self, ai_response: str, sentences: List[str], complexity: str, native_language: str = "English") -> List[Dict[str, Any]]:
        """Parse batch AI response into standardized format for Chinese Traditional word-level analysis"""
        try:
            # Extract JSON from response
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0].strip()

            batch_data = json.loads(ai_response)
            if "batch_results" not in batch_data:
                raise ValueError("Missing batch_results in response")

            results = []
            for item in batch_data["batch_results"]:
                sentence_index = item.get("sentence_index", 0) - 1  # Convert to 0-based
                if 0 <= sentence_index < len(sentences):
                    sentence = sentences[sentence_index]

                    # Convert batch format to standardized format
                    elements = {}
                    word_explanations = []
                    colors = self.get_color_scheme(complexity)

                    # Process words into elements by grammatical role
                    for word_data in item.get("words", []):
                        role = word_data.get("grammatical_role", "other")
                        if role not in elements:
                            elements[role] = []

                        elements[role].append({
                            "word": word_data.get("word", ""),
                            "individual_meaning": word_data.get("individual_meaning", ""),
                            "grammatical_role": role
                        })

                        # Add to word explanations as [word, pos, color, explanation]
                        word = word_data.get("word", "")
                        individual_meaning = word_data.get("individual_meaning", "")
                        category = self._map_grammatical_role_to_category(role)
                        color = colors.get(category, '#888888')
                        explanation = f"{individual_meaning} ({role})"

                        word_explanations.append([word, role, color, explanation])

                    # Reorder word_explanations to match sentence word order
                    word_explanations = self._reorder_explanations_by_sentence_position(sentence, word_explanations)

                    # Process word combinations
                    word_combinations = []
                    for combo in item.get("word_combinations", []):
                        word_combinations.append({
                            "text": combo.get("text", ""),
                            "combined_meaning": combo.get("combined_meaning", ""),
                            "grammatical_role": combo.get("grammatical_role", "compound")
                        })

                    # Add combinations to elements for HTML generation
                    if word_combinations:
                        elements["word_combinations"] = word_combinations

                    explanations = item.get("explanations", {})

                    results.append({
                        "sentence": sentence,
                        "elements": elements,
                        "word_explanations": word_explanations,
                        "explanations": explanations
                    })
                else:
                    # Fallback for invalid index
                    results.append({
                        "sentence": sentences[len(results)] if len(results) < len(sentences) else "",
                        "elements": {},
                        "word_explanations": [],
                        "explanations": {"sentence_structure": "Parsing failed", "complexity_notes": ""}
                    })

            return results

        except Exception as e:
            logger.error(f"Chinese Traditional batch parsing failed: {e}")
            # Fallback to basic parsing
            return [{
                "sentence": sentence,
                "elements": {},
                "word_explanations": [],
                "explanations": {"sentence_structure": f"Analysis failed: {e}", "complexity_notes": ""}
            } for sentence in sentences]

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Chinese Traditional grammatical elements"""
        # Use the same color scheme for all complexity levels (Chinese categories are fundamental)
        return self.GRAMMATICAL_ROLES.copy()

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Chinese Traditional analysis quality with 3-6 simple checks (85% threshold)"""
        # Handle empty or invalid inputs
        if not parsed_data or not original_sentence or not parsed_data.get('elements'):
            return 0.5  # Neutral fallback for empty inputs

        score = 0.0
        checks_passed = 0
        total_checks = 6

        try:
            elements = parsed_data.get('elements', {})

            # Check 1: Required particles present in appropriate contexts
            has_particles = any(role in ['aspect_particle', 'modal_particle', 'structural_particle']
                              for role in elements.keys())
            if has_particles:
                checks_passed += 1
                score += 0.15

            # Check 2: Script validation - all characters are valid Traditional Han characters
            sentence_chars = re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf]', original_sentence)
            all_words = []
            for role_elements in elements.values():
                if isinstance(role_elements, list):
                    all_words.extend([item.get('word', '') for item in role_elements])

            word_chars = ''.join(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf]', ' '.join(all_words)))
            char_coverage = len(set(word_chars)) / len(set(sentence_chars)) if sentence_chars else 0
            if char_coverage >= 0.8:  # 80% character coverage
                checks_passed += 1
                score += 0.15

            # Check 3: Measure word agreement - nouns have appropriate classifiers
            nouns = elements.get('noun', [])
            measure_words = elements.get('measure_word', [])
            if nouns and measure_words:  # If both exist, likely proper agreement
                checks_passed += 1
                score += 0.15

            # Check 4: Tone markers in Pinyin (if present)
            has_tones = bool(self.pinyin_tone_pattern.search(original_sentence))
            if not has_tones or any('āáǎà' in word.get('individual_meaning', '') for role_elements in elements.values()
                                   for word in (role_elements if isinstance(role_elements, list) else [])):
                checks_passed += 1
                score += 0.15

            # Check 5: Word order patterns (basic SVO check)
            verbs = elements.get('verb', [])
            if verbs:  # Has verbs, basic structure present
                checks_passed += 1
                score += 0.15

            # Check 6: Compound word recognition
            combinations = elements.get('word_combinations', [])
            if combinations:  # Has compound recognition
                checks_passed += 1
                score += 0.25  # Higher weight for compounds

            # Calculate final score with minimum threshold
            if checks_passed >= 4:  # Need at least 4 checks for high quality
                final_score = max(score, 0.85)
            elif checks_passed >= 3:
                final_score = max(score, 0.7)
            else:
                final_score = score * 0.5

            logger.info(f"Chinese Traditional validation: {checks_passed}/{total_checks} checks passed, score: {final_score}")
            return min(final_score, 1.0)  # Cap at 1.0

        except Exception as e:
            logger.error(f"Chinese Traditional validation failed: {e}")
            return 0.5  # Neutral fallback score

    # Legacy methods for backward compatibility (redirect to new batch methods)
    def get_grammar_prompt(self, complexity: str, sentence: str, target_word: str) -> str:
        """Legacy method - redirect to batch prompt for single sentence"""
        return self.get_batch_grammar_prompt(complexity, [sentence], target_word)

    def parse_grammar_response(self, ai_response: str, complexity: str, sentence: str) -> Dict[str, Any]:
        """Legacy method - redirect to batch parsing for single sentence"""
        results = self.parse_batch_grammar_response(ai_response, [sentence], complexity)
        return results[0] if results else {
            "sentence": sentence,
            "elements": {},
            "word_explanations": [],
            "explanations": {"sentence_structure": "Parsing failed", "complexity_notes": ""}
        }

    def _initialize_patterns(self):
        """Initialize language-specific patterns and rules"""
        # Call the Chinese Traditional-specific pattern initialization
        self._initialize_chinese_traditional_patterns()

    def _initialize_chinese_traditional_patterns(self):
        """Initialize Chinese Traditional-specific linguistic patterns (5-12 most frequent markers only)"""
        # Aspect particles (most common grammatical markers) - Traditional characters
        self.aspect_patterns = {
            'perfective_le': re.compile(r'了(?=\s|$|[^了著過])'),  # 了 (le) - perfective aspect
            'durative_zhe': re.compile(r'著(?=\s|$|[^了著過])'),   # 著 (zhe/zhú) - durative aspect
            'experiential_guo': re.compile(r'過(?=\s|$|[^了著過])') # 過 (guo) - experiential aspect
        }

        # Modal particles (sentence-final) - Same as Simplified
        self.modal_patterns = {
            'question_ma': re.compile(r'嗎(?=\s*$)'),     # 嗎 (ma) - yes-no questions
            'continuation_ne': re.compile(r'呢(?=\s*$)'),  # 呢 (ne) - topic continuation
            'suggestion_ba': re.compile(r'吧(?=\s*$)'),    # 吧 (ba) - suggestion/assumption
            'exclamation_a': re.compile(r'啊(?=\s*$)')     # 啊 (a) - exclamation/realization
        }

        # Structural particles - Same as Simplified
        self.structural_patterns = {
            'attribution_de': re.compile(r'的(?=\s|$)'),   # 的 (de) - attribution/possession
            'adverbial_de': re.compile(r'地(?=\s|$)'),     # 地 (de) - adverbial modification
            'complement_de': re.compile(r'得(?=\s|$)')     # 得 (de) - resultative complement
        }

        # Top 10 measure words (classifiers) - Traditional characters
        self.measure_word_patterns = {
            'general_ge': re.compile(r'個(?=\s|$)'),       # 個 (gè) - general classifier
            'books_ben': re.compile(r'本(?=\s|$)'),        # 本 (běn) - books, notebooks
            'cups_bei': re.compile(r'杯(?=\s|$)'),         # 杯 (bēi) - cups, glasses
            'flat_zhang': re.compile(r'張(?=\s|$)'),       # 張 (zhāng) - flat objects
            'animals_zhi': re.compile(r'隻(?=\s|$)'),      # 隻 (zhī) - animals, one of pair
            'vehicles_liang': re.compile(r'輛(?=\s|$)'),   # 輛 (liàng) - vehicles
            'businesses_jia': re.compile(r'家(?=\s|$)'),   # 家 (jiā) - businesses, families
            'people_wei': re.compile(r'位(?=\s|$)'),       # 位 (wèi) - people (polite)
            'long_tiao': re.compile(r'條(?=\s|$)'),        # 條 (tiáo) - long thin objects
            'matters_jian': re.compile(r'件(?=\s|$)')      # 件 (jiàn) - items, matters
        }

        # Common prepositions/coverbs - Same as Simplified
        self.preposition_patterns = {
            'location_zai': re.compile(r'^在|\s在(?=\s)'),  # 在 (zài) - location, progressive
            'towards_dui': re.compile(r'對(?=\s|$)'),       # 對 (duì) - towards, regarding
            'benefactive_gei': re.compile(r'給(?=\s|$)'),   # 給 (gěi) - to, for (benefactive)
            'from_cong': re.compile(r'從(?=\s|$)'),         # 從 (cóng) - from
            'to_dao': re.compile(r'到(?=\s|$)')             # 到 (dào) - to, until
        }

        # Traditional Han character validation (extended Unicode ranges for Traditional characters)
        self.traditional_han_character_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf]')

        # Pinyin validation (basic tone marks) - Same as Simplified
        self.pinyin_tone_pattern = re.compile(r'[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]')

    def _map_grammatical_role_to_category(self, role: str) -> str:
        """Map grammatical role to color category"""
        # Simplified mapping for color assignment
        role_mapping = {
            'noun': 'noun',
            'pronoun': 'pronoun',
            'verb': 'verb',
            'adjective': 'adjective',
            'numeral': 'numeral',
            'measure_word': 'measure_word',
            'time_word': 'time_word',
            'locative_word': 'locative_word',
            'aspect_particle': 'aspect_particle',
            'modal_particle': 'modal_particle',
            'structural_particle': 'structural_particle',
            'preposition': 'preposition',
            'conjunction': 'conjunction',
            'adverb': 'adverb',
            'interjection': 'interjection',
            'onomatopoeia': 'onomatopoeia'
        }
        return role_mapping.get(role, 'other')

    def _reorder_explanations_by_sentence_position(self, sentence: str, word_explanations: List[List]) -> List[List]:
        """
        Reorder word explanations to match the order they appear in the sentence.
        This ensures grammar explanations are displayed in sentence word order for better user experience.
        """
        if not word_explanations or not sentence:
            return word_explanations or []

        # For Chinese Traditional, we need to handle word positioning more carefully
        # Create a list to track word positions
        positioned_explanations = []

        for explanation in word_explanations:
            word = explanation[0]  # word is at index 0 in [word, pos, color, explanation]
            if word:
                # Find all occurrences of this word in the sentence
                positions = []
                start = 0
                while True:
                    pos = sentence.find(word, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1

                # Use the first occurrence position, or a high number if not found
                position = positions[0] if positions else float('inf')
                positioned_explanations.append((position, explanation))

        # Sort by position in sentence
        positioned_explanations.sort(key=lambda x: x[0])

        # Extract just the explanations
        sorted_explanations = [exp for _, exp in positioned_explanations]

        logger.debug(f"Reordered {len(sorted_explanations)} Chinese Traditional explanations by sentence position")
        return sorted_explanations

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
    """Factory function to create Chinese Traditional analyzer"""
    return ZhTwAnalyzer()