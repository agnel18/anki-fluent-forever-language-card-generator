# languages/french/domain/fr_prompt_builder.py
"""
French Prompt Builder - Domain Component

FRENCH PROMPT BUILDING:
This component demonstrates how to construct effective AI prompts for French grammar analysis.
It uses Jinja2 templates for maintainable, parameterized prompts.

RESPONSIBILITIES:
1. Build single-sentence analysis prompts
2. Build batch analysis prompts for multiple sentences
3. Parameterize prompts with French-specific context
4. Ensure prompts produce consistent JSON output
5. Handle template rendering errors gracefully

PROMPT ENGINEERING PRINCIPLES:
- Clear instructions: Explicit JSON structure requirements
- Contextual information: Include complexity level and target word
- Error prevention: Specify exact field names and formats
- Language specificity: French-appropriate grammatical categories
- Consistency: Same structure for single and batch prompts

USAGE FOR FRENCH:
1. Copy template structure and modify content
2. Update grammatical role lists for French features
3. Adjust examples and instructions for French-specific features
4. Test prompts produce valid JSON with expected structure
5. Include French-specific prompt context and examples

INTEGRATION:
- Called by main analyzer for prompt generation
- Receives configuration from FrConfig
- Templates support parameterization for different contexts
- Error handling prevents crashes from template issues
"""

import logging
from typing import List
from jinja2 import Template
from .fr_config import FrConfig

logger = logging.getLogger(__name__)

class FrPromptBuilder:
    """
    Builds prompts for French grammar analysis using templates.

    FRENCH TEMPLATE SYSTEM:
    - Jinja2 templates: Maintainable and parameterized
    - Language-specific: French-appropriate instructions and examples
    - Structured output: Explicit JSON format requirements
    - Error handling: Graceful fallbacks for template failures

    TEMPLATE FEATURES:
    - Complexity-aware: Different instructions for different levels
    - Target word highlighting: Special handling for focus words
    - Batch support: Efficient multi-sentence processing
    - JSON validation: Clear structure requirements
    - French-specific: Gender agreement, verb conjugations, preposition usage
    """

    def __init__(self, config: FrConfig):
        """
        Initialize with configuration.

        TEMPLATE INITIALIZATION:
        1. Store config reference for access to templates and settings
        2. Pre-compile templates for performance
        3. Validate template availability
        4. Set up error handling for template rendering
        """
        self.config = config
        self.single_template = Template(self.config.prompt_templates['single'])
        self.batch_template = Template(self.config.prompt_templates['batch'])

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """
        Build prompt for single French sentence analysis.

        FRENCH SINGLE PROMPT:
        - Includes French-specific grammatical roles
        - Emphasizes gender agreement and verb conjugations
        - Provides French-appropriate examples
        - Ensures detailed morphological analysis
        """
        try:
            # Get grammatical roles list based on complexity
            grammatical_roles = self._get_grammatical_roles_list(complexity)

            context = {
                'sentence': sentence,
                'target_word': target_word,
                'complexity': complexity,
                'grammatical_roles_list': grammatical_roles,
                'native_language': 'English',
                'language_name': 'French',
                'patterns': self.config.patterns,
            }
            prompt = self.single_template.render(**context)
            logger.debug(f"Built single French prompt for complexity {complexity}")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build single French prompt for '{sentence}': {e}")
            return f"""Analyze this French sentence: {sentence}
Target word: {target_word}
Complexity: {complexity}

Identify the grammatical role of each word and explain gender agreement, verb conjugations, and French-specific features.
Return JSON with grammatical analysis."""

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """
        Build prompt for batch French sentence analysis.

        FRENCH BATCH PROMPT:
        - Processes multiple sentences efficiently
        - Maintains French-specific analysis requirements
        - Ensures consistent output format across sentences
        """
        try:
            # Get grammatical roles list based on complexity
            grammatical_roles = self._get_grammatical_roles_list(complexity)

            # Format sentences for the prompt
            sentences_text = '\n'.join([f'{i+1}. {sentence}' for i, sentence in enumerate(sentences)])

            context = {
                'sentences': sentences,
                'sentences_text': sentences_text,
                'target_word': target_word,
                'complexity': complexity,
                'grammatical_roles_list': grammatical_roles,
                'native_language': 'English',
                'language_name': 'French',
                'patterns': self.config.patterns,
            }
            prompt = self.batch_template.render(**context)
            logger.debug(f"Built batch French prompt for {len(sentences)} sentences")
            return prompt
        except Exception as e:
            logger.error(f"Failed to build batch French prompt: {e}")
            sentences_text = '\n'.join(sentences)
            return f"""Analyze these French sentences:
{sentences_text}
Target word: {target_word}
Complexity: {complexity}

For each sentence, provide grammatical analysis with gender agreement and verb conjugation details.
Return batch JSON response."""

    def _get_grammatical_roles_list(self, complexity: str) -> str:
        """
        Get formatted list of grammatical roles for the given complexity level.

        ROLE LIST FORMATTING:
        - Beginner: Core roles only
        - Intermediate: More detailed roles
        - Advanced: Full role hierarchy
        """
        roles = self.config.grammatical_roles

        if complexity == "beginner":
            role_list = [
                "noun", "verb", "adjective", "adverb", "pronoun",
                "determiner", "preposition", "conjunction"
            ]
        elif complexity == "intermediate":
            role_list = [
                "noun", "verb", "auxiliary_verb", "modal_verb", "adjective",
                "adverb", "pronoun", "personal_pronoun", "reflexive_pronoun",
                "possessive_pronoun", "demonstrative_pronoun", "determiner",
                "definite_article", "indefinite_article", "partitive_article",
                "preposition", "conjunction"
            ]
        else:  # advanced
            role_list = [
                "noun", "proper_noun", "common_noun", "verb", "auxiliary_verb",
                "modal_verb", "reflexive_verb", "irregular_verb", "regular_er_verb",
                "regular_ir_verb", "regular_re_verb", "adjective", "possessive_adjective",
                "demonstrative_adjective", "interrogative_adjective", "indefinite_adjective",
                "adverb", "pronoun", "personal_pronoun", "reflexive_pronoun",
                "possessive_pronoun", "demonstrative_pronoun", "relative_pronoun",
                "indefinite_pronoun", "determiner", "definite_article", "indefinite_article",
                "partitive_article", "possessive_determiner", "demonstrative_determiner",
                "preposition", "conjunction", "interjection"
            ]

        # Format as bullet list
        formatted_list = '\n'.join([f'- {role.replace("_", " ")}' for role in role_list])
        return formatted_list