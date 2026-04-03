# languages/japanese/domain/ja_prompt_builder.py
"""
Japanese Prompt Builder - Domain Component

Constructs AI prompts for Japanese grammar analysis using Jinja2 templates.
"""

import logging
from typing import List
from jinja2 import Template
from .ja_config import JaConfig

logger = logging.getLogger(__name__)


class JaPromptBuilder:
    """Builds prompts for Japanese grammar analysis using templates."""

    def __init__(self, config: JaConfig):
        self.config = config
        self.single_template = Template(self.config.prompt_templates['single'])
        self.batch_template = Template(self.config.prompt_templates['batch'])

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build prompt for single Japanese sentence analysis."""
        try:
            grammatical_roles = self._get_grammatical_roles_list(complexity)

            context = {
                'sentence': sentence,
                'target_word': target_word,
                'complexity': complexity,
                'grammatical_roles_list': grammatical_roles,
                'native_language': 'English',
                'language_name': 'Japanese',
                'patterns': self.config.patterns,
            }
            prompt = self.single_template.render(**context)
            logger.debug(f"Built single Japanese prompt for complexity {complexity}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build single Japanese prompt for '{sentence}': {e}")
            return f"""Analyze this Japanese sentence: {sentence}
Target word: {target_word}
Complexity: {complexity}

Break the sentence into individual words/morphemes (Japanese has no spaces).
Identify particles, verb forms, adjective types, and politeness levels.
Return JSON with grammatical analysis."""

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Build prompt for batch Japanese sentence analysis."""
        try:
            grammatical_roles = self._get_grammatical_roles_list(complexity)
            sentences_text = '\n'.join([f'{i+1}. {sentence}' for i, sentence in enumerate(sentences)])

            context = {
                'sentences': sentences,
                'sentences_text': sentences_text,
                'target_word': target_word,
                'complexity': complexity,
                'grammatical_roles_list': grammatical_roles,
                'native_language': 'English',
                'language_name': 'Japanese',
                'patterns': self.config.patterns,
            }
            prompt = self.batch_template.render(**context)
            logger.debug(f"Built batch Japanese prompt for {len(sentences)} sentences")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build batch Japanese prompt: {e}")
            sentences_text = '\n'.join(sentences)
            return f"""Analyze these Japanese sentences:
{sentences_text}
Target word: {target_word}
Complexity: {complexity}

For each sentence, break into words/morphemes and provide grammatical analysis.
Return batch JSON response."""

    def _get_grammatical_roles_list(self, complexity: str) -> str:
        """Get formatted list of grammatical roles for the given complexity level."""
        if complexity == "beginner":
            role_list = [
                "noun", "verb", "adjective", "adverb", "particle",
                "copula", "conjunction", "pronoun"
            ]
        elif complexity == "intermediate":
            role_list = [
                "noun", "verb", "auxiliary_verb", "i_adjective", "na_adjective",
                "adverb", "particle", "topic_particle", "subject_particle",
                "object_particle", "copula", "counter", "conjunction", "pronoun"
            ]
        else:  # advanced
            role_list = [
                "noun", "verb", "auxiliary_verb", "honorific_verb", "humble_verb",
                "potential_verb", "passive_verb", "causative_verb",
                "i_adjective", "na_adjective", "adverb",
                "particle", "topic_particle", "subject_particle", "object_particle",
                "sentence_final_particle", "nominalizer", "quotation_particle",
                "copula", "counter", "conjunction", "pronoun", "interjection",
                "te_form", "conditional_form", "volitional_form"
            ]

        return '\n'.join([f'- {role.replace("_", " ")}' for role in role_list])
