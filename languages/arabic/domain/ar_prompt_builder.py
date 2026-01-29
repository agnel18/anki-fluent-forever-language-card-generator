# Arabic Prompt Builder
# Handles prompt generation for Arabic grammar analysis
# Key consideration: Arabic is RTL (Right to Left)

import logging
from typing import Dict, List, Any, Optional
from .ar_config import ArConfig

logger = logging.getLogger(__name__)

class ArPromptBuilder:
    """
    Builds prompts for Arabic grammar analysis.
    Handles RTL text direction and Arabic-specific linguistic features.
    """

    def __init__(self, config: ArConfig):
        self.config = config
        self.single_template = config.prompt_templates['single']
        self.batch_template = config.prompt_templates['batch']

    def build_single_prompt(self, sentence: str, target_word: str, complexity: str) -> str:
        """
        Build prompt for single sentence analysis.
        Arabic is RTL, so we need to be careful with text direction.
        """
        grammatical_roles = self._format_grammatical_roles(complexity)

        prompt = self.single_template.format(
            sentence=sentence,
            target_word=target_word,
            complexity=complexity,
            grammatical_roles=grammatical_roles
        )

        return prompt

    def build_batch_prompt(self, sentences: List[str], target_word: str, complexity: str) -> str:
        """
        Build prompt for batch sentence analysis.
        """
        # Format sentences for batch processing
        formatted_sentences = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(sentences))

        grammatical_roles = self._format_grammatical_roles(complexity)

        prompt = self.batch_template.format(
            sentences=formatted_sentences,
            target_word=target_word,
            complexity=complexity,
            grammatical_roles=grammatical_roles
        )

        return prompt

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
Focus on basic word classes and their functions in simple Arabic sentences.
Identify: nouns (أسماء), verbs (أفعال), particles (حروف).
Note definite article usage (ال) and basic sentence structure.
Consider Arabic as a root-based language with Right-to-Left reading direction.
Examples: Subject-verb-object order, basic greetings, simple statements.""",

            'intermediate': """
Analyze word relationships and grammatical functions in Arabic sentences.
Identify: adjectives (صفات), prepositions (حروف جر), conjunctions (حروف عطف), pronouns (ضمائر).
Note case markings (إعراب) in written forms, verb conjugations, and syntactic relationships.
Consider definite article assimilation (sun/moon letters), plural patterns, and compound structures.
Examples: Complex sentences, relative clauses, prepositional phrases.""",

            'advanced': """
Provide detailed morphological and syntactic analysis of Arabic linguistic structures.
Identify: case markings (رفع/نصب/جر), verb forms (أبواب I-X), participles (اسم فاعل/مفعول).
Analyze root-based morphology (جذور ثلاثية/رباعية), plural patterns (سالم/مكسر), and complex syntactic structures.
Note assimilation rules, hamza variations (همزة), emphatic consonants (مظمى), and advanced grammatical features.
Consider historical linguistic patterns, dialectal variations, and literary usage.
Examples: Classical poetry analysis, complex conditional sentences, passive constructions."""
        }

        return instructions.get(complexity, instructions['beginner'])

    def validate_arabic_text(self, text: str) -> bool:
        """Validate that text contains Arabic characters"""
        return self.config.is_arabic_text(text)

    def prepare_text_for_analysis(self, text: str) -> str:
        """Prepare Arabic text for analysis (normalization, etc.)"""
        return self.config.normalize_arabic_text(text)