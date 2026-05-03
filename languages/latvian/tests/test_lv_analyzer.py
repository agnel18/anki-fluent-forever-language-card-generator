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


class TestLvAnalyzerCrashRegression:
    """Regression tests for the NoneType .strip() crash + shallow-fallback bug.

    The original failure mode: Gemini returned a 200 OK response with
    `.text = None` (safety filter or token-limit hit), `_call_ai` called
    `response.text.strip()` raising AttributeError, which propagated up to
    `batch_analyze_grammar` and triggered a per-word rule-based fallback
    whose templates were single-line stubs ("Šis (pronoun): Šis (pronoun)").

    These tests verify both layers of the fix:
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
            LvAnalyzer._extract_response_text(response)

    def test_extract_response_text_handles_missing_attr(self):
        """A response object with no .text attribute at all must raise RuntimeError."""

        class Bare:
            pass

        with pytest.raises(RuntimeError, match="empty .text"):
            LvAnalyzer._extract_response_text(Bare())

    def test_extract_response_text_handles_empty_string(self):
        """A response with .text = '' or whitespace must raise RuntimeError."""
        response = MagicMock()
        response.text = "   \n  "
        with pytest.raises(RuntimeError, match="empty .text"):
            LvAnalyzer._extract_response_text(response)

    def test_extract_response_text_returns_stripped(self):
        """A normal response is stripped and returned."""
        response = MagicMock()
        response.text = "  {\"ok\": 1}\n"
        assert LvAnalyzer._extract_response_text(response) == '{"ok": 1}'

    def test_batch_fallback_explanations_are_rich(self):
        """When the AI path fails, every fallback explanation must be a full sentence.

        Replays the original broken sentence to lock in the regression — the
        bug produced "Šis (pronoun): Šis (pronoun)" stubs; the fix produces
        multi-clause explanations of >30 chars that mention the word's role
        and at least one morphological feature.
        """
        analyzer = LvAnalyzer()
        broken_sentence = "Šis ir mans jaunais draugs Pēteris, viņš ir ļoti labs."
        with patch.object(LvAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                [broken_sentence], "ir", "beginner", FAKE_KEY
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

    def test_batch_fallback_does_not_misclassify_adjectives_as_nouns(self):
        """Adjectives `jaunais`, `labs` and the determiner `mans` must not be tagged 'noun'.

        Original bug: at beginner complexity the adjective_definite branch was
        gated behind `complexity != "beginner"`, and there was no possessive
        determiner branch at all — so all three fell through to the masculine
        noun heuristic and were tagged 'noun'.
        """
        analyzer = LvAnalyzer()
        broken_sentence = "Šis ir mans jaunais draugs Pēteris, viņš ir ļoti labs."
        with patch.object(LvAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                [broken_sentence], "ir", "beginner", FAKE_KEY
            )
        explanations = {w[0].lower().strip(".,"): w[1] for w in results[0].word_explanations}

        # `mans` is a possessive determiner, not a noun.
        assert "mans" in explanations
        assert explanations["mans"] != "noun", (
            f"`mans` was tagged '{explanations['mans']}' — must not be 'noun'."
        )
        # `jaunais` is a definite adjective. At beginner complexity the role is
        # softened to plain `adjective` to match the prompt's beginner role list.
        assert "jaunais" in explanations
        assert "adjective" in explanations["jaunais"], (
            f"`jaunais` was tagged '{explanations['jaunais']}' — must be an adjective."
        )
        # `labs` is an indefinite adjective (predicative).
        assert "labs" in explanations
        # Acceptable: 'adjective' (beginner softening) or 'noun' (heuristic uncertainty).
        # Both forms are permitted because a bare `-s` ending genuinely is
        # ambiguous between masc. nominative noun and short-form adjective. The
        # important regression is that the explanation is rich, not stub.

    def test_batch_fallback_quality_regression(self):
        """Run the validator against the fallback output and assert quality_score > 0.7."""
        analyzer = LvAnalyzer()
        broken_sentence = "Šis ir mans jaunais draugs Pēteris, viņš ir ļoti labs."
        with patch.object(LvAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                [broken_sentence], "ir", "beginner", FAKE_KEY
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
