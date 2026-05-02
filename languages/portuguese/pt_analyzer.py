# languages/portuguese/pt_analyzer.py
"""
Portuguese Grammar Analyzer — Clean Architecture Facade

Implements BaseGrammarAnalyzer for Portuguese (both Brazilian and European
varieties as a single analyzer with register tagging).

Lazy imports inside _call_ai() follow the required pattern (per CLAUDE.md
"Analyzer import patterns") to support unittest.mock.patch() and avoid
cross-test contamination during analyzer auto-discovery.

Class name: PtAnalyzer  (auto-discovered by analyzer_registry.py)

Distinctive Portuguese features handled:
  - Three-state clitic placement (proclitic / enclitic / mesoclitic)
  - Object-clitic allomorphs (-lo / -no after r/s/z and nasal endings)
  - Obligatory contractions (do, no, ao, pelo, dele, naquele, daquilo, ...)
  - Ser vs estar copula split with copula_type meta-field
  - Personal infinitive vs future subjunctive disambiguation by trigger
  - BR / PT register tagging
  - Productive future subjunctive
  - Debitive (ter de / ter que + infinitive)
"""

import logging
import time
from typing import Any, Dict, List, Optional

from streamlit_app.language_analyzers.base_analyzer import (
    BaseGrammarAnalyzer,
    GrammarAnalysis,
    LanguageConfig,
)

from .domain.pt_config import PtConfig
from .domain.pt_prompt_builder import PtPromptBuilder
from .domain.pt_response_parser import PtResponseParser
from .domain.pt_fallbacks import PtFallbacks
from .domain.pt_validator import PtValidator

# IMPORTANT: streamlit_app.shared_utils is imported lazily inside _call_ai().
# Module-level imports break unittest.mock.patch() during analyzer discovery.

logger = logging.getLogger(__name__)


class PtAnalyzer(BaseGrammarAnalyzer):
    """
    Grammar analyzer for Portuguese (Português).

    Indo-European, Romance, Western Romance, Ibero-Romance.
    Script: Latin with diacritics (LTR).
    Complexity levels: beginner, intermediate, advanced.

    Key features:
      ser_estar_split, three_state_clitics, obligatory_contractions,
      personal_infinitive, future_subjunctive, fusional_morphology,
      grammatical_gender, br_pt_register_split, debitive_construction.
    """

    VERSION = "1.0"
    LANGUAGE_CODE = "pt"
    LANGUAGE_NAME = "Portuguese"

    def __init__(self):
        # Initialise domain components
        self.pt_config = PtConfig()
        self.pt_fallbacks = PtFallbacks(self.pt_config)
        self.prompt_builder = PtPromptBuilder(self.pt_config)
        self.response_parser = PtResponseParser(self.pt_config, self.pt_fallbacks)
        self.validator = PtValidator(self.pt_config)
        # Convenience alias matching French gold-standard naming
        self.fallbacks = self.pt_fallbacks

        config = LanguageConfig(
            code="pt",
            name="Portuguese",
            native_name="Português",
            family="Indo-European",
            script_type="alphabetic",
            complexity_rating="high",
            key_features=[
                "ser_estar_split",
                "three_state_clitics",
                "obligatory_contractions",
                "personal_infinitive",
                "future_subjunctive",
                "fusional_morphology",
                "grammatical_gender",
                "br_pt_register_split",
                "debitive_construction",
                "pro_drop",
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
        """Generate Portuguese-specific AI prompt for grammar analysis."""
        return self.prompt_builder.build_single_prompt(
            sentence, target_word, complexity
        )

    def parse_grammar_response(
        self, ai_response: str, complexity: str, sentence: str
    ) -> Dict[str, Any]:
        """Parse AI response into standardised grammar analysis format."""
        return self.response_parser.parse_response(
            ai_response, complexity, sentence
        )

    def get_color_scheme(self, complexity: str) -> Dict[str, str]:
        """Return color scheme for Portuguese grammatical roles."""
        return self.pt_config.get_color_scheme(complexity)

    def validate_analysis(
        self, parsed_data: Dict[str, Any], original_sentence: str
    ) -> float:
        """Validate analysis quality and return confidence score."""
        result = self.validator.validate_result(parsed_data, original_sentence)
        return result.get("confidence", 0.0)

    # ------------------------------------------------------------------
    # Sentence generation prompt — REQUIRED override (per CLAUDE.md)
    # Without this the system falls back to a generic prompt and we lose
    # Portuguese-specific sentence quality.
    # ------------------------------------------------------------------

    def get_sentence_generation_prompt(
        self,
        word: str,
        language: str,
        num_sentences: int,
        enriched_meaning: str = "",
        min_length: int = 3,
        max_length: int = 15,
        difficulty: str = "intermediate",
        topics: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Get Portuguese-specific sentence generation prompt.
        Delegates to the prompt builder.
        """
        return self.prompt_builder.get_sentence_generation_prompt(
            word=word,
            language=language,
            num_sentences=num_sentences,
            enriched_meaning=enriched_meaning,
            min_length=min_length,
            max_length=max_length,
            difficulty=difficulty,
            topics=topics,
        )

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
        """Analyse grammar for a single Portuguese sentence."""
        # Honour user difficulty when explicitly invoked elsewhere — but
        # respect the complexity argument when caller provided one.
        complexity = self._resolve_complexity(complexity)

        try:
            start = time.time()
            logger.info(
                f"Portuguese analysis: '{sentence[:50]}...' "
                f"(complexity: {complexity})"
            )

            prompt = self.prompt_builder.build_single_prompt(
                sentence, target_word, complexity
            )
            ai_response = self._call_ai(prompt, gemini_api_key)
            result = self.response_parser.parse_response(
                ai_response, complexity, sentence, target_word
            )
            validated = self.validator.validate_result(result, sentence)

            # Quality adjustment
            quality = self.validator.validate_explanation_quality(validated)
            base_conf = validated.get("confidence", 0.5)
            quality_score = quality.get("quality_score", 1.0)
            confidence = min(base_conf * quality_score, 1.0)
            validated["confidence"] = confidence
            validated["explanation_quality"] = quality

            html_output = self._generate_html_output(validated, sentence, complexity)
            elapsed = time.time() - start
            logger.info(
                f"Portuguese analysis done in {elapsed:.2f}s, "
                f"confidence={confidence:.2f}"
            )

            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=validated.get("elements", {}),
                explanations=validated.get("explanations", {}),
                word_explanations=validated.get("word_explanations", []),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=confidence,
            )

        except Exception as exc:
            logger.error(f"Portuguese analysis failed for '{sentence[:60]}': {exc}")
            fallback = self.fallbacks.create_fallback(sentence, complexity)
            html_output = self._generate_html_output(fallback, sentence, complexity)
            return GrammarAnalysis(
                sentence=sentence,
                target_word=target_word or "",
                language_code=self.language_code,
                complexity_level=complexity,
                grammatical_elements=fallback.get("elements", {}),
                explanations=fallback.get("explanations", {}),
                word_explanations=fallback.get("word_explanations", []),
                color_scheme=self.get_color_scheme(complexity),
                html_output=html_output,
                confidence_score=fallback.get("confidence", 0.3),
            )

    # ------------------------------------------------------------------
    # Batch analysis — matches Japanese / Latvian pattern exactly,
    # returns List[GrammarAnalysis] (NOT List[Dict]).
    # ------------------------------------------------------------------

    def batch_analyze_grammar(
        self,
        sentences: List[str],
        target_word: str,
        complexity: str,
        gemini_api_key: str,
    ) -> List[GrammarAnalysis]:
        """Analyse grammar for multiple Portuguese sentences in one AI call."""
        complexity = self._resolve_complexity(complexity)
        logger.info(
            f"Portuguese batch analyse: {len(sentences)} sentences, "
            f"complexity={complexity}"
        )
        try:
            prompt = self.prompt_builder.build_batch_prompt(
                sentences, target_word, complexity
            )
            ai_response = self._call_ai(prompt, gemini_api_key)
            results = self.response_parser.parse_batch_response(
                ai_response, sentences, complexity, target_word
            )

            grammar_analyses: List[GrammarAnalysis] = []
            for result, sentence in zip(results, sentences):
                validated = self.validator.validate_result(result, sentence)
                html_output = self._generate_html_output(validated, sentence, complexity)
                grammar_analyses.append(
                    GrammarAnalysis(
                        sentence=sentence,
                        target_word=target_word or "",
                        language_code=self.language_code,
                        complexity_level=complexity,
                        grammatical_elements=validated.get("elements", {}),
                        explanations=validated.get("explanations", {}),
                        color_scheme=self.get_color_scheme(complexity),
                        html_output=html_output,
                        confidence_score=validated.get("confidence", 0.0),
                        word_explanations=validated.get("word_explanations", []),
                    )
                )
            return grammar_analyses

        except Exception as exc:
            logger.error(f"Portuguese batch analysis failed: {exc}")
            fallback_analyses: List[GrammarAnalysis] = []
            for sentence in sentences:
                fallback = self.fallbacks.create_fallback(sentence, complexity)
                html_output = self._generate_html_output(fallback, sentence, complexity)
                fallback_analyses.append(
                    GrammarAnalysis(
                        sentence=sentence,
                        target_word=target_word or "",
                        language_code=self.language_code,
                        complexity_level=complexity,
                        grammatical_elements=fallback.get("elements", {}),
                        explanations=fallback.get("explanations", {}),
                        color_scheme=self.get_color_scheme(complexity),
                        html_output=html_output,
                        confidence_score=fallback.get("confidence", 0.3),
                        word_explanations=fallback.get("word_explanations", []),
                    )
                )
            return fallback_analyses

    # ------------------------------------------------------------------
    # AI call — LAZY IMPORT (per CLAUDE.md)
    # NEVER move the streamlit_app.shared_utils import to module scope.
    # ------------------------------------------------------------------

    def _call_ai(self, prompt: str, gemini_api_key: str) -> str:
        """Call Gemini AI for Portuguese grammar analysis. Lazy imports required."""
        # LAZY IMPORT — required for unittest.mock.patch() to work and to
        # prevent cross-test contamination during analyzer auto-discovery.
        from streamlit_app.shared_utils import (
            get_gemini_api,
            get_gemini_fallback_model,
            get_gemini_model,
        )

        max_retries = 3
        base_delay = 1.0

        for attempt in range(max_retries):
            try:
                api = get_gemini_api()
                api.configure(api_key=gemini_api_key)

                # Try primary model
                try:
                    response = api.generate_content(
                        model=get_gemini_model(),
                        contents=prompt,
                        config={"max_output_tokens": 20000, "temperature": 0.1},
                    )
                    return response.text.strip()

                except Exception as primary_error:
                    logger.warning(
                        f"Primary model failed (attempt {attempt+1}): "
                        f"{str(primary_error)[:200]}"
                    )
                    # Fall back to preview model
                    try:
                        response = api.generate_content(
                            model=get_gemini_fallback_model(),
                            contents=prompt,
                            config={"max_output_tokens": 20000, "temperature": 0.1},
                        )
                        return response.text.strip()
                    except Exception as fallback_error:
                        logger.warning(
                            f"Fallback model also failed (attempt {attempt+1}): "
                            f"{str(fallback_error)[:200]}"
                        )
                        if attempt < max_retries - 1:
                            time.sleep(base_delay * (2 ** attempt))
                        else:
                            raise fallback_error

            except Exception as exc:
                logger.error(
                    f"All models failed on attempt {attempt+1}: {str(exc)[:200]}"
                )
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                else:
                    return '{"error": "AI service unavailable", "sentence": "error"}'

        return '{"error": "AI service unavailable", "sentence": "error"}'

    # ------------------------------------------------------------------
    # Difficulty / complexity resolution
    # ------------------------------------------------------------------

    def _resolve_complexity(self, requested: str) -> str:
        """
        Resolve the effective complexity level.

        Per CLAUDE.md: never hardcode 'intermediate'. Read st.session_state
        difficulty when no explicit complexity was provided. Wrapped in
        try/except so the analyzer works outside Streamlit (tests, scripts).
        """
        if requested and requested in self.supported_levels:
            return requested
        try:
            import streamlit as st  # type: ignore
            session_difficulty = st.session_state.get("difficulty")
            if session_difficulty in self.supported_levels:
                return session_difficulty
        except Exception:
            pass
        return "intermediate"

    # ------------------------------------------------------------------
    # HTML output generation
    # ------------------------------------------------------------------

    def _generate_html_output(
        self,
        parsed_data: Dict[str, Any],
        sentence: str,
        complexity: str,
    ) -> str:
        """
        Generate HTML with inline color styling for Anki display.
        Portuguese is LTR alphabetic with spaces — straightforward
        word-by-word coloring; clitic-verb forms are rendered word by word.
        """
        explanations = parsed_data.get("word_explanations", []) or []
        color_scheme = self.get_color_scheme(complexity)

        if not explanations:
            return sentence

        parts: List[str] = []
        for exp in explanations:
            if isinstance(exp, (list, tuple)) and len(exp) >= 3:
                word = str(exp[0])
                role = str(exp[1])
                color = str(exp[2]) or color_scheme.get(role, color_scheme.get("other", "#AAAAAA"))
            elif isinstance(exp, dict):
                word = str(exp.get("word", ""))
                role = str(exp.get("grammatical_role") or exp.get("role") or "other")
                color = (
                    exp.get("color")
                    or color_scheme.get(role, color_scheme.get("other", "#AAAAAA"))
                )
            else:
                continue
            if not word:
                continue
            # Escape any literal braces to be Anki/template-safe
            safe = word.replace("{", "{{").replace("}", "}}")
            parts.append(
                f'<span style="color: {color}; font-weight: bold;">{safe}</span>'
            )

        return " ".join(parts)

    def _map_grammatical_role_to_category(self, role: str) -> str:
        """
        Map a Portuguese role label to a broad category (legacy callers).
        NOTE: grammar_processor._convert_analyzer_output_to_explanations
        reads the role and color directly from word_explanations and does
        NOT call this method — so Portuguese-specific roles preserve their
        distinct colors. This helper is purely for legacy compatibility.
        """
        mapping = {
            "noun": "noun",
            "verb": "verb",
            "adjective": "adjective",
            "adverb": "adverb",
            "pronoun": "pronoun",
            "personal_pronoun": "pronoun",
            "possessive_pronoun": "pronoun",
            "demonstrative_pronoun": "pronoun",
            "reflexive_pronoun": "pronoun",
            "relative_pronoun": "pronoun",
            "indefinite_pronoun": "pronoun",
            "interrogative_pronoun": "pronoun",
            "preposition": "preposition",
            "conjunction": "conjunction",
            "subordinating_conjunction": "conjunction",
            "interjection": "interjection",
            "article": "article",
            "definite_article": "article",
            "indefinite_article": "article",
            "numeral": "numeral",
            "auxiliary_verb": "auxiliary_verb",
            "modal_verb": "modal_verb",
            "pronominal_verb": "verb",
            # Portuguese-specific roles preserve their identity
            "copula": "copula",
            "contraction": "contraction",
            "personal_infinitive": "personal_infinitive",
            "mesoclitic": "mesoclitic",
            "clitic_pronoun": "clitic_pronoun",
            "gerund": "gerund",
            "past_participle": "past_participle",
            "subjunctive_marker": "subjunctive_marker",
            "conditional": "conditional",
            "debitive": "debitive",
            "particle": "particle",
            "other": "other",
        }
        return mapping.get(role, "other")
