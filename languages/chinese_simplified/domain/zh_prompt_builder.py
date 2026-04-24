"""
Chinese Simplified Prompt Builder - Domain Component

Handles ALL prompt generation:
- Grammar analysis (single + batch)
- Sentence generation (moved from zh_analyzer.py)
"""

import logging
from typing import List, Optional
from jinja2 import Template, Environment, BaseLoader
from .zh_config import ZhConfig

logger = logging.getLogger(__name__)

class ZhPromptBuilder:
    """
    Builds Chinese-specific prompts for grammar analysis and sentence creation.
    Follows clean architecture - no AI logic, only prompt templating.
    """

    def __init__(self, config: ZhConfig):
        self.config: ZhConfig = config
        self.jinja_env = Environment(loader=BaseLoader())

    def build_single_analysis_prompt(self, sentence: str, target_word: Optional[str], complexity: str) -> str:
        """Strong Chinese-specific prompt that forces rich, context-specific explanations and forbids generic labels."""
        template_str = self.config.prompt_templates.get("single", "")
        if not template_str:
            # RICH FALLBACK PROMPT — explicitly forbids generic explanations
            return f"""You are a native-level Chinese linguistics expert teaching Simplified Chinese.

Analyze this sentence: "{sentence}"
Focus especially on the word "{target_word}".

For EVERY word/particle/character in the sentence, provide:
- Exact grammatical role (e.g. pronoun, verb, modal particle, structural particle, aspect marker, classifier, etc.)
- DETAILED, CONTEXT-SPECIFIC explanation of what the word does in THIS sentence (do NOT use generic definitions)
- Why it is used here and how it affects meaning/grammar

IMPORTANT: If you cannot provide a detailed, context-specific explanation for a word, write "[WARNING: Explanation missing for this word]" and explain why. NEVER use generic labels like "a word that describes a noun" or "a thing, person, or concept". If you do, the answer will be rejected.

Output format EXACTLY like this:

Grammar Explanations:
我 (pronoun): A first-person singular pronoun meaning 'I'. It functions as the subject of the sentence.
吧 (modal_particle): A sentence-final modal particle indicating suggestion, confirmation, or assumption. It softens the sentence into a suggestion here.

Complexity level: {complexity}
Language: Chinese Simplified (Simplified characters only)"""

        # If a proper template exists in config, use it but still enrich
        template = self.jinja_env.from_string(template_str)
        context = {
            "sentence": sentence,
            "target_word": target_word or "",
            "complexity": complexity,
            "language": "Chinese Simplified",
            "grammatical_roles": self.config.grammatical_roles,
        }
        try:
            prompt = template.render(**context)
            return prompt
        except Exception:
            return f"Analyze the following sentence: {sentence} (target word: {target_word}, complexity: {complexity})"

    def build_batch_analysis_prompt(self, sentences: List[str], target_word: Optional[str], complexity: str) -> str:
        """Build a strong batch prompt for Chinese Simplified that forces rich, context-specific grammar explanations and forbids generic labels."""
        template_str = self.config.prompt_templates.get("batch", self.config.prompt_templates.get("single", ""))
        
        if not template_str:
            # RICH BATCH PROMPT — explicitly forbids generic explanations
            sentences_text = "\n".join(f"{i+1}. {sent}" for i, sent in enumerate(sentences))
            
            return f"""You are a native-level expert Chinese linguistics teacher specializing in Simplified Chinese.

Analyze the following {len(sentences)} sentences in Simplified Chinese. Focus especially on the word "{target_word}" in each sentence.

Sentences to analyze:
{sentences_text}

For EVERY word, particle, or character in each sentence, provide:
- Exact grammatical role (pronoun, verb, modal particle, structural particle, aspect marker, classifier, etc.)
- DETAILED, CONTEXT-SPECIFIC explanation of what the word does **in this particular sentence** (do NOT use generic definitions)
- Why it is used here and how it affects the meaning or grammar

IMPORTANT: If you cannot provide a detailed, context-specific explanation for a word, write "[WARNING: Explanation missing for this word]" and explain why. NEVER use generic labels like "a word that describes a noun" or "a thing, person, or concept". If you do, the answer will be rejected.

Output format MUST be exactly like this for each sentence:

Grammar Explanations:
我 (pronoun): A first-person singular pronoun meaning 'I'. It functions as the subject of the sentence.
吧 (modal_particle): A sentence-final modal particle indicating suggestion, confirmation, or assumption. It softens the sentence into a polite suggestion here.

Do this for ALL words in ALL sentences. Be detailed and educational — never give generic labels like "a word that describes a noun".

Complexity level: {complexity}
Language: Chinese Simplified (use only Simplified characters)

Return ONLY the structured explanations, no extra text."""

        # If a custom template exists in config, use it
        template = self.jinja_env.from_string(template_str)
        sentences_text = "\n".join(f"{i+1}. {sent}" for i, sent in enumerate(sentences))
        context = {
            "sentences": sentences_text,
            "target_word": target_word or "",
            "complexity": complexity,
            "language": "Chinese Simplified",
            "sentence_count": len(sentences),
            "grammatical_roles": self.config.grammatical_roles,
            "aspect_markers": getattr(self.config, "aspect_markers", {}),
            "modal_particles": getattr(self.config, "modal_particles", {}),
            "structural_particles": getattr(self.config, "structural_particles", {})
        }
        try:
            prompt = template.render(**context)
            logger.debug(f"Generated batch analysis prompt for {len(sentences)} sentences.")
            return prompt
        except Exception as e:
            logger.error(f"Failed to render batch analysis template: {e}")
            # Fallback to rich prompt above
            return f"""You are a native-level expert Chinese linguistics teacher.

Analyze these sentences:
{sentences_text}

Provide detailed, context-specific grammar explanations for every word, especially "{target_word}"."""

    def get_sentence_generation_prompt(
        self,
        word: str,
        language: str,
        num_sentences: int,
        enriched_meaning: str = "",
        min_length: int = 3,
        max_length: int = 15,
        difficulty: str = "intermediate",
        topics: Optional[List[str]] = None
    ) -> str:
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