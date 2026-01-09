# Chinese Simplified Grammar Analyzer
# Auto-generated analyzer for Chinese Simplified (中文简体)
# Language Family: Sino-Tibetan
# Script Type: logographic
# Complexity Rating: high

import re
import json
import logging
from typing import Dict, List, Any, Tuple

from streamlit_app.language_analyzers.base_analyzer import BaseGrammarAnalyzer, LanguageConfig, GrammarAnalysis

logger = logging.getLogger(__name__)

class ZhAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Chinese Simplified (中文简体).

    Key Features: ['word_segmentation', 'compounds_first', 'chinese_categories', 'aspect_system', 'topic_comment']
    Complexity Levels: ['beginner', 'intermediate', 'advanced']
    """

    VERSION = "3.0"
    LANGUAGE_CODE = "zh"
    LANGUAGE_NAME = "Chinese Simplified"

    # Grammatical Role Mapping (16 categories based on Chinese linguistics)
    GRAMMATICAL_ROLES = {
        # Content Words (实词 / Shící) - Independent Meaning
        "noun": "#FFAA00",                    # Orange - People/places/things/concepts
        "verb": "#44FF44",                    # Green - Actions/states/changes
        "adjective": "#FF44FF",               # Magenta - Qualities/descriptions
        "numeral": "#FFFF44",                 # Yellow - Numbers/quantities
        "measure_word": "#FFD700",            # Gold - Classifiers (个, 本, 杯)
        "pronoun": "#FF4444",                 # Red - Replacements for nouns
        "time_word": "#FFA500",               # Orange-red - Time expressions
        "locative_word": "#FF8C00",           # Dark orange - Location/direction

        # Function Words (虚词 / Xūcí) - Structural/Grammatical
        "aspect_particle": "#8A2BE2",         # Purple - Aspect markers (了, 着, 过)
        "modal_particle": "#DA70D6",          # Plum - Tone/mood particles (吗, 呢, 吧)
        "structural_particle": "#9013FE",     # Violet - Structural particles (的, 地, 得)
        "preposition": "#4444FF",             # Blue - Prepositions/coverbs
        "conjunction": "#888888",             # Gray - Connectors
        "adverb": "#44FFFF",                  # Cyan - Modifies verbs/adjectives
        "interjection": "#FFD700",            # Gold - Emotions/exclamations
        "onomatopoeia": "#FFD700"             # Gold - Sound imitation
    }

    def __init__(self):
        config = LanguageConfig(
            code="zh",
            name="Chinese Simplified",
            native_name="中文简体",
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
        """Generate Chinese-specific AI prompt for batch grammar analysis (word-level, not character-level)"""
        sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        return f"""Analyze the grammar of these Chinese sentences at the WORD level (not character-by-character).

Target word: "{target_word}"
Language: Chinese Simplified
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
- Focus on Chinese grammatical categories (实词/虚词 distinction)
- Include measure words, aspect particles, and modal particles appropriately
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
          "word": "学生",
          "individual_meaning": "student",
          "grammatical_role": "noun"
        }}
      ],
      "word_combinations": [
        {{
          "text": "学习中文",
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
        """Parse batch AI response into standardized format for Chinese word-level analysis"""
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
            logger.error(f"Chinese batch parsing failed: {e}")
            # Fallback to basic parsing
            return [{
                "sentence": sentence,
                "elements": {},
                "word_explanations": [],
                "explanations": {"sentence_structure": f"Analysis failed: {e}", "complexity_notes": ""}
            } for sentence in sentences]

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Chinese grammatical elements"""
        # Use the same color scheme for all complexity levels (Chinese categories are fundamental)
        return self.GRAMMATICAL_ROLES.copy()

    def validate_analysis(self, parsed_data: Dict[str, Any], original_sentence: str) -> float:
        """Validate Chinese analysis quality with 3-6 simple checks (85% threshold)"""
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

            # Check 2: Script validation - all characters are valid Han characters
            sentence_chars = re.findall(r'[\u4e00-\u9fff]', original_sentence)
            all_words = []
            for role_elements in elements.values():
                if isinstance(role_elements, list):
                    all_words.extend([item.get('word', '') for item in role_elements])

            word_chars = ''.join(re.findall(r'[\u4e00-\u9fff]', ' '.join(all_words)))
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
            final_score = max(score, 0.7) if checks_passed >= 3 else score * 0.5

            logger.info(f"Chinese validation: {checks_passed}/{total_checks} checks passed, score: {final_score}")
            return min(final_score, 1.0)  # Cap at 1.0

        except Exception as e:
            logger.error(f"Chinese validation failed: {e}")
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
        # Call the Chinese-specific pattern initialization
        self._initialize_chinese_patterns()

    def _initialize_chinese_patterns(self):
        """Initialize Chinese-specific linguistic patterns (5-12 most frequent markers only)"""
        # Aspect particles (most common grammatical markers)
        self.aspect_patterns = {
            'perfective_le': re.compile(r'了(?=\s|$|[^了着过])'),  # 了 (le) - perfective aspect
            'durative_zhe': re.compile(r'着(?=\s|$|[^了着过])'),   # 着 (zhe) - durative aspect
            'experiential_guo': re.compile(r'过(?=\s|$|[^了着过])') # 过 (guo) - experiential aspect
        }

        # Modal particles (sentence-final)
        self.modal_patterns = {
            'question_ma': re.compile(r'吗(?=\s*$)'),     # 吗 (ma) - yes-no questions
            'continuation_ne': re.compile(r'呢(?=\s*$)'),  # 呢 (ne) - topic continuation
            'suggestion_ba': re.compile(r'吧(?=\s*$)'),    # 吧 (ba) - suggestion/assumption
            'exclamation_a': re.compile(r'啊(?=\s*$)')     # 啊 (a) - exclamation/realization
        }

        # Structural particles
        self.structural_patterns = {
            'attribution_de': re.compile(r'的(?=\s|$)'),   # 的 (de) - attribution/possession
            'adverbial_de': re.compile(r'地(?=\s|$)'),     # 地 (de) - adverbial modification
            'complement_de': re.compile(r'得(?=\s|$)')     # 得 (de) - resultative complement
        }

        # Top 10 measure words (classifiers)
        self.measure_word_patterns = {
            'general_ge': re.compile(r'个(?=\s|$)'),       # 个 (gè) - general classifier
            'books_ben': re.compile(r'本(?=\s|$)'),        # 本 (běn) - books, notebooks
            'cups_bei': re.compile(r'杯(?=\s|$)'),         # 杯 (bēi) - cups, glasses
            'flat_zhang': re.compile(r'张(?=\s|$)'),       # 张 (zhāng) - flat objects
            'animals_zhi': re.compile(r'只(?=\s|$)'),      # 只 (zhī) - animals, one of pair
            'vehicles_liang': re.compile(r'辆(?=\s|$)'),   # 辆 (liàng) - vehicles
            'businesses_jia': re.compile(r'家(?=\s|$)'),   # 家 (jiā) - businesses, families
            'people_wei': re.compile(r'位(?=\s|$)'),       # 位 (wèi) - people (polite)
            'long_tiao': re.compile(r'条(?=\s|$)'),        # 条 (tiáo) - long thin objects
            'matters_jian': re.compile(r'件(?=\s|$)')      # 件 (jiàn) - items, matters
        }

        # Common prepositions/coverbs
        self.preposition_patterns = {
            'location_zai': re.compile(r'^在|\s在(?=\s)'),  # 在 (zài) - location, progressive
            'towards_dui': re.compile(r'对(?=\s|$)'),       # 对 (duì) - towards, regarding
            'benefactive_gei': re.compile(r'给(?=\s|$)'),   # 给 (gěi) - to, for (benefactive)
            'from_cong': re.compile(r'从(?=\s|$)'),         # 从 (cóng) - from
            'to_dao': re.compile(r'到(?=\s|$)')             # 到 (dào) - to, until
        }

        # Han character validation (basic check for valid characters)
        self.han_character_pattern = re.compile(r'[\u4e00-\u9fff]')

        # Pinyin validation (basic tone marks)
        self.pinyin_tone_pattern = re.compile(r'[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]')

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

    def get_batch_grammar_prompt(self, complexity: str, sentences: List[str], target_word: str, native_language: str = "English") -> str:
        """Generate Chinese-specific AI prompt for batch grammar analysis with word-level focus"""
        sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        return f"""Analyze Chinese sentences at the WORD level with compounds-first ordering.

Target word: "{target_word}"
Language: Chinese (Simplified)
Complexity level: {complexity}
Analysis should be in {native_language}

Sentences to analyze:
{sentences_text}

CRITICAL REQUIREMENTS FOR CHINESE WORD-LEVEL ANALYSIS:
- Segment sentences into WORDS, not individual characters
- Identify compound words FIRST (higher priority in explanations)
- Use Chinese-appropriate grammatical categories (实词/虚词 distinction)
- Compounds should appear higher in explanations than individual character breakdowns

For EACH word in EVERY sentence, provide:
- word: the exact word as it appears (can be compound or single character)
- combined_meaning: English translation/meaning of the word
- grammatical_role: EXACTLY ONE category from Chinese linguistics: noun, locative_noun, time_noun, verb, adjective, adverb, numeral, classifier, pronoun, personal_pronoun, demonstrative_pronoun, interrogative_pronoun, indefinite_pronoun, modal_verb, directional_verb, coverb, conjunction, particle, interjection, onomatopoeia, other

COMPOUNDS-FIRST ORDERING:
- Multi-character compounds (e.g., "图书馆", "学习") get HIGHER priority in explanations
- Single characters appear after compounds
- This helps beginners understand word-level meanings first

CHINESE GRAMMATICAL CATEGORIES (词类):
CONTENT WORDS (实词):
- noun: people, places, things, concepts (书、本、人、北京、水、爱情)
- verb: actions, states, changes (是、吃、跑、爱、想、知道、可以)
- adjective: qualities, descriptions (大、红、好、漂亮、快乐、雪白)
- adverb: modifies verbs/adjectives (很、都、也、不、已经、正在、非常、马上)
- numeral: numbers, quantities (一、二、三、第一、半、几、许多)
- classifier: measure words (个、本、只、张、杯、次、群、辆)
- pronoun: replaces nouns (我、你、他、这、那、谁、什么、大家)
- time_noun: time expressions (今天、现在、昨天、早上、星期三)
- locative_noun: location/direction (上面、里面、东、左、前、附近)

FUNCTION WORDS (虚词):
- coverb: verb-derived prepositions (在、从、把、被、对于、关于、向、跟)
- conjunction: connects clauses (和、但是、因为、所以、如果、虽然、或者)
- particle: grammatical markers (的、地、得、所、了、着、过、们、吗、呢、吧、啊、呀)
- interjection: expresses emotion (啊、哦、哎呀、哇、嗯、嘿)
- onomatopoeia: imitates sounds (砰、哗哗、汪汪、咚咚、叮咚)

Return JSON in this exact format:
{{
  "batch_results": [
    {{
      "sentence_index": 1,
      "sentence": "{sentences[0] if sentences else ''}",
      "words": [
        {{
          "word": "图书馆",
          "combined_meaning": "library",
          "grammatical_role": "noun"
        }},
        {{
          "word": "学习",
          "combined_meaning": "to study",
          "grammatical_role": "verb"
        }},
        {{
          "word": "图",
          "combined_meaning": "diagram/picture",
          "grammatical_role": "noun"
        }},
        {{
          "word": "书",
          "combined_meaning": "book",
          "grammatical_role": "noun"
        }},
        {{
          "word": "馆",
          "combined_meaning": "hall/building",
          "grammatical_role": "noun"
        }}
      ],
      "explanations": {{
        "sentence_structure": "Brief grammatical summary",
        "compounds_first": "Multi-character words analyzed before individual characters",
        "complexity_notes": "Notes about {complexity} level structures"
      }}
    }}
  ]
}}

IMPORTANT:
- Analyze ALL {len(sentences)} sentences
- WORD-LEVEL analysis, not character-by-character
- COMPOUNDS appear FIRST in word lists and explanations
- Use authentic Chinese grammatical categories
- Return ONLY the JSON object, no additional text
"""

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

    def parse_batch_grammar_response(self, ai_response: str, sentences: List[str], complexity: str, native_language: str = "English") -> List[Dict[str, Any]]:
        """Parse batch AI response for Chinese word-level analysis with compounds-first ordering"""
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

                    # Convert batch format to standard format expected by _transform_to_standard_format
                    elements = {}
                    word_explanations = []

                    # COMPOUNDS-FIRST ORDERING: Process words in the order they appear in the response
                    # The AI should already put compounds first, so we maintain that order
                    for word_data in item.get("words", []):
                        word = word_data.get("word", "").strip()
                        if word:
                            grammatical_role = word_data.get("grammatical_role", "other")
                            category = self._map_grammatical_role_to_category(grammatical_role)

                            # Group words by category
                            if category not in elements:
                                elements[category] = []

                            elements[category].append({
                                "word": word,
                                "combined_meaning": word_data.get("combined_meaning", ""),
                                "grammatical_role": grammatical_role
                            })

                            # Create word explanation with color and educational enhancement
                            color = self._get_color_for_category(category, complexity)

                            # Create pedagogically rich explanation for word-level analysis
                            combined_meaning = word_data.get('combined_meaning', '').strip()
                            explanation_text = self._create_educational_explanation(
                                combined_meaning, category, grammatical_role
                            )

                            word_explanations.append([
                                word,
                                grammatical_role,
                                color,
                                explanation_text
                            ])

                    # Reorder word_explanations to match sentence word order
                    word_explanations = self._reorder_explanations_by_sentence_position(sentence, word_explanations)

                    # Create explanations
                    explanations = item.get("explanations", {})
                    if not explanations:
                        explanations = {
                            "sentence_structure": f"Chinese sentence with word-level analysis",
                            "compounds_first": "Multi-character compounds analyzed before individual characters",
                            "complexity_notes": f"Analysis at {complexity} level using Chinese grammatical categories"
                        }

                    results.append({
                        "sentence": sentence,
                        "elements": elements,
                        "explanations": explanations,
                        "word_explanations": word_explanations
                    })
                else:
                    # Fallback for invalid sentence index
                    results.append({
                        "sentence": sentences[len(results)] if len(results) < len(sentences) else "",
                        "elements": {},
                        "explanations": {"sentence_structure": "Batch parsing failed", "complexity_notes": ""},
                        "word_explanations": []
                    })

            return results

        except Exception as e:
            logger.error(f"Chinese batch parsing failed: {e}")
            # Fallback to base class method
            return super().parse_batch_grammar_response(ai_response, sentences, complexity, native_language)

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return comprehensive color scheme for Chinese grammatical elements using Chinese-appropriate categories"""
        schemes = {
            "beginner": {
                # CONTENT WORDS (实词 / Shící) - Independent meaning
                "noun": "#FFAA00",                    # Orange - People/places/things/concepts
                "verb": "#44FF44",                    # Green - Actions/states/changes
                "adjective": "#FF44FF",               # Magenta - Qualities/descriptions
                "numeral": "#FFFF44",                 # Yellow - Numbers/quantities
                "classifier": "#FFD700",              # Gold - Measure words (个、只、本)
                "pronoun": "#FF4444",                 # Red - Replaces nouns
                "time_noun": "#FFA500",               # Orange-red - Time expressions
                "locative_noun": "#FF8C00",           # Dark orange - Location/direction

                # FUNCTION WORDS (虚词 / Xūcí) - Structural/grammatical
                "aspect_particle": "#8A2BE2",         # Purple - Aspect markers (了、着、过)
                "modal_particle": "#DA70D6",          # Plum - Tone/mood particles (吗、呢、吧)
                "structural_particle": "#9013FE",     # Violet - Structural particles (的、地、得)
                "coverb": "#4444FF",                  # Blue - Prepositions/coverbs
                "conjunction": "#888888",             # Gray - Connectors
                "adverb": "#44FFFF",                  # Cyan - Modifies verbs/adjectives
                "interjection": "#FFD700",            # Gold - Emotions/exclamations
                "onomatopoeia": "#FFD700",            # Gold - Sound imitation
                "other": "#AAAAAA"                    # Light gray - Other
            },
            "intermediate": {
                # Same as beginner for now - Chinese categories are consistent across levels
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "adjective": "#FF44FF",
                "numeral": "#FFFF44",
                "classifier": "#FFD700",
                "pronoun": "#FF4444",
                "time_noun": "#FFA500",
                "locative_noun": "#FF8C00",
                "aspect_particle": "#8A2BE2",
                "modal_particle": "#DA70D6",
                "structural_particle": "#9013FE",
                "coverb": "#4444FF",
                "conjunction": "#888888",
                "adverb": "#44FFFF",
                "interjection": "#FFD700",
                "onomatopoeia": "#FFD700",
                "other": "#AAAAAA"
            },
            "advanced": {
                # Same as intermediate - Chinese categories are consistent across levels
                "noun": "#FFAA00",
                "verb": "#44FF44",
                "adjective": "#FF44FF",
                "numeral": "#FFFF44",
                "classifier": "#FFD700",
                "pronoun": "#FF4444",
                "time_noun": "#FFA500",
                "locative_noun": "#FF8C00",
                "aspect_particle": "#8A2BE2",
                "modal_particle": "#DA70D6",
                "structural_particle": "#9013FE",
                "coverb": "#4444FF",
                "conjunction": "#888888",
                "adverb": "#44FFFF",
                "interjection": "#FFD700",
                "onomatopoeia": "#FFD700",
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
        """Generate HTML output for Chinese text with word-level coloring using colors from word_explanations"""
        explanations = parsed_data.get('word_explanations', [])

        logger.info(f"DEBUG Chinese HTML Gen - Input explanations count: {len(explanations)}")
        logger.info(f"DEBUG Chinese HTML Gen - Input sentence: '{sentence}'")

        # Create mapping of words to colors directly from word_explanations (authoritative source)
        word_to_color = {}
        for exp in explanations:
            if len(exp) >= 3:
                word, pos, color = exp[0], exp[1], exp[2]
                word_to_color[word] = color
                logger.info(f"DEBUG Chinese HTML Gen - Word '{word}' -> Color '{color}' (POS: '{pos}')")

        logger.info(f"DEBUG Chinese HTML Gen - Word-to-color mapping: {word_to_color}")

        # For word-level analysis, we need to segment the sentence into words
        # Since we don't have proper word segmentation yet, we'll use a simple approach:
        # Try to match compound words first, then individual characters
        html_parts = []
        remaining_sentence = sentence

        # COMPOUNDS-FIRST APPROACH: Try longer matches first
        sorted_words = sorted(word_to_color.keys(), key=len, reverse=True)  # Longest first

        while remaining_sentence:
            matched = False
            for word in sorted_words:
                if remaining_sentence.startswith(word):
                    color = word_to_color[word]
                    html_parts.append(f'<span style="color: {color}; font-weight: bold;">{word}</span>')
                    remaining_sentence = remaining_sentence[len(word):]
                    logger.info(f"DEBUG Chinese HTML Gen - ✓ Colored word '{word}' with color '{color}'")
                    matched = True
                    break

            if not matched:
                # No word match, take first character
                char = remaining_sentence[0]
                if char in word_to_color:
                    color = word_to_color[char]
                    html_parts.append(f'<span style="color: {color}; font-weight: bold;">{char}</span>')
                    logger.info(f"DEBUG Chinese HTML Gen - ✓ Colored character '{char}' with color '{color}'")
                elif char.strip():  # Only add non-whitespace characters without color
                    html_parts.append(f'<span style="color: #888888;">{char}</span>')
                    logger.warning(f"DEBUG Chinese HTML Gen - ✗ No color found for character '{char}'")
                else:
                    # Preserve whitespace
                    html_parts.append(char)
                remaining_sentence = remaining_sentence[1:]

        result = ''.join(html_parts)
        logger.info(f"DEBUG Chinese HTML Gen - Final HTML output length: {len(result)}")
        logger.info(f"DEBUG Chinese HTML Gen - Final HTML preview: {result[:300]}...")
        return result

    def _get_color_for_category(self, category: str, complexity: str = "beginner") -> str:
        """Get color for a grammatical category"""
        color_scheme = self.get_color_scheme(complexity)
        return color_scheme.get(category, "#888888")  # Default to grey if category not found

    def _map_grammatical_role_to_category(self, grammatical_role: str) -> str:
        """Map grammatical role descriptions to Chinese-appropriate categories (实词/虚词 distinction)"""
        role_lower = grammatical_role.lower().strip()

        # STEP 1: PREPROCESSING - Fix AI hallucinations and standardize terms
        if role_lower in ["co verb", "prepositional_verb"]:
            role_lower = "coverb"
        elif role_lower in ["m measure_word", "counter"]:
            role_lower = "classifier"
        elif role_lower in ["aux modal", "modal_verb", "auxiliary_verb"]:
            role_lower = "modal_particle"  # Chinese modal particles
        elif role_lower in ["direction complement", "directional_verb"]:
            role_lower = "verb"  # Directional complements are verbs in Chinese
        elif role_lower in ["aspect particle", "aspect marker"]:
            role_lower = "aspect_particle"
        elif role_lower in ["structural particle", "structural"]:
            role_lower = "structural_particle"
        elif role_lower in ["modal particle", "tone particle", "mood particle"]:
            role_lower = "modal_particle"

        # STEP 2: CHINESE-SPECIFIC PARTICLE TYPES (Highest Priority)
        # Aspect particles (动态助词)
        if any(keyword in role_lower for keyword in [
            'aspect_particle', 'aspect', '了', '着', '过', 'aspect marker', 'perfective', 'progressive', 'experiential'
        ]):
            return 'aspect_particle'

        # Modal particles (语气助词)
        if any(keyword in role_lower for keyword in [
            'modal_particle', 'modal', '语气', '吗', '呢', '吧', '啊', '呀', '咯', '喽', 'tone', 'mood'
        ]):
            return 'modal_particle'

        # Structural particles (结构助词)
        if any(keyword in role_lower for keyword in [
            'structural_particle', 'structural', '结构', '的', '地', '得', '所', '把', '被'
        ]):
            return 'structural_particle'

        # STEP 3: CONTENT WORDS (实词) - Independent meaning
        # Time nouns (时间词)
        if any(keyword in role_lower for keyword in [
            'time_noun', 'time', 'temporal', '今天', '昨天', '明天', '早上', '晚上', '年', '月', '日', '时', '分'
        ]):
            return 'time_noun'

        # Locative nouns (方位词)
        if any(keyword in role_lower for keyword in [
            'locative_noun', 'locative', 'spatial', 'direction', '上', '下', '里', '外', '前', '后', '左', '右', '东', '西', '南', '北', '中', '间'
        ]):
            return 'locative_noun'

        # Pronouns (代词)
        if any(keyword in role_lower for keyword in [
            'pronoun', '代词', '代', '我', '你', '他', '她', '它', '我们', '你们', '他们', '这', '那', '谁', '什么'
        ]):
            return 'pronoun'

        # Classifiers/Measure words (量词)
        if any(keyword in role_lower for keyword in [
            'classifier', 'measure_word', '量词', '个', '本', '张', '只', '条', '把', '杯', '次', '群', '辆'
        ]):
            return 'classifier'

        # Numerals (数词)
        if any(keyword in role_lower for keyword in [
            'numeral', '数词', '数', '数字', '一', '二', '三', '四', '五', '十', '百', '千', '万'
        ]):
            return 'numeral'

        # STEP 4: FUNCTION WORDS (虚词) - Structural/grammatical
        # Coverbs (verb-derived prepositions)
        if any(keyword in role_lower for keyword in [
            'coverb', '在', '从', '到', '用', '给', '对', '向', '往', '跟', '和', '于', '自', '由'
        ]):
            return 'coverb'

        # Conjunctions (连词)
        if any(keyword in role_lower for keyword in [
            'conjunction', '连词', '和', '但是', '因为', '所以', '如果', '虽然', '或者', '与', '及'
        ]):
            return 'conjunction'

        # Adverbs (副词)
        if any(keyword in role_lower for keyword in [
            'adverb', '副词', '副', '很', '都', '也', '不', '已经', '正在', '非常', '马上', '太', '更'
        ]):
            return 'adverb'

        # Interjections (叹词)
        if any(keyword in role_lower for keyword in [
            'interjection', '叹词', '啊', '哦', '哎呀', '哇', '嗯', '嘿', '唉'
        ]):
            return 'interjection'

        # Onomatopoeia (拟声词)
        if any(keyword in role_lower for keyword in [
            'onomatopoeia', 'sound_imitation', '拟声词', '汪汪', '叮咚', '哗啦', '砰', '咚咚'
        ]):
            return 'onomatopoeia'

        # STEP 5: BASIC CONTENT WORD CATEGORIES
        if any(keyword in role_lower for keyword in ['verb', '动词', '动']):
            return 'verb'

        if any(keyword in role_lower for keyword in ['adjective', '形容词', '形']):
            return 'adjective'

        if any(keyword in role_lower for keyword in ['noun', '名词', '名']):
            return 'noun'

        # STEP 6: DEFAULT FALLBACKS
        # AI-generated roles that need mapping
        if 'subject' in role_lower:
            return 'pronoun'  # Subjects are typically pronouns in Chinese
        elif 'negation' in role_lower or 'determiner' in role_lower:
            return 'other'  # Negation particles and determiners

        return 'other'  # Default fallback

    def _create_educational_explanation(self, combined_meaning: str, category: str, grammatical_role: str) -> str:
        """Create pedagogically rich explanations for word-level Chinese analysis"""
        if not combined_meaning or not combined_meaning.strip():
            # Fallback when no meaning provided
            fallback_explanations = {
                'noun': f'{grammatical_role} (person/place/thing/object)',
                'verb': f'{grammatical_role} (action/state/change)',
                'adjective': f'{grammatical_role} (describes quality/size/color)',
                'adverb': f'{grammatical_role} (modifies verb/adjective - how/when/where)',
                'numeral': f'{grammatical_role} (number or position in sequence)',
                'classifier': f'{grammatical_role} (measure word for counting nouns)',
                'pronoun': f'{grammatical_role} (replaces a noun)',
                'time_noun': f'{grammatical_role} (indicates time period/moment)',
                'locative_noun': f'{grammatical_role} (indicates place/position/direction)',
                'aspect_particle': f'{grammatical_role} (marks action completion/progress/experience)',
                'modal_particle': f'{grammatical_role} (expresses tone/mood/question)',
                'structural_particle': f'{grammatical_role} (connects sentence elements)',
                'coverb': f'{grammatical_role} (verb used like preposition)',
                'conjunction': f'{grammatical_role} (connects words/clauses)',
                'interjection': f'{grammatical_role} (expresses emotion/surprise)',
                'onomatopoeia': f'{grammatical_role} (imitates natural sound)',
                'other': f'{grammatical_role} (grammatical function)'
            }
            return fallback_explanations.get(category, f"{combined_meaning} ({grammatical_role})")

        base_meaning = combined_meaning.strip()

        # Educational enhancements for Chinese learners (word-level focus)
        educational_enhancements = {
            'noun': f"{base_meaning} (person/place/thing/object - 实词)",
            'verb': f"{base_meaning} (action/state/change - 实词)",
            'adjective': f"{base_meaning} (describes quality/size/color - 实词)",
            'adverb': f"{base_meaning} (modifies verb/adjective - how/when/where - 实词)",
            'numeral': f"{base_meaning} (number or position in sequence - 实词)",
            'classifier': f"{base_meaning} (measure word for counting nouns - 量词)",
            'pronoun': f"{base_meaning} (replaces a noun - 代词)",
            'time_noun': f"{base_meaning} (indicates time period/moment - 时间词)",
            'locative_noun': f"{base_meaning} (indicates place/position/direction - 方位词)",
            'aspect_particle': f"{base_meaning} (marks completion/progress/experience - 动态助词)",
            'modal_particle': f"{base_meaning} (expresses tone/mood/question - 语气助词)",
            'structural_particle': f"{base_meaning} (connects sentence elements - 结构助词)",
            'coverb': f"{base_meaning} (verb-derived preposition - 虚词)",
            'conjunction': f"{base_meaning} (connects words/clauses - 连词)",
            'interjection': f"{base_meaning} (expresses emotion/surprise - 叹词)",
            'onomatopoeia': f"{base_meaning} (imitates natural sound - 拟声词)",
            'other': f"{base_meaning} (grammatical function - 虚词)"
        }

        return educational_enhancements.get(category, f"{base_meaning} ({grammatical_role})")

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
            "noun": "#FFAA00",              # Orange
            "locative_noun": "#FFAA00",     # Orange
            "time_noun": "#FFAA00",         # Orange
            "verb": "#44FF44",              # Green
            "adjective": "#FF44FF",         # Magenta
            "adverb": "#44FFFF",            # Cyan
            "numeral": "#FFFF44",           # Yellow
            "classifier": "#FFFF44",        # Yellow
            "pronoun": "#FF4444",           # Red
            "personal_pronoun": "#FF4444",  # Red
            "demonstrative_pronoun": "#FF4444", # Red
            "interrogative_pronoun": "#FF4444", # Red
            "indefinite_pronoun": "#FF4444", # Red
            "modal_verb": "#44FF44",        # Green
            "directional_verb": "#44FF44",  # Green
            "coverb": "#4444FF",            # Blue
            "conjunction": "#888888",       # Gray
            "particle": "#AA44FF",          # Purple
            "interjection": "#FFD700",      # Gold
            "onomatopoeia": "#FFD700",      # Gold
            "other": "#AAAAAA"              # Light gray
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

    def _reorder_explanations_by_sentence_position(self, sentence: str, word_explanations: List[List]) -> List[List]:
        """
        Reorder word explanations to match the order they appear in the sentence.
        This ensures grammar explanations are displayed in sentence word order for better user experience.
        """
        if not word_explanations or not sentence:
            return word_explanations

        # For Chinese, we need to handle word positioning more carefully
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

        logger.debug(f"Reordered {len(sorted_explanations)} Chinese explanations by sentence position")
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
    """Factory function to create Chinese (Simplified) analyzer"""
    return ZhAnalyzer()
