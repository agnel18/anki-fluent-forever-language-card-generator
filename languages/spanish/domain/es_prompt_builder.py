# Spanish Prompt Builder
# Handles prompt generation for Spanish grammar analysis
# Key consideration: Spanish is LTR (Left to Right)
# ENHANCED: Now uses Jinja2 templates like Hindi gold standard

import logging
from typing import Dict, List, Any, Optional
from jinja2 import Template
from .es_config import EsConfig

logger = logging.getLogger(__name__)

class EsPromptBuilder:
    """
    Builds prompts for Spanish grammar analysis.
    Handles LTR text direction and Spanish-specific linguistic features.
    ENHANCED: Uses Jinja2 templates like Hindi gold standard.
    """

    def __init__(self, config: EsConfig):
        self.config = config
        # Load templates from config like Hindi gold standard
        self.templates = self._load_templates_from_config()
        
        # Backward compatibility attributes
        self.single_template = self.templates.get('single_analysis')
        self.batch_template = self.templates.get('batch_analysis')

    def _load_templates_from_config(self) -> Dict[str, Template]:
        """Load Jinja2 templates from config - LIKE HINDI GOLD STANDARD"""
        config_templates = self.config.prompt_templates

        return {
            'single_analysis': Template(config_templates['single']),
            'batch_analysis': Template(config_templates['batch']),
        }

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """
        Build prompt for single sentence analysis.
        Spanish is LTR, so standard text direction.
        ENHANCED: Uses Jinja2 template rendering like Hindi gold standard.
        """
        grammatical_roles = self._format_grammatical_roles(complexity)

        context = {
            'sentence': sentence,
            'target_word': target_word,
            'complexity': complexity,
            'language_name': self.config.language_name,
            'grammatical_roles': grammatical_roles
        }

        return self.templates['single_analysis'].render(**context)

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """
        Build prompt for batch sentence analysis.
        ENHANCED: Uses Jinja2 template rendering like Hindi gold standard.
        """
        # Format sentences for batch processing
        formatted_sentences = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        grammatical_roles = self._format_grammatical_roles(complexity)

        context = {
            'sentences': formatted_sentences,
            'target_word': target_word,
            'complexity': complexity,
            'batch_size': len(sentences),
            'grammatical_roles': grammatical_roles
        }

        return self.templates['batch_analysis'].render(**context)

    def _format_grammatical_roles(self, complexity: str) -> str:
        """Format grammatical roles for prompt inclusion"""
        roles = self.config.get_grammatical_roles(complexity)

        # Format as bullet points for clarity
        formatted_roles = []
        for role_key, role_description in roles.items():
            formatted_roles.append(f"- {role_key}: {role_description}")

        return "\n".join(formatted_roles)

    def get_complexity_specific_instructions(self, complexity: str) -> str:
        """Get complexity-specific analysis instructions based on comprehensive grammar concepts"""
        instructions = {
            'beginner': """
Focus on basic word classes and their functions in simple Spanish sentences.
Identify: nouns (sustantivos), verbs (verbos), adjectives (adjetivos).
Note definite/indefinite articles (el/la, un/una) and basic sentence structure.
Consider Spanish as an inflected language with gender agreement and verb conjugation.
Examples: Subject-verb-object order, basic greetings, simple statements.""",

            'intermediate': """
Analyze word relationships and grammatical functions in Spanish sentences.
Identify: pronouns (pronombres), prepositions (preposiciones), conjunctions (conjunciones), adverbs (adverbios).
Note gender/number agreement, verb tenses, and syntactic relationships.
Consider ser/estar distinction, por/para usage, and adjective position.
Examples: Complex sentences, relative clauses, prepositional phrases.""",

            'advanced': """
Provide detailed morphological and syntactic analysis of Spanish linguistic structures.
Identify: clitic pronouns (pronombres clíticos), subjunctive mood (subjuntivo), differential object marking.
Analyze verb conjugation paradigms, agreement patterns, and complex syntactic structures.
Note regional variations (leísmo/loísmo), adjective position effects on meaning, and advanced grammatical features.
Consider historical linguistic patterns and literary usage.
Examples: Subjunctive in complex sentences, passive constructions, complex conditional structures."""
        }

        return instructions.get(complexity, instructions['beginner'])

    def validate_spanish_text(self, text: str) -> bool:
        """Validate that text contains Spanish characters"""
        return self.config.is_spanish_text(text)

    def prepare_text_for_analysis(self, text: str) -> str:
        """Prepare Spanish text for analysis (normalization, etc.)"""
        # Basic normalization for Spanish
        return text.strip()