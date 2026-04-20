"""
Chinese Simplified Prompt Builder - Domain Component

Handles ALL prompt generation:
- Grammar analysis (single + batch)
- Sentence generation (moved from zh_analyzer.py)
"""

import logging
from typing import List, Optional

from .zh_config import ZhConfig

logger = logging.getLogger(__name__)

class ZhPromptBuilder:
    """
    Builds Chinese-specific prompts for grammar analysis and sentence creation.
    Follows clean architecture - no AI logic, only prompt templating.
    """

    def __init__(self, config: ZhConfig):
        self.config = config

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build single-sentence grammar analysis prompt."""
        roles_list = self.config._get_grammatical_roles_list(complexity)
        template = self.config.prompt_templates.get("single", "")

        prompt = template.replace("{{sentence}}", sentence) \
                         .replace("{{target_word}}", target_word or "") \
                         .replace("{{complexity}}", complexity) \
                         .replace("{{grammatical_roles_list}}", roles_list)
        return prompt

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Build batch grammar analysis prompt."""
        roles_list = self.config._get_grammatical_roles_list(complexity)
        sentences_str = "\n".join([f"- {s}" for s in sentences])

        template = self.config.prompt_templates.get("batch", self.config.prompt_templates.get("single", ""))
        prompt = template.replace("{{sentences}}", sentences_str) \
                         .replace("{{target_word}}", target_word or "") \
                         .replace("{{complexity}}", complexity) \
                         .replace("{{grammatical_roles_list}}", roles_list)
        return prompt

    def get_sentence_generation_prompt(self, word: str, language: str, num_sentences: int,
                                     enriched_meaning: str = "", min_length: int = 3,
                                     max_length: int = 15, difficulty: str = "intermediate",
                                     topics: Optional[List[str]] = None) -> str:
        """
        Chinese Simplified-specific sentence generation prompt.
        (Moved here from zh_analyzer.py to follow clean architecture)
        """
        # Build context instruction
        if topics:
            context_instruction = f"- CRITICAL REQUIREMENT: ALL sentences MUST relate to these specific topics: {', '.join(topics)}. Force the word usage into these contexts even if it requires creative interpretation. Do NOT use generic contexts."
        else:
            context_instruction = "- Use diverse real-life contexts: home, travel, food, emotions, work, social life, daily actions"

        # Build meaning instruction
        if enriched_meaning and enriched_meaning != 'N/A':
            if enriched_meaning.startswith('{') and enriched_meaning.endswith('}'):
                context_lines = enriched_meaning[1:-1].split('\n')
                definitions = []
                for line in context_lines:
                    line = line.strip()
                    if line.startswith('Definition'):
                        def_text = line.split(':', 1)[1].strip() if ':' in line else line
                        def_text = def_text.split(' | ')[0].strip()
                        definitions.append(def_text)
                if definitions:
                    meaning_summary = '; '.join(definitions[:4])
                    enriched_meaning_instruction = f'Analyze this linguistic data for "{word}" and generate a brief, clean English meaning that encompasses ALL the meanings. Data: {meaning_summary}. IMPORTANT: Consider all meanings and provide a comprehensive meaning.'
                else:
                    enriched_meaning_instruction = f'Analyze this linguistic context for "{word}" and generate a brief, clean English meaning. Context: {enriched_meaning[:200]}. IMPORTANT: Return ONLY the English meaning.'
            else:
                enriched_meaning_instruction = f'Use this pre-reviewed meaning for "{word}": "{enriched_meaning}". Generate a clean English meaning based on this.'
        else:
            enriched_meaning_instruction = f'Provide a brief English meaning for "{word}".'

        # Full Chinese-specific prompt
        prompt = f"""You are a native-level expert linguist in Simplified Chinese (简体中文).

Your task: Generate a complete learning package for the Simplified Chinese word "{word}" in ONE response.

===========================
STEP 1: WORD MEANING
===========================
{enriched_meaning_instruction}
Format: Return exactly one line like "house (a building where people live)" or "he (male pronoun, used as subject)"
IMPORTANT: Keep the entire meaning under 75 characters total.

===========================
WORD-SPECIFIC RESTRICTIONS
===========================
Based on the meaning above, identify any grammatical constraints for "{word}".
Examples: particles only (的/了/吗), specific measure words required, character-based restrictions.
If no restrictions apply, state "No specific grammatical restrictions."
IMPORTANT: Keep the entire restrictions summary under 60 characters total.

===========================
STEP 2: SENTENCES
===========================
Generate exactly {num_sentences} highly natural, idiomatic sentences in Simplified Chinese for the word "{word}".

QUALITY RULES:
- Every sentence must use proper Simplified Chinese characters
- Grammar, syntax, and character usage must be correct
- The target word "{word}" MUST be used correctly according to restrictions
- Each sentence must be between {min_length} and {max_length} words/characters long
- Difficulty: {difficulty}

VARIETY REQUIREMENTS:
- Use different aspect particles (了, 着, 过) and sentence structures
- Use different sentence types: declarative, interrogative, imperative
- Include appropriate measure words/classifiers when needed
{context_instruction}

===========================
STEP 3: ENGLISH TRANSLATIONS
===========================
For EACH sentence above, provide a natural, fluent English translation.

===========================
STEP 4: PINYIN TRANSCRIPTION
===========================
For EACH sentence above, provide accurate Pinyin transcription with tone marks.

===========================
STEP 5: IMAGE KEYWORDS
===========================
For EACH sentence above, generate exactly 3 specific keywords for image search (English only).

===========================
OUTPUT FORMAT - FOLLOW EXACTLY
===========================
Return your response in this exact text format:

MEANING: [brief English meaning]

RESTRICTIONS: [grammatical restrictions]

SENTENCES:
1. [sentence 1 in Simplified Chinese]
2. [sentence 2 in Simplified Chinese]
...

TRANSLATIONS:
1. [natural English translation for sentence 1]
2. [natural English translation for sentence 2]
...

PINYIN:
1. [Pinyin for sentence 1]
2. [Pinyin for sentence 2]
...

KEYWORDS:
1. [keyword1, keyword2, keyword3]
2. [keyword1, keyword2, keyword3]
...

IMPORTANT:
- Return ONLY the formatted text, no extra explanation
- Sentences must be in Simplified Chinese characters only
- Ensure exactly {num_sentences} sentences, translations, Pinyin, and keywords"""

        return prompt