# languages/russian/tests/test_integration.py
"""
Integration tests for Russian analyzer — all components together.
AI calls are mocked — no real API key required.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.russian.ru_analyzer import RuAnalyzer
from streamlit_app.language_analyzers.base_analyzer import GrammarAnalysis
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
)

FAKE_KEY = "fake-api-key"


def _mock_call_ai(response_text):
    return patch.object(RuAnalyzer, "_call_ai", MagicMock(return_value=response_text))


class TestRuIntegration:
    """Full pipeline integration tests for the Russian analyzer.

    Each test mocks _call_ai and runs one sentence end-to-end through the
    complete pipeline: analyze_grammar → parse → validate → html_output.
    """

    def test_beginner_pipeline(self):
        """Beginner sentence: Я читаю книгу. — full pipeline."""
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert result.language_code == "ru"
        assert result.complexity_level == "beginner"
        assert len(result.word_explanations) > 0
        assert result.html_output is not None
        assert "<span" in result.html_output
        assert result.confidence_score >= 0.5

    def test_intermediate_pipeline(self):
        """Intermediate sentence: Мне нужно написать письмо. — full pipeline."""
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_INTERMEDIATE_RESPONSE):
            result = analyzer.analyze_grammar(
                "Мне нужно написать письмо.", "написать", "intermediate", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert result.complexity_level == "intermediate"
        assert len(result.word_explanations) > 0
        assert "<span" in result.html_output
        assert result.confidence_score >= 0.5

    def test_advanced_pipeline(self):
        """Advanced sentence: Книга, которую она читала, была интересной. — full pipeline."""
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_ADVANCED_RESPONSE):
            result = analyzer.analyze_grammar(
                "Книга, которую она читала, была интересной.",
                "которую", "advanced", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert result.complexity_level == "advanced"
        assert len(result.word_explanations) > 0
        assert "<span" in result.html_output
        assert result.confidence_score >= 0.5

    def test_pipeline_word_explanations_format(self):
        """word_explanations must be [word, role, color, meaning] 4-tuples."""
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        for item in result.word_explanations:
            assert len(item) == 4, f"Expected 4-tuple, got: {item}"
            word, role, color, meaning = item
            assert isinstance(word, str)
            assert isinstance(role, str)
            assert isinstance(color, str)
            assert isinstance(meaning, str)
            assert color.startswith("#"), f"Color should be hex, got: {color!r}"

    def test_pipeline_color_scheme_populated(self):
        """color_scheme must contain at least the basic POS roles."""
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        scheme = result.color_scheme
        assert "noun" in scheme
        assert "verb" in scheme
        assert "adjective" in scheme

    def test_pipeline_fallback_still_produces_output(self):
        """Full pipeline still produces output when AI fails."""
        analyzer = RuAnalyzer()
        with patch.object(RuAnalyzer, "_call_ai", side_effect=Exception("API down")):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert len(result.word_explanations) > 0
        # Fallback confidence is capped at 0.3
        assert result.confidence_score <= 0.3

    def test_batch_pipeline_all_three_levels(self):
        """Batch mode must work at all 3 complexity levels."""
        analyzer = RuAnalyzer()
        test_cases = [
            ("beginner",      ["Я читаю книгу.", "Она пишет письмо."], SAMPLE_BEGINNER_RESPONSE),
            ("intermediate",  ["Мне нужно написать письмо.", "Ему нравится читать."], SAMPLE_INTERMEDIATE_RESPONSE),
            ("advanced",      ["Книга, которую она читала, была интересной."], SAMPLE_ADVANCED_RESPONSE),
        ]
        for level, sentences, mock_response in test_cases:
            batch_resp = "[" + ", ".join([mock_response] * len(sentences)) + "]"
            with _mock_call_ai(batch_resp):
                results = analyzer.batch_analyze_grammar(
                    sentences, "книга", level, FAKE_KEY
                )
            assert len(results) == len(sentences), f"Wrong count at {level}"
            for r in results:
                assert isinstance(r, GrammarAnalysis)
                assert r.complexity_level == level
                assert "<span" in r.html_output or r.html_output  # Non-empty output

    def test_beginner_html_contains_cyrillic_words(self):
        """The HTML output for a Cyrillic sentence should contain Cyrillic characters."""
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        # At least some Cyrillic characters should survive into the HTML
        has_cyrillic = any(
            "Ѐ" <= c <= "ӿ" for c in result.html_output
        )
        assert has_cyrillic, (
            f"No Cyrillic in HTML output: {result.html_output[:200]!r}"
        )
