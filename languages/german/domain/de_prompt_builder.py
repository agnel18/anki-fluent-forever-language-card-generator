# German Prompt Builder
# Builds AI prompts for German grammar analysis
# Enhanced with Jinja2 templates like Spanish gold standard

import logging
from typing import Dict, List, Any, Optional
from jinja2 import Template
from .de_config import DeConfig

logger = logging.getLogger(__name__)

class DePromptBuilder:
    """
    Builds comprehensive prompts for German grammar analysis.
    Handles case system, gender agreement, verb conjugations, and linguistic complexity.
    Based on Duden German grammar standards.
    ENHANCED: Uses Jinja2 templates like Spanish gold standard.
    """

    def __init__(self, config: DeConfig):
        self.config = config
        # Load templates from config like Spanish gold standard
        self.templates = self._load_templates_from_config()

        # Backward compatibility attributes
        self.single_template = self.templates.get('single_analysis')
        self.batch_template = self.templates.get('batch_analysis')

    def _load_templates_from_config(self) -> Dict[str, Template]:
        """Load Jinja2 templates from config - LIKE SPANISH GOLD STANDARD"""
        config_templates = self.config.prompt_templates

        return {
            'single_analysis': Template(config_templates['single']),
            'batch_analysis': Template(config_templates['batch']),
        }

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """
        Build prompt for single sentence analysis.
        German uses case system and V2 word order.
        ENHANCED: Uses Jinja2 template rendering like Spanish gold standard.
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
        ENHANCED: Uses Jinja2 template rendering like Spanish gold standard.
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
Focus on basic word classes and their functions in simple German sentences.
Identify: articles (der/die/das), nouns (Nomen), verbs (Verben), and pronouns.
Note definite/indefinite articles and basic sentence structure.
Consider German as an inflected language with case system and gender agreement.
Examples: Subject-verb-object order, basic greetings, simple statements.""",

            'intermediate': """
Analyze word relationships and grammatical functions in German sentences.
Identify: pronouns (Pronomen), prepositions (Präpositionen), conjunctions (Konjunktionen), adjectives (Adjektive).
Note case system (Nominativ/Akkusativ/Dativ/Genitiv), gender agreement, and syntactic relationships.
Consider separable verbs (trennbare Verben), modal verbs, and adjective declension.
Examples: Complex sentences, relative clauses, prepositional phrases.""",

            'advanced': """
Provide detailed morphological and syntactic analysis of German linguistic structures.
Identify: reflexive verbs (reflexive Verben), subjunctive mood (Konjunktiv), passive voice (Passiv).
Analyze verb conjugation paradigms, case assignment, and complex syntactic structures.
Note word order variations (V2 principle), compound words, and regional variations.
Consider historical linguistic patterns and literary usage.
Examples: Subjunctive in complex sentences, passive constructions, complex conditional structures."""
        }

        return instructions.get(complexity, instructions['beginner'])

    def validate_german_text(self, text: str) -> bool:
        """Validate that text contains German characters"""
        german_chars = set('äöüßÄÖÜẞ')
        return any(char in text for char in german_chars) or len(text.split()) > 0

    def prepare_text_for_analysis(self, text: str) -> str:
        """Prepare German text for analysis"""
        return text.strip()