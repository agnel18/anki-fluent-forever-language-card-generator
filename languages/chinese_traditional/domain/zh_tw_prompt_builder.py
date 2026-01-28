# languages/chinese_traditional/domain/zh_tw_prompt_builder.py
"""
AI prompt generation for Chinese Traditional grammar analysis.
Handles the creation of prompts for Gemini AI to analyze Chinese Traditional sentences.
"""

import json
from typing import List, Dict, Any
from .zh_tw_config import ZhTwConfig


class ZhTwPromptBuilder:
    """
    Builds AI prompts specifically for Chinese Traditional grammar analysis.

    Focuses on:
    - Word-level analysis (not character-level)
    - Chinese grammatical categories (實詞/虛詞)
    - Aspect particles and modal particles
    - Measure words and classifiers
    - Topic-comment structure
    """

    def __init__(self, config: ZhTwConfig):
        self.config = config

    def build_batch_grammar_prompt(
        self,
        complexity: str,
        sentences: List[str],
        target_word: str,
        native_language: str = "English"
    ) -> str:
        """
        Generate Chinese Traditional-specific AI prompt for batch grammar analysis.

        Args:
            complexity: Complexity level (beginner/intermediate/advanced)
            sentences: List of sentences to analyze
            target_word: The target word being learned
            native_language: Language for explanations

        Returns:
            Formatted prompt string for AI analysis
        """

        # Format sentences with numbering
        sentences_text = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        # Get allowed grammatical roles
        allowed_roles = list(self.config.grammatical_roles.keys())

        # Complexity-specific instructions
        complexity_instructions = self._get_complexity_instructions(complexity)

        prompt = f"""Analyze the grammar of these Chinese Traditional sentences at the WORD level (not character-by-character).

Target word: "{target_word}"
Language: Chinese Traditional (繁體中文)
Complexity level: {complexity}
Analysis should be in {native_language}

{complexity_instructions}

Sentences to analyze:
{sentences_text}

For EACH word in EVERY sentence, IN THE ORDER THEY APPEAR IN THE SENTENCE (left to right), provide:
- word: the exact word as it appears in the sentence
- individual_meaning: SPECIFIC {native_language} translation/meaning of this EXACT word (MANDATORY - UNIQUE for each word, not generic category descriptions)
- grammatical_role: EXACTLY ONE category from this list: {', '.join(allowed_roles)}

Additionally, identify 1-2 key compound words/phrases per sentence:
- word_combinations: array of compounds with text, combined_meaning, grammatical_role

CRITICAL REQUIREMENTS:
- Analyze at WORD level, not character level (Chinese words are compounds of characters)
- individual_meaning MUST be SPECIFIC and UNIQUE for EACH word - provide the actual meaning/translation, NOT generic descriptions like "a word that describes a noun"
- grammatical_role MUST be EXACTLY from the allowed list (one word only)
- Focus on Chinese grammatical categories (實詞/虛詞 distinction)
- Include 量詞 (measure words), 體詞 (aspect particles), and 語氣詞 (modal particles) appropriately
- word_combinations are OPTIONAL but enhance learning when present
- WORDS MUST BE LISTED IN THE EXACT ORDER THEY APPEAR IN THE SENTENCE (left to right, no grouping by category)

MANDATORY: For EACH sentence, include an "explanations" field with rich, specific analysis:
- overall_structure: Detailed sentence structure analysis (e.g., "Subject-Verb-Object structure with time adverbial '昨天' modifying the verb phrase")
- key_features: Important grammatical concepts demonstrated (e.g., "Use of aspect particle '了' indicating completed action, topic-comment structure")

Return JSON in this exact format:
{{
  "batch_results": [
    {{
      "sentence_index": 1,
      "words": [
        {{
          "word": "word1",
          "individual_meaning": "meaning1",
          "grammatical_role": "noun"
        }},
        {{
          "word": "word2",
          "individual_meaning": "meaning2",
          "grammatical_role": "verb"
        }}
      ],
      "word_combinations": [
        {{
          "text": "compound_word",
          "combined_meaning": "compound meaning",
          "grammatical_role": "noun"
        }}
      ],
      "explanations": {{
        "overall_structure": "Detailed analysis of sentence structure and grammatical relationships",
        "key_features": "Key grammatical concepts and linguistic features demonstrated"
      }}
    }}
  ]
}}

Example for sentence "我昨天去了學校。":
{{
  "sentence_index": 1,
  "words": [
    {{"word": "我", "individual_meaning": "I, me (first person singular pronoun)", "grammatical_role": "pronoun"}},
    {{"word": "昨天", "individual_meaning": "yesterday (time adverbial)", "grammatical_role": "time_word"}},
    {{"word": "去", "individual_meaning": "to go (verb of motion)", "grammatical_role": "verb"}},
    {{"word": "了", "individual_meaning": "particle indicating completed action (aspect marker)", "grammatical_role": "aspect_particle"}},
    {{"word": "學校", "individual_meaning": "school (educational institution, noun)", "grammatical_role": "noun"}},
    {{"word": "。", "individual_meaning": "period (sentence ending punctuation)", "grammatical_role": "punctuation"}}
  ],
  "explanations": {{
    "overall_structure": "Subject-Verb-Object structure with time adverbial '昨天' modifying the verb phrase '去了' and aspect particle '了' indicating completed action",
    "key_features": "Demonstrates perfective aspect marking with '了', time adverbial placement, and basic SVO word order in Chinese"
  }}
}}

IMPORTANT: Ensure all words are listed in sentence order, meanings are accurate for Chinese Traditional characters, and explanations provide rich grammatical analysis."""

        return prompt

    def _get_complexity_instructions(self, complexity: str) -> str:
        """
        Get complexity-specific analysis instructions.

        Args:
            complexity: Complexity level

        Returns:
            Instructions string for the prompt
        """

        if complexity == "beginner":
            return """
BEGINNER LEVEL INSTRUCTIONS:
- Focus on basic content words (nouns, verbs, adjectives)
- Identify simple particles (了, 嗎, 的)
- Explain measure words when present
- Keep explanations simple and clear"""

        elif complexity == "intermediate":
            return """
INTERMEDIATE LEVEL INSTRUCTIONS:
- Include all grammatical categories
- Explain aspect particles (了, 著, 過) and their functions
- Identify modal particles (嗎, 呢, 吧) and their tones
- Explain structural particles (的, 地, 得) usage
- Note topic-comment sentence structure when present"""

        elif complexity == "advanced":
            return """
ADVANCED LEVEL INSTRUCTIONS:
- Analyze complex grammatical structures
- Explain resultative compounds (verb + result, e.g., 吃完 = eat + finish)
- Identify directional complements (進來 = enter + come)
- Note pivot constructions (topic-comment structures)
- Explain nuanced particle usage and sentence mood
- Include analysis of sentence aspect and modality"""

        else:
            return """
GENERAL INSTRUCTIONS:
- Provide comprehensive grammatical analysis
- Include all relevant Chinese linguistic features
- Explain particle functions and sentence structure"""

    def build_single_sentence_prompt(
        self,
        sentence: str,
        target_word: str,
        complexity: str = "intermediate",
        native_language: str = "English"
    ) -> str:
        """
        Build prompt for single sentence analysis.

        Args:
            sentence: Single sentence to analyze
            target_word: Target word being learned
            complexity: Complexity level
            native_language: Language for explanations

        Returns:
            Formatted prompt for single sentence analysis
        """

        allowed_roles = list(self.config.grammatical_roles.keys())
        complexity_instructions = self._get_complexity_instructions(complexity)

        return f"""Analyze this single Chinese Traditional sentence at the word level:

Sentence: "{sentence}"
Target word: "{target_word}"
Language: Chinese Traditional (繁體中文)
Complexity: {complexity}

{complexity_instructions}

CRITICAL: Provide UNIQUE, INDIVIDUAL meanings for EACH word. Do NOT repeat meanings across words. Each word must have its own specific meaning.

Provide word-by-word analysis in {native_language}:

For each word in order:
- word: exact word from sentence
- individual_meaning: UNIQUE {native_language} translation/meaning SPECIFIC to this exact word only (MANDATORY - do not reuse meanings from other words)
- grammatical_role: one from [{', '.join(allowed_roles)}]

CRITICAL REQUIREMENTS:
- individual_meaning MUST be UNIQUE for each word - no repeating meanings
- individual_meaning MUST describe only this specific word's meaning/function
- grammatical_role MUST be EXACTLY from the allowed list
- WORDS MUST BE LISTED IN THE EXACT ORDER THEY APPEAR IN THE SENTENCE
- MANDATORY: Include the "explanations" field with overall_structure and key_features

Return JSON in this exact format:
{{
  "words": [
    {{
      "word": "word1",
      "individual_meaning": "unique_meaning_specific_to_word1",
      "grammatical_role": "noun"
    }},
    {{
      "word": "word2", 
      "individual_meaning": "unique_meaning_specific_to_word2",
      "grammatical_role": "verb"
    }}
  ],
  "explanations": {{
    "overall_structure": "comprehensive sentence analysis",
    "key_features": "important grammatical concepts demonstrated"
  }}
}}

Example for "我喜歡吃蘋果。":
{{
  "words": [
    {{"word": "我", "individual_meaning": "I, me (first person singular pronoun)", "grammatical_role": "pronoun"}},
    {{"word": "喜歡", "individual_meaning": "to like, to be fond of (verb expressing preference)", "grammatical_role": "verb"}},
    {{"word": "吃", "individual_meaning": "to eat, to consume (verb of consumption)", "grammatical_role": "verb"}},
    {{"word": "蘋果", "individual_meaning": "apple (fruit, noun)", "grammatical_role": "noun"}},
    {{"word": "。", "individual_meaning": "period (sentence ending punctuation)", "grammatical_role": "punctuation"}}
  ],
  "explanations": {{
    "overall_structure": "Subject-verb-object sentence structure",
    "key_features": "Use of personal pronoun subject and noun object"
  }}
}}

IMPORTANT: Each individual_meaning must be unique and specific to that word only. Do not group meanings or repeat the same meaning for different words.

Analyze now:"""

    def build_validation_prompt(
        self,
        analysis_result: Dict[str, Any],
        original_sentence: str,
        complexity: str = "intermediate"
    ) -> str:
        """
        Build prompt for validating analysis results.

        Args:
            analysis_result: The analysis result to validate
            original_sentence: Original sentence being analyzed
            complexity: Complexity level

        Returns:
            Validation prompt
        """

        return f"""Validate this Chinese Traditional grammar analysis:

Original Sentence: "{original_sentence}"
Complexity Level: {complexity}

Analysis Result:
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

Check for:
1. All words from sentence are analyzed
2. Grammatical roles are appropriate for Chinese
3. Meanings are accurate for Traditional characters
4. Word order is preserved
5. Compound words are properly identified

Return validation result as JSON with issues found."""