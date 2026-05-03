# languages/english/en_analyzer.py
"""
English Grammar Analyzer — Facade

Implements BaseGrammarAnalyzer for the English language.
Orchestrates domain components: config, prompt_builder, response_parser, validator, fallbacks.

Lazy imports inside _call_ai() follow the required pattern to support test mocking
and avoid cross-test contamination (see CLAUDE.md — Analyzer import patterns).

Class name: EnAnalyzer  (auto-discovered by analyzer_registry.py)
"""

import logging
import time
from typing import Any, Dict, List, Optional

from streamlit_app.language_analyzers.base_analyzer import (
    BaseGrammarAnalyzer,
    GrammarAnalysis,
    LanguageConfig,
)

from .domain.en_config import EnConfig
from .domain.en_prompt_builder import EnPromptBuilder
from .domain.en_response_parser import EnResponseParser
from .domain.en_fallbacks import EnFallbacks
from .domain.en_validator import EnValidator

logger = logging.getLogger(__name__)


class EnAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for English.

    English — West Germanic, Indo-European family.
    Key features: analytic morphology, strict SVO word order, auxiliary verb system,
    minimal inflection, phrasal verbs, categorical ambiguity.

    Script: Latin (LTR).
    Complexity levels: beginner, intermediate, advanced.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "en"
    LANGUAGE_NAME = "English"

    def __init__(self):
        # Initialise domain components
        self.en_config = EnConfig()
        self.en_fallbacks = EnFallbacks(self.en_config)
        self.prompt_builder = EnPromptBuilder(self.en_config)
        self.response_parser = EnResponseParser(self.en_config, self.en_fallbacks)
        self.validator = EnValidator(self.en_config)

        config = LanguageConfig(
            code="en",
            name="English",
            native_name="English",
            family="Indo-European",
            script_type="alphabetic",
            complexity_rating="medium",
            key_features=[
                "analytic_morphology",
                "auxiliary_stack",
                "strict_svo",
                "minimal_inflection",
                "phrasal_verbs",
            ],
            supported_complexity_levels=["beginner", "intermediate", "advanced"],
        )
        super().__init__(config)

    # ------------------------------------------------------------------
    # BaseGrammarAnalyzer abstract methods
    # ------------------------------------------------------------------

    def get_grammar_prompt(
        self, complexity: str, sentence: str, target_word: str
    ) -> str:
        raise NotImplementedError("Phase 3")

    def parse_grammar_response(
        self, ai_response: str, complexity: str, sentence: str
    ) -> Dict[str, Any]:
        raise NotImplementedError("Phase 3")

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        raise NotImplementedError("Phase 3")

    def validate_analysis(
        self, parsed_data: Dict[str, Any], original_sentence: str
    ) -> float:
        raise NotImplementedError("Phase 3")

    # ------------------------------------------------------------------
    # Single sentence analysis
    # ------------------------------------------------------------------

    def analyze_grammar(
        self,
        sentence: str,
        target_word: str,
        complexity: str,
        gemini_api_key: str,
    ) -> GrammarAnalysis:
        """Analyse grammar for a single English sentence."""
        raise NotImplementedError("Phase 3")

    # ------------------------------------------------------------------
    # Batch analysis
    # ------------------------------------------------------------------

    def batch_analyze_grammar(
        self,
        sentences: List[str],
        target_word: str,
        complexity: str,
        gemini_api_key: str,
    ) -> List[GrammarAnalysis]:
        """Analyse grammar for multiple English sentences in one AI call."""
        raise NotImplementedError("Phase 3")

    # ------------------------------------------------------------------
    # AI call — lazy import to support test mocking (per CLAUDE.md)
    # ------------------------------------------------------------------

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """Call Gemini AI for English grammar analysis. Lazy imports required."""
        raise NotImplementedError("Phase 3")

    # ------------------------------------------------------------------
    # HTML output generation
    # ------------------------------------------------------------------

    def _generate_html_output(
        self,
        parsed_data: Dict[str, Any],
        sentence: str,
        complexity: str,
    ) -> str:
        """Generate HTML with inline color styling for Anki display."""
        raise NotImplementedError("Phase 3")

    def _map_grammatical_role_to_category(self, role: str) -> str:
        """Map an English role label to a broad category (for legacy callers)."""
        raise NotImplementedError("Phase 3")
