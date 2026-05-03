# languages/english/domain/en_fallbacks.py
"""
English Fallbacks — Domain Component

Rule-based fallback analysis for English grammar when AI calls fail.
Provides basic morphological and syntactic analysis without AI.
"""

import logging
from typing import Dict, Any

from .en_config import EnConfig

logger = logging.getLogger(__name__)


class EnFallbacks:
    """Rule-based fallback analysis for English."""

    def __init__(self, config: EnConfig):
        raise NotImplementedError("Phase 3")

    def create_fallback(
        self, sentence: str, complexity: str
    ) -> Dict[str, Any]:
        """Create a rule-based fallback analysis."""
        raise NotImplementedError("Phase 3")
