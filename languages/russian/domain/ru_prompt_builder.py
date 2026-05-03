# languages/russian/domain/ru_prompt_builder.py
"""
Russian Prompt Builder — Domain Component

Constructs AI prompts for Russian grammar analysis at various complexity levels.
"""

from typing import Optional
from .ru_config import RuConfig


class RuPromptBuilder:
    """
    Builds grammar analysis prompts for Russian.
    Uses Jinja2 templates for flexibility and maintainability.
    """

    def __init__(self, config: RuConfig):
        raise NotImplementedError("Phase 3")

    def build_single_prompt(
        self, sentence: str, target_word: str, complexity: str
    ) -> str:
        raise NotImplementedError("Phase 3")

    def build_batch_prompt(
        self, sentences: list, target_words: list, complexity: str
    ) -> str:
        raise NotImplementedError("Phase 3")
