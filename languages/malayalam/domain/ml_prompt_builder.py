# languages/malayalam/domain/ml_prompt_builder.py
"""
Malayalam Prompt Builder - Domain Component

Constructs AI prompts for Malayalam grammar analysis using Jinja2 templates.
"""

import logging
from typing import List
from jinja2 import Template
from .ml_config import MlConfig

logger = logging.getLogger(__name__)


class MlPromptBuilder:
    """Builds prompts for Malayalam grammar analysis using templates."""

    def __init__(self, config: MlConfig):
        self.config = config
        self.single_template = Template(self.config.prompt_templates['single'])
        self.batch_template = Template(self.config.prompt_templates['batch'])

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build prompt for single Malayalam sentence analysis."""
        try:
            grammatical_roles = self._get_grammatical_roles_list(complexity)

            context = {
                'sentence': sentence,
                'target_word': target_word,
                'complexity': complexity,
                'grammatical_roles_list': grammatical_roles,
                'native_language': 'English',
                'language_name': 'Malayalam',
                'patterns': self.config.patterns,
            }
            prompt = self.single_template.render(**context)
            logger.debug(f"Built single Malayalam prompt for complexity {complexity}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build single Malayalam prompt for '{sentence}': {e}")
            return f"""Analyze this Malayalam sentence: {sentence}
Target word: {target_word}
Complexity: {complexity}

Malayalam is a Dravidian agglutinative language with SOV word order.
Identify case markers, verb tenses, postpositions, and grammatical roles.
Return JSON with grammatical analysis."""

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Build prompt for batch Malayalam sentence analysis."""
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
                'language_name': 'Malayalam',
                'patterns': self.config.patterns,
            }
            prompt = self.batch_template.render(**context)
            logger.debug(f"Built batch Malayalam prompt for {len(sentences)} sentences")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build batch Malayalam prompt: {e}")
            sentences_text = '\n'.join(sentences)
            return f"""Analyze these Malayalam sentences:
{sentences_text}
Target word: {target_word}
Complexity: {complexity}

For each sentence, identify grammatical roles and provide analysis.
Return batch JSON response."""

    def _get_grammatical_roles_list(self, complexity: str) -> str:
        """Get formatted list of grammatical roles for the given complexity level."""
        if complexity == "beginner":
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "postposition", "conjunction", "copula", "demonstrative"
            ]
        elif complexity == "intermediate":
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "postposition", "conjunction", "case_marker",
                "verbal_participle", "auxiliary_verb", "copula",
                "negative_particle", "question_particle", "emphatic_particle",
                "honorific_pronoun", "demonstrative", "determiner", "infinitive"
            ]
        else:  # advanced
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "postposition", "conjunction", "case_marker",
                "verbal_participle", "auxiliary_verb", "causative_verb",
                "passive_verb", "copula", "negative_particle",
                "question_particle", "emphatic_particle", "honorific_pronoun",
                "relative_participle", "conditional_form", "concessive_form",
                "infinitive", "classifier", "demonstrative", "determiner",
                "interjection"
            ]

        return '\n'.join([f'- {role.replace("_", " ")}' for role in role_list])
