# languages/english/domain/en_prompt_builder.py
"""
English Prompt Builder — Domain Component

Builds AI prompts for English grammar analysis.
English-specific: highlights analytic morphology, auxiliary stacks,
phrasal verbs, and categorical ambiguity.
"""

import logging
from typing import List, Optional

from .en_config import EnConfig

logger = logging.getLogger(__name__)


class EnPromptBuilder:
    """Builds prompts for English grammar analysis using Gemini AI."""

    def __init__(self, config: EnConfig):
        raise NotImplementedError("Phase 3")

    def build_single_prompt(
        self, sentence: str, target_word: str, complexity: str
    ) -> str:
        """Build a prompt for analysing one English sentence."""
        raise NotImplementedError("Phase 3")

    def build_batch_prompt(
        self, sentences: List[str], target_word: str, complexity: str
    ) -> str:
        """Build a prompt for analysing multiple English sentences."""
        raise NotImplementedError("Phase 3")
