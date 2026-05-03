# languages/english/tests/test_en_analyzer.py
"""
Integration-level tests for EnAnalyzer.
AI calls are mocked — no real API key required.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.english.en_analyzer import EnAnalyzer
from streamlit_app.language_analyzers.base_analyzer import GrammarAnalysis
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
)

FAKE_KEY = "fake-api-key"


def _mock_call_ai(response_text):
    """Patch EnAnalyzer._call_ai to return a fixed string."""
    mock = MagicMock(return_value=response_text)
    return patch.object(EnAnalyzer, "_call_ai", mock)


class TestEnAnalyzerInit:
    def test_instantiation(self):
        analyzer = EnAnalyzer()
        assert analyzer is not None
        assert analyzer.LANGUAGE_CODE == "en"

    def test_language_code(self):
        analyzer = EnAnalyzer()
        assert analyzer.language_code == "en"

    def test_color_scheme_all_levels(self):
        analyzer = EnAnalyzer()
        for level in ("beginner", "intermediate", "advanced"):
            scheme = analyzer.get_color_scheme(level)
            assert isinstance(scheme, dict)
            assert len(scheme) > 5

    def test_get_grammar_prompt(self):
        analyzer = EnAnalyzer()
        prompt = analyzer.get_grammar_prompt("beginner", "The cat eats fish.", "eats")
        assert "The cat eats fish." in prompt
        assert len(prompt) > 100


class TestEnAnalyzerSingle:
    def test_analyze_grammar_beginner(self):
        analyzer = EnAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "The cat eats fish.", "eats", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert result.language_code == "en"
        assert result.complexity_level == "beginner"
        assert len(result.word_explanations) > 0

    def test_analyze_grammar_intermediate(self):
        analyzer = EnAnalyzer()
        with _mock_call_ai(SAMPLE_INTERMEDIATE_RESPONSE):
            result = analyzer.analyze_grammar(
                "I want to run quickly.", "run", "intermediate", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        # The 'to' should be tagged as infinitive_marker (or particle)
        roles = [w[1] for w in result.word_explanations]
        assert any(r in ("infinitive_marker", "particle") for r in roles), (
            f"Expected infinitive_marker or particle for 'to', got roles: {roles}"
        )

    def test_analyze_grammar_advanced(self):
        analyzer = EnAnalyzer()
        with _mock_call_ai(SAMPLE_ADVANCED_RESPONSE):
            result = analyzer.analyze_grammar(
                "The book that she read was interesting.",
                "book", "advanced", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        roles = [w[1] for w in result.word_explanations]
        assert "relative_pronoun" in roles, (
            f"Expected relative_pronoun for 'that', got roles: {roles}"
        )

    def test_confidence_score_range(self):
        analyzer = EnAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "The cat eats fish.", "eats", "beginner", FAKE_KEY
            )
        assert 0.0 <= result.confidence_score <= 1.0

    def test_html_output_generated(self):
        analyzer = EnAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "The cat eats fish.", "eats", "beginner", FAKE_KEY
            )
        assert result.html_output is not None
        assert len(result.html_output) > 0
        assert "<span" in result.html_output

    def test_fallback_on_api_error(self):
        analyzer = EnAnalyzer()
        with patch.object(EnAnalyzer, "_call_ai", side_effect=Exception("API down")):
            result = analyzer.analyze_grammar(
                "The cat eats fish.", "eats", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        # Fallback should still produce word_explanations
        assert len(result.word_explanations) > 0


class TestEnAnalyzerBatch:
    def test_batch_analyze_beginner(self):
        analyzer = EnAnalyzer()
        sentences = [
            "The cat eats fish.",
            "She reads a book.",
            "They play outside.",
        ]
        batch_response = f"[{SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_BEGINNER_RESPONSE}]"
        with _mock_call_ai(batch_response):
            results = analyzer.batch_analyze_grammar(
                sentences, "cat", "beginner", FAKE_KEY
            )
        assert len(results) == 3
        for r in results:
            assert isinstance(r, GrammarAnalysis)

    def test_batch_analyze_returns_list_of_grammar_analysis(self):
        analyzer = EnAnalyzer()
        sentences = ["The cat eats fish.", "She reads a book."]
        batch_response = f"[{SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_BEGINNER_RESPONSE}]"
        with _mock_call_ai(batch_response):
            results = analyzer.batch_analyze_grammar(
                sentences, "eats", "intermediate", FAKE_KEY
            )
        for r in results:
            assert isinstance(r, GrammarAnalysis)
            assert r.language_code == "en"

    def test_batch_fallback_on_error(self):
        analyzer = EnAnalyzer()
        sentences = ["The cat eats fish.", "She reads a book."]
        with patch.object(EnAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                sentences, "eats", "beginner", FAKE_KEY
            )
        assert len(results) == 2
        for r in results:
            assert isinstance(r, GrammarAnalysis)
            assert len(r.word_explanations) > 0

    def test_batch_analyze_all_complexity_levels(self):
        """Ensure all 3 complexity levels work in batch mode."""
        analyzer = EnAnalyzer()
        sentences_b = ["The cat eats fish.", "She reads a book."]
        sentences_i = [
            "I want to run quickly.",
            "She is going to the park.",
        ]
        sentences_a = [
            "The book that she read was interesting.",
            "He said that the problem had been solved.",
        ]
        for complexity, sentences in [
            ("beginner", sentences_b),
            ("intermediate", sentences_i),
            ("advanced", sentences_a),
        ]:
            batch_resp = "[" + ", ".join([SAMPLE_BEGINNER_RESPONSE] * len(sentences)) + "]"
            with _mock_call_ai(batch_resp):
                results = analyzer.batch_analyze_grammar(
                    sentences, "cat", complexity, FAKE_KEY
                )
            assert len(results) == len(sentences), f"Failed at {complexity}"
            for r in results:
                assert isinstance(r, GrammarAnalysis)
                assert r.complexity_level == complexity


class TestEnAnalyzerValidate:
    def test_validate_analysis_returns_float(self):
        analyzer = EnAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "The cat eats fish.", "eats", "beginner", FAKE_KEY
            )
        score = analyzer.validate_analysis(
            {"word_explanations": result.word_explanations,
             "overall_structure": "SVO"},
            "The cat eats fish."
        )
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestEnAnalyzerCrashRegression:
    """Regression tests for the NoneType .strip() crash + shallow-fallback bug.

    The original failure mode: Gemini returned a 200 OK response with
    `.text = None` (safety filter or token-limit hit), `_call_ai` called
    `response.text.strip()` raising AttributeError, which propagated up to
    `batch_analyze_grammar` and triggered a per-word rule-based fallback
    whose templates could produce single-line stubs.

    These tests verify both layers:
      1. _extract_response_text never raises AttributeError — only a
         RuntimeError that the existing retry layer can handle.
      2. When the rule-based fallback IS reached, every per-word explanation
         is a multi-clause sentence (>30 chars) — never a stub.
    """

    def test_extract_response_text_handles_none(self):
        """A response object with .text = None must raise RuntimeError, not AttributeError."""
        response = MagicMock()
        response.text = None
        with pytest.raises(RuntimeError, match="empty .text"):
            EnAnalyzer._extract_response_text(response)

    def test_extract_response_text_handles_missing_attr(self):
        """A response object with no .text attribute at all must raise RuntimeError."""

        class Bare:
            pass

        with pytest.raises(RuntimeError, match="empty .text"):
            EnAnalyzer._extract_response_text(Bare())

    def test_extract_response_text_handles_empty_string(self):
        """A response with .text = '' or whitespace must raise RuntimeError."""
        response = MagicMock()
        response.text = "   \n  "
        with pytest.raises(RuntimeError, match="empty .text"):
            EnAnalyzer._extract_response_text(response)

    def test_extract_response_text_returns_stripped(self):
        """A normal response is stripped and returned."""
        response = MagicMock()
        response.text = '  {"ok": 1}\n'
        assert EnAnalyzer._extract_response_text(response) == '{"ok": 1}'

    def test_batch_fallback_explanations_are_rich(self):
        """When the AI path fails, every fallback explanation must be a full sentence.

        The bug produced stubs like "The (article): The" — the fix produces
        multi-clause explanations of >30 chars that mention the word's role
        and at least one morphological feature.
        """
        analyzer = EnAnalyzer()
        sentence = "The quick brown fox jumps over the lazy dog."
        with patch.object(EnAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                [sentence], "fox", "beginner", FAKE_KEY
            )
        assert len(results) == 1
        explanations = results[0].word_explanations
        assert len(explanations) > 0

        for word, role, color, meaning in explanations:
            # No stubs — explanation body (after the "{word} ({role}):" prefix)
            # must be a real sentence.
            prefix = f"{word} ({role}):".lower()
            body = meaning.lower()
            if body.startswith(prefix):
                body = body[len(prefix):].strip()
            assert len(body) > 30, (
                f"Stub explanation for '{word}' ({role}): meaning={meaning!r}"
            )
            # The body must NOT just repeat the word.
            assert body != word.lower(), (
                f"Explanation for '{word}' just repeats the word: {meaning!r}"
            )

    def test_batch_fallback_does_not_misclassify_pronoun_case(self):
        """I/her/him must be tagged as personal_pronoun with correct cases, not as noun.

        English-specific equivalent of the Latvian adjective-misclassification test:
        pronoun case survival is the strongest inflectional remnant in English,
        and the fallback must honour it.
        """
        analyzer = EnAnalyzer()
        sentence = "I see her with him."
        with patch.object(EnAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                [sentence], "see", "intermediate", FAKE_KEY
            )
        explanations = {w[0].lower().strip(".,!?"): (w[1], w[3]) for w in results[0].word_explanations}

        # 'I' must be tagged as a pronoun, not a noun.
        assert "i" in explanations, "Token 'I' not found in word_explanations"
        role_i, meaning_i = explanations["i"]
        assert role_i in ("personal_pronoun", "pronoun"), (
            f"'I' was tagged '{role_i}' — must be personal_pronoun or pronoun, not noun."
        )
        # Check the meaning mentions nominative case for 'I'
        assert "nominative" in meaning_i.lower(), (
            f"'I' meaning should mention nominative case; got: {meaning_i!r}"
        )

        # 'her' in this position (after verb, before preposition) must be pronoun.
        assert "her" in explanations, "Token 'her' not found in word_explanations"
        role_her, _ = explanations["her"]
        assert role_her in ("personal_pronoun", "pronoun", "possessive_determiner"), (
            f"'her' was tagged '{role_her}' — must be a pronoun form, not noun."
        )

        # 'him' must be tagged as a pronoun (accusative), not a noun.
        assert "him" in explanations, "Token 'him' not found in word_explanations"
        role_him, meaning_him = explanations["him"]
        assert role_him in ("personal_pronoun", "pronoun"), (
            f"'him' was tagged '{role_him}' — must be personal_pronoun or pronoun."
        )
        assert "accusative" in meaning_him.lower(), (
            f"'him' meaning should mention accusative case; got: {meaning_him!r}"
        )

    def test_batch_fallback_quality_regression(self):
        """Run the validator against the fallback output and assert quality_score > 0.7."""
        analyzer = EnAnalyzer()
        sentence = "The quick brown fox jumps over the lazy dog."
        with patch.object(EnAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                [sentence], "fox", "beginner", FAKE_KEY
            )

        # Build a result dict shaped like what the validator expects.
        word_explanations_dicts = []
        for word, role, color, meaning in results[0].word_explanations:
            # Strip "{word} ({role}):" prefix to recover individual_meaning
            prefix = f"{word} ({role}):"
            body = meaning[len(prefix):].strip() if meaning.startswith(prefix) else meaning
            word_explanations_dicts.append({
                "word": word,
                "role": role,
                "color": color,
                "meaning": meaning,
                "individual_meaning": body,
            })
        quality = analyzer.validator.validate_explanation_quality(
            {"word_explanations": word_explanations_dicts}
        )
        assert quality["quality_score"] > 0.7, (
            f"Fallback explanations failed quality gate: {quality}"
        )
        assert quality["stub_count"] == 0, (
            f"Fallback produced stub explanations: {quality}"
        )
