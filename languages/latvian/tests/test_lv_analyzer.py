# languages/latvian/tests/test_lv_analyzer.py
"""
Integration-level tests for LvAnalyzer.
AI calls are mocked — no real API key required.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.latvian.lv_analyzer import LvAnalyzer
from streamlit_app.language_analyzers.base_analyzer import GrammarAnalysis
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
)

FAKE_KEY = "fake-api-key"


def _mock_call_ai(response_text):
    """Patch LvAnalyzer._call_ai to return a fixed string."""
    mock = MagicMock(return_value=response_text)
    return patch.object(LvAnalyzer, "_call_ai", mock)


class TestLvAnalyzerInit:
    def test_instantiation(self):
        analyzer = LvAnalyzer()
        assert analyzer is not None
        assert analyzer.LANGUAGE_CODE == "lv"

    def test_language_code(self):
        analyzer = LvAnalyzer()
        assert analyzer.language_code == "lv"

    def test_color_scheme_all_levels(self):
        analyzer = LvAnalyzer()
        for level in ("beginner", "intermediate", "advanced"):
            scheme = analyzer.get_color_scheme(level)
            assert isinstance(scheme, dict)
            assert len(scheme) > 5

    def test_get_grammar_prompt(self):
        analyzer = LvAnalyzer()
        prompt = analyzer.get_grammar_prompt("beginner", "Es runāju.", "runāju")
        assert "Es runāju." in prompt
        assert len(prompt) > 100


class TestLvAnalyzerSingle:
    def test_analyze_grammar_beginner(self):
        analyzer = LvAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Es runāju latviski.", "runāju", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert result.language_code == "lv"
        assert result.complexity_level == "beginner"
        assert len(result.word_explanations) > 0

    def test_analyze_grammar_intermediate(self):
        analyzer = LvAnalyzer()
        with _mock_call_ai(SAMPLE_INTERMEDIATE_RESPONSE):
            result = analyzer.analyze_grammar(
                "Man jāmācās latviešu valoda.", "jāmācās", "intermediate", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        roles = [w[1] for w in result.word_explanations]
        assert "debitive" in roles

    def test_analyze_grammar_advanced(self):
        analyzer = LvAnalyzer()
        with _mock_call_ai(SAMPLE_ADVANCED_RESPONSE):
            result = analyzer.analyze_grammar(
                "Uzrakstītā vēstule tika nosūtīta vakar.",
                "vēstule", "advanced", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        roles = [w[1] for w in result.word_explanations]
        assert "participle" in roles

    def test_confidence_score_range(self):
        analyzer = LvAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Es runāju latviski.", "runāju", "beginner", FAKE_KEY
            )
        assert 0.0 <= result.confidence_score <= 1.0

    def test_html_output_generated(self):
        analyzer = LvAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Es runāju latviski.", "runāju", "beginner", FAKE_KEY
            )
        assert result.html_output is not None
        assert len(result.html_output) > 0
        assert "<span" in result.html_output

    def test_fallback_on_api_error(self):
        analyzer = LvAnalyzer()
        with patch.object(LvAnalyzer, "_call_ai", side_effect=Exception("API down")):
            result = analyzer.analyze_grammar(
                "Es runāju.", "runāju", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        # Fallback should still produce word_explanations
        assert len(result.word_explanations) > 0


class TestLvAnalyzerBatch:
    def test_batch_analyze_beginner(self):
        analyzer = LvAnalyzer()
        sentences = [
            "Es runāju latviski.",
            "Māja ir skaista.",
            "Viņš iet uz skolu.",
        ]
        batch_response = f"[{SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_BEGINNER_RESPONSE}]"
        with _mock_call_ai(batch_response):
            results = analyzer.batch_analyze_grammar(
                sentences, "māja", "beginner", FAKE_KEY
            )
        assert len(results) == 3
        for r in results:
            assert isinstance(r, GrammarAnalysis)

    def test_batch_analyze_returns_list_of_grammar_analysis(self):
        analyzer = LvAnalyzer()
        sentences = ["Es runāju.", "Viņš iet."]
        batch_response = f"[{SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_BEGINNER_RESPONSE}]"
        with _mock_call_ai(batch_response):
            results = analyzer.batch_analyze_grammar(
                sentences, "runāju", "intermediate", FAKE_KEY
            )
        for r in results:
            assert isinstance(r, GrammarAnalysis)
            assert r.language_code == "lv"

    def test_batch_fallback_on_error(self):
        analyzer = LvAnalyzer()
        sentences = ["Es runāju.", "Viņš iet."]
        with patch.object(LvAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                sentences, "runāju", "beginner", FAKE_KEY
            )
        assert len(results) == 2
        for r in results:
            assert isinstance(r, GrammarAnalysis)
            assert len(r.word_explanations) > 0

    def test_batch_analyze_all_complexity_levels(self):
        """Ensure all 3 complexity levels work in batch mode."""
        analyzer = LvAnalyzer()
        sentences_b = ["Es runāju.", "Māja ir liela."]
        sentences_i = [
            "Man jāmācās latviešu valoda.",
            "Bērniem patīk spēlēties parkā.",
        ]
        sentences_a = [
            "Uzrakstītā vēstule tika nosūtīta vakar.",
            "Strādājošais skolotājs dzīvo kaimiņos.",
        ]
        for complexity, sentences in [
            ("beginner", sentences_b),
            ("intermediate", sentences_i),
            ("advanced", sentences_a),
        ]:
            batch_resp = "[" + ", ".join([SAMPLE_BEGINNER_RESPONSE] * len(sentences)) + "]"
            with _mock_call_ai(batch_resp):
                results = analyzer.batch_analyze_grammar(
                    sentences, "māja", complexity, FAKE_KEY
                )
            assert len(results) == len(sentences), f"Failed at {complexity}"
            for r in results:
                assert isinstance(r, GrammarAnalysis)
                assert r.complexity_level == complexity


class TestLvAnalyzerValidate:
    def test_validate_analysis_returns_float(self):
        analyzer = LvAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Es runāju latviski.", "runāju", "beginner", FAKE_KEY
            )
        score = analyzer.validate_analysis(
            {"word_explanations": result.word_explanations,
             "overall_structure": "SVO"},
            "Es runāju latviski."
        )
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
