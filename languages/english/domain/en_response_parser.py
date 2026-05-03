# languages/english/domain/en_response_parser.py
"""
English Response Parser — Domain Component

Parses Gemini AI responses into structured grammar analysis.
Handles 5-level fallback parsing chain: direct JSON, Markdown code block,
JSON repair, text patterns, rule-based fallback.
"""

import logging
from typing import Dict, Any, List, Optional

from .en_config import EnConfig
from .en_fallbacks import EnFallbacks

logger = logging.getLogger(__name__)


class EnResponseParser:
    """Parses AI responses for English grammar analysis."""

    def __init__(self, config: EnConfig, fallbacks: EnFallbacks):
        raise NotImplementedError("Phase 3")

    def parse_response(
        self,
        ai_response: str,
        complexity: str,
        sentence: str,
        target_word: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parse a single AI response."""
        raise NotImplementedError("Phase 3")

    def parse_batch_response(
        self,
        ai_response: str,
        sentences: List[str],
        complexity: str,
        target_word: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Parse a batch AI response."""
        raise NotImplementedError("Phase 3")
