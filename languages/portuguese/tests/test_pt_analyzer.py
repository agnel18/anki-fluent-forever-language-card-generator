# languages/portuguese/tests/test_pt_analyzer.py
"""
Unit tests for PtAnalyzer facade.
AI calls are mocked — no real API key required.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.portuguese.pt_analyzer import PtAnalyzer
from streamlit_app.language_analyzers.base_analyzer import GrammarAnalysis
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE_2,
    SAMPLE_SER_RESPONSE,
    SAMPLE_ESTAR_RESPONSE,
    SAMPLE_CONTRACTION_RESPONSE,
)

FAKE_KEY = "fake-api-key-unit"


def _mock_call_ai(response_text):
    """Patch PtAnalyzer._call_ai to return a fixed string."""
    return patch.object(PtAnalyzer, "_call_ai", return_value=response_text)


class TestPtAnalyzerInit:
    def test_instantiation(self):
        analyzer = PtAnalyzer()
        assert analyzer is not None

    def test_language_code(self):
        analyzer = PtAnalyzer()
        assert analyzer.LANGUAGE_CODE == "pt"
        assert analyzer.language_code == "pt"

    def test_supported_complexity_levels(self):
        """Behavior 1: all three tiers must be supported."""
        analyzer = PtAnalyzer()
        for level in ("beginner", "intermediate", "advanced"):
            assert analyzer.is_complexity_supported(level), (
                f"Expected '{level}' to be supported"
            )

    def test_unsupported_level_returns_false(self):
        analyzer = PtAnalyzer()
        assert not analyzer.is_complexity_supported("ultra_advanced")

    def test_color_scheme_all_levels(self):
        """Behavior 1: get_color_scheme returns non-empty dict for all tiers."""
        analyzer = PtAnalyzer()
        for level in ("beginner", "intermediate", "advanced"):
            scheme = analyzer.get_color_scheme(level)
            assert isinstance(scheme, dict)
            assert len(scheme) > 5

    def test_get_supported_features(self):
        analyzer = PtAnalyzer()
        features = analyzer.get_supported_features()
        assert isinstance(features, list)

    def test_get_grammar_prompt(self):
        analyzer = PtAnalyzer()
        prompt = analyzer.get_grammar_prompt("beginner", "O gato dorme.", "dorme")
        assert "O gato dorme." in prompt
        assert len(prompt) > 100


class TestPtAnalyzerSingleAnalysis:
    def test_analyze_grammar_beginner(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "O gato bebe leite.", "gato", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert result.language_code == "pt"
        assert result.complexity_level == "beginner"
        assert len(result.word_explanations) > 0

    def test_analyze_grammar_intermediate(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_INTERMEDIATE_RESPONSE):
            result = analyzer.analyze_grammar(
                "Ela vai ao mercado comprar pão.",
                "mercado", "intermediate", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        roles = [w[1] for w in result.word_explanations]
        assert "contraction" in roles

    def test_analyze_grammar_advanced(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_ADVANCED_RESPONSE):
            result = analyzer.analyze_grammar(
                "Disse-me a verdade que precisava de saber.",
                "verdade", "advanced", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        roles = [w[1] for w in result.word_explanations]
        assert "clitic_pronoun" in roles or "personal_pronoun" in roles

    def test_confidence_score_range(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "O gato bebe leite.", "gato", "beginner", FAKE_KEY
            )
        assert 0.0 <= result.confidence_score <= 1.0

    def test_html_output_generated(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "O gato bebe leite.", "gato", "beginner", FAKE_KEY
            )
        assert result.html_output is not None
        assert len(result.html_output) > 0
        assert "<span" in result.html_output

    def test_fallback_on_api_error(self):
        analyzer = PtAnalyzer()
        with patch.object(PtAnalyzer, "_call_ai", side_effect=Exception("API down")):
            result = analyzer.analyze_grammar(
                "O gato dorme.", "gato", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert len(result.word_explanations) > 0

    # Behavior 2: ser vs estar copula
    def test_ser_copula_tagged_in_result(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_SER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Ela é triste.", "é", "intermediate", FAKE_KEY
            )
        roles = [w[1] for w in result.word_explanations]
        assert "copula" in roles

    def test_estar_copula_tagged_in_result(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_ESTAR_RESPONSE):
            result = analyzer.analyze_grammar(
                "Ela está triste.", "está", "intermediate", FAKE_KEY
            )
        roles = [w[1] for w in result.word_explanations]
        assert "copula" in roles

    # Behavior 3: contraction handling
    def test_contraction_role_in_result(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_CONTRACTION_RESPONSE):
            result = analyzer.analyze_grammar(
                "Eu vou ao mercado.", "mercado", "intermediate", FAKE_KEY
            )
        roles = [w[1] for w in result.word_explanations]
        assert "contraction" in roles


class TestPtAnalyzerBatchAnalysis:
    def test_batch_analyze_returns_list(self):
        analyzer = PtAnalyzer()
        sentences = ["O gato dorme.", "Ela come pão.", "Eu falo português."]
        batch_response = (
            f"[{SAMPLE_BEGINNER_RESPONSE}, "
            f"{SAMPLE_BEGINNER_RESPONSE}, "
            f"{SAMPLE_BEGINNER_RESPONSE}]"
        )
        with _mock_call_ai(batch_response):
            results = analyzer.batch_analyze_grammar(
                sentences, "gato", "beginner", FAKE_KEY
            )
        assert len(results) == 3
        for r in results:
            assert isinstance(r, GrammarAnalysis)

    def test_batch_language_code(self):
        analyzer = PtAnalyzer()
        sentences = ["O gato dorme.", "Ela come pão."]
        batch_response = f"[{SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_BEGINNER_RESPONSE}]"
        with _mock_call_ai(batch_response):
            results = analyzer.batch_analyze_grammar(
                sentences, "gato", "beginner", FAKE_KEY
            )
        for r in results:
            assert r.language_code == "pt"

    def test_batch_fallback_on_error(self):
        analyzer = PtAnalyzer()
        sentences = ["O gato dorme.", "Ela come pão."]
        with patch.object(PtAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                sentences, "gato", "beginner", FAKE_KEY
            )
        assert len(results) == 2
        for r in results:
            assert isinstance(r, GrammarAnalysis)
            assert len(r.word_explanations) > 0

    def test_batch_all_complexity_levels(self):
        """Behavior 1: all three complexity levels work in batch mode."""
        analyzer = PtAnalyzer()
        sentences = ["O gato dorme.", "Ela come pão."]
        for complexity, mock_resp in [
            ("beginner", SAMPLE_BEGINNER_RESPONSE),
            ("intermediate", SAMPLE_INTERMEDIATE_RESPONSE),
            ("advanced", SAMPLE_ADVANCED_RESPONSE),
        ]:
            batch_resp = f"[{mock_resp}, {mock_resp}]"
            with _mock_call_ai(batch_resp):
                results = analyzer.batch_analyze_grammar(
                    sentences, "gato", complexity, FAKE_KEY
                )
            assert len(results) == 2, f"Failed at complexity={complexity}"
            for r in results:
                assert isinstance(r, GrammarAnalysis)
                assert r.complexity_level == complexity


class TestPtAnalyzerValidation:
    def test_validate_analysis_returns_float(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "O gato bebe leite.", "gato", "beginner", FAKE_KEY
            )
        score = analyzer.validate_analysis(
            {
                "word_explanations": result.word_explanations,
                "overall_structure": "SVO",
            },
            "O gato bebe leite.",
        )
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_validate_color_consistency(self):
        analyzer = PtAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "O gato bebe leite.", "gato", "beginner", FAKE_KEY
            )
        ok, msg = analyzer.validate_color_consistency(
            result.html_output, result.word_explanations
        )
        assert isinstance(ok, bool)
        assert isinstance(msg, str)


class TestPtAnalyzerSentenceGenerationPrompt:
    def test_sentence_generation_prompt_returns_string(self):
        analyzer = PtAnalyzer()
        prompt = analyzer.get_sentence_generation_prompt(
            word="casa",
            language="Portuguese",
            num_sentences=3,
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 100
        assert "casa" in prompt

    def test_sentence_generation_prompt_none_on_no_word(self):
        """With an empty word, the analyzer may return None or a minimal prompt."""
        analyzer = PtAnalyzer()
        prompt = analyzer.get_sentence_generation_prompt(
            word="",
            language="Portuguese",
            num_sentences=3,
        )
        # May return None or a string — just ensure no crash
        assert prompt is None or isinstance(prompt, str)

    def test_get_batch_grammar_prompt_returns_string(self):
        analyzer = PtAnalyzer()
        sentences = ["O gato dorme.", "Ela come pão."]
        prompt = analyzer.get_batch_grammar_prompt(
            "intermediate", sentences, "gato"
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 100
