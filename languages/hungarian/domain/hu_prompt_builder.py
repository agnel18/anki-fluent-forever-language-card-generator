# languages/hungarian/domain/hu_prompt_builder.py
"""
Hungarian Prompt Builder - Domain Component

Constructs AI prompts for Hungarian grammar analysis using Jinja2 templates.
"""

import logging
from typing import List
from jinja2 import Template
from .hu_config import HuConfig

logger = logging.getLogger(__name__)


class HuPromptBuilder:
    """Builds prompts for Hungarian grammar analysis using templates."""

    def __init__(self, config: HuConfig):
        self.config = config
        self.single_template = Template(self.config.prompt_templates['single'])
        self.batch_template = Template(self.config.prompt_templates['batch'])

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """Build prompt for single Hungarian sentence analysis."""
        try:
            grammatical_roles = self._get_grammatical_roles_list(complexity)

            context = {
                'sentence': sentence,
                'target_word': target_word,
                'complexity': complexity,
                'grammatical_roles_list': grammatical_roles,
                'native_language': 'English',
                'language_name': 'Hungarian',
                'patterns': self.config.patterns,
            }
            prompt = self.single_template.render(**context)
            logger.debug(f"Built single Hungarian prompt for complexity {complexity}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build single Hungarian prompt for '{sentence}': {e}")
            return f"""Analyze this Hungarian sentence: {sentence}
Target word: {target_word}
Complexity: {complexity}

Identify case markers, verb conjugation type, preverbs, postpositions, and possessive suffixes.
Return JSON with grammatical analysis."""

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """Build prompt for batch Hungarian sentence analysis."""
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
                'language_name': 'Hungarian',
                'patterns': self.config.patterns,
            }
            prompt = self.batch_template.render(**context)
            logger.debug(f"Built batch Hungarian prompt for {len(sentences)} sentences")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build batch Hungarian prompt: {e}")
            sentences_text = '\n'.join(sentences)
            return f"""Analyze these Hungarian sentences:
{sentences_text}
Target word: {target_word}
Complexity: {complexity}

For each sentence, identify case markers, conjugation type, preverbs, and postpositions.
Return batch JSON response."""

    def _get_grammatical_roles_list(self, complexity: str) -> str:
        """Get formatted list of grammatical roles for the given complexity level."""
        if complexity == "beginner":
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "definite_article", "indefinite_article",
                "conjunction", "copula", "postposition", "preverb", "numeral"
            ]
        elif complexity == "intermediate":
            role_list = [
                "noun", "verb", "definite_conjugation", "indefinite_conjugation",
                "auxiliary_verb", "adjective", "adverb", "pronoun",
                "definite_article", "indefinite_article",
                "conjunction", "copula", "postposition", "preverb", "numeral",
                "accusative", "dative", "instrumental",
                "inessive", "superessive", "sublative",
                "elative", "illative", "allative", "ablative",
                "possessive_suffix"
            ]
        else:  # advanced
            role_list = [
                "noun", "verb", "definite_conjugation", "indefinite_conjugation",
                "auxiliary_verb", "causative_verb", "potential_verb",
                "adjective", "adverb", "pronoun",
                "definite_article", "indefinite_article",
                "conjunction", "copula", "postposition", "preverb", "numeral",
                "accusative", "dative", "instrumental",
                "causal_final", "translative",
                "inessive", "superessive", "adessive",
                "sublative", "delative", "elative",
                "illative", "allative", "ablative",
                "terminative", "essive_formal", "distributive",
                "possessive_suffix", "interjection"
            ]

        return '\n'.join([f'- {role.replace("_", " ")}' for role in role_list])
