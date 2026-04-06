# languages/korean/domain/ko_prompt_builder.py
"""
Korean Prompt Builder - Domain Component

Constructs AI prompts for Korean grammar analysis using Jinja2 templates.
"""

import logging
from typing import List
from jinja2 import Template
from .ko_config import KoConfig

logger = logging.getLogger(__name__)


class KoPromptBuilder:
    """Builds prompts for Korean grammar analysis using templates."""

    def __init__(self, config: KoConfig):
        self.config = config
        self.single_template = Template(self.config.prompt_templates['single'])
        self.batch_template = Template(self.config.prompt_templates['batch'])

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build prompt for single Korean sentence analysis."""
        try:
            grammatical_roles = self._get_grammatical_roles_list(complexity)

            context = {
                'sentence': sentence,
                'target_word': target_word,
                'complexity': complexity,
                'grammatical_roles_list': grammatical_roles,
                'native_language': 'English',
                'language_name': 'Korean',
                'patterns': self.config.patterns,
            }
            prompt = self.single_template.render(**context)
            logger.debug(f"Built single Korean prompt for complexity {complexity}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build single Korean prompt for '{sentence}': {e}")
            return f"""Analyze this Korean sentence: {sentence}
Target word: {target_word}
Complexity: {complexity}

Identify particles, verb conjugations, speech levels, and honorific forms.
Return JSON with grammatical analysis."""

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Build prompt for batch Korean sentence analysis."""
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
                'language_name': 'Korean',
                'patterns': self.config.patterns,
            }
            prompt = self.batch_template.render(**context)
            logger.debug(f"Built batch Korean prompt for {len(sentences)} sentences")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build batch Korean prompt: {e}")
            sentences_text = '\n'.join(sentences)
            return f"""Analyze these Korean sentences:
{sentences_text}
Target word: {target_word}
Complexity: {complexity}

For each sentence, identify particles, verb conjugations, and speech levels.
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
                "noun", "verb", "auxiliary_verb", "adjective",
                "adverb", "particle", "topic_marker", "subject_marker",
                "object_marker", "locative_particle", "copula",
                "counter", "conjunction", "pronoun", "connective_ending"
            ]
        else:  # advanced
            role_list = [
                "noun", "verb", "auxiliary_verb", "honorific_verb", "humble_verb",
                "passive_verb", "causative_verb",
                "adjective", "descriptive_verb", "adverb",
                "particle", "topic_marker", "subject_marker", "object_marker",
                "honorific_particle", "possessive_particle", "locative_particle",
                "instrumental_particle", "comitative_particle",
                "copula", "counter", "conjunction", "pronoun", "interjection",
                "connective_ending", "sentence_final_ending",
                "nominalizer", "quotative"
            ]

        return '\n'.join([f'- {role.replace("_", " ")}' for role in role_list])
