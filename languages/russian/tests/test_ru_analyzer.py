# languages/russian/tests/test_ru_analyzer.py
"""
Integration-level tests for RuAnalyzer.
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
    """Patch RuAnalyzer._call_ai to return a fixed string."""
    mock = MagicMock(return_value=response_text)
    return patch.object(RuAnalyzer, "_call_ai", mock)


class TestRuAnalyzerInit:
    def test_instantiation(self):
        analyzer = RuAnalyzer()
        assert analyzer is not None
        assert analyzer.LANGUAGE_CODE == "ru"

    def test_language_code(self):
        analyzer = RuAnalyzer()
        assert analyzer.language_code == "ru"

    def test_color_scheme_all_levels(self):
        analyzer = RuAnalyzer()
        for level in ("beginner", "intermediate", "advanced"):
            scheme = analyzer.get_color_scheme(level)
            assert isinstance(scheme, dict)
            assert len(scheme) > 5

    def test_get_grammar_prompt_contains_sentence(self):
        analyzer = RuAnalyzer()
        sentence = "Я читаю книгу."
        prompt = analyzer.get_grammar_prompt("beginner", sentence, "читаю")
        assert sentence in prompt
        assert len(prompt) > 100

    def test_get_grammar_prompt_cyrillic_sentence(self):
        analyzer = RuAnalyzer()
        sentence = "Мне нужно написать письмо."
        prompt = analyzer.get_grammar_prompt("intermediate", sentence, "написать")
        assert sentence in prompt

    def test_get_grammar_prompt_advanced(self):
        analyzer = RuAnalyzer()
        sentence = "Книга, которую она читала, была интересной."
        prompt = analyzer.get_grammar_prompt("advanced", sentence, "которую")
        assert sentence in prompt


class TestRuAnalyzerSingle:
    def test_analyze_grammar_beginner(self):
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert result.language_code == "ru"
        assert result.complexity_level == "beginner"
        assert len(result.word_explanations) > 0

    def test_analyze_grammar_beginner_nominative_pronoun(self):
        """At beginner level, Я should be a personal_pronoun with nominative in explanation."""
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        # Find the explanation for Я
        ya_meanings = [
            meaning for word, role, color, meaning in result.word_explanations
            if word == "Я"
        ]
        assert ya_meanings, "No explanation for 'Я' found"
        assert "nominative" in ya_meanings[0].lower(), (
            f"Expected 'nominative' in Я explanation, got: {ya_meanings[0]!r}"
        )

    def test_analyze_grammar_intermediate_dative(self):
        """At intermediate level, мне should be tagged with dative."""
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_INTERMEDIATE_RESPONSE):
            result = analyzer.analyze_grammar(
                "Мне нужно написать письмо.", "написать", "intermediate", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        # Find мне
        mne_meanings = [
            meaning for word, role, color, meaning in result.word_explanations
            if word == "Мне"
        ]
        assert mne_meanings, "No explanation for 'Мне' found"
        assert "dative" in mne_meanings[0].lower(), (
            f"Expected 'dative' in Мне explanation, got: {mne_meanings[0]!r}"
        )

    def test_analyze_grammar_advanced_relative_pronoun(self):
        """At advanced level, которую should be tagged as relative_pronoun."""
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_ADVANCED_RESPONSE):
            result = analyzer.analyze_grammar(
                "Книга, которую она читала, была интересной.",
                "которую", "advanced", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        roles = [w[1] for w in result.word_explanations]
        assert "relative_pronoun" in roles, (
            f"Expected 'relative_pronoun' in roles, got: {roles}"
        )

    def test_confidence_score_range(self):
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        assert 0.0 <= result.confidence_score <= 1.0

    def test_html_output_generated(self):
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        assert result.html_output is not None
        assert len(result.html_output) > 0
        assert "<span" in result.html_output

    def test_fallback_on_api_error(self):
        analyzer = RuAnalyzer()
        with patch.object(RuAnalyzer, "_call_ai", side_effect=Exception("API down")):
            result = analyzer.analyze_grammar(
                "Я читаю.", "читаю", "beginner", FAKE_KEY
            )
        assert isinstance(result, GrammarAnalysis)
        assert len(result.word_explanations) > 0


class TestRuAnalyzerBatch:
    def test_batch_analyze_beginner(self):
        analyzer = RuAnalyzer()
        sentences = [
            "Я читаю книгу.",
            "Она пишет письмо.",
            "Мы идём домой.",
        ]
        batch_response = (
            f"[{SAMPLE_BEGINNER_RESPONSE}, "
            f"{SAMPLE_BEGINNER_RESPONSE}, "
            f"{SAMPLE_BEGINNER_RESPONSE}]"
        )
        with _mock_call_ai(batch_response):
            results = analyzer.batch_analyze_grammar(
                sentences, "читаю", "beginner", FAKE_KEY
            )
        assert len(results) == 3
        for r in results:
            assert isinstance(r, GrammarAnalysis)

    def test_batch_analyze_returns_list_of_grammar_analysis(self):
        analyzer = RuAnalyzer()
        sentences = ["Я читаю книгу.", "Она пишет письмо."]
        batch_response = f"[{SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_BEGINNER_RESPONSE}]"
        with _mock_call_ai(batch_response):
            results = analyzer.batch_analyze_grammar(
                sentences, "читаю", "intermediate", FAKE_KEY
            )
        for r in results:
            assert isinstance(r, GrammarAnalysis)
            assert r.language_code == "ru"

    def test_batch_fallback_on_error(self):
        analyzer = RuAnalyzer()
        sentences = ["Я читаю.", "Она пишет."]
        with patch.object(RuAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                sentences, "читаю", "beginner", FAKE_KEY
            )
        assert len(results) == 2
        for r in results:
            assert isinstance(r, GrammarAnalysis)
            assert len(r.word_explanations) > 0

    def test_batch_analyze_all_complexity_levels(self):
        """Ensure all 3 complexity levels work in batch mode."""
        analyzer = RuAnalyzer()
        sentences_b = ["Я читаю книгу.", "Она пишет письмо."]
        sentences_i = [
            "Мне нужно написать письмо.",
            "Ему нравится читать книги.",
        ]
        sentences_a = [
            "Книга, которую она читала, была интересной.",
            "Человек, написавший эту книгу, жил в Москве.",
        ]
        for complexity, sentences in [
            ("beginner", sentences_b),
            ("intermediate", sentences_i),
            ("advanced", sentences_a),
        ]:
            batch_resp = "[" + ", ".join([SAMPLE_BEGINNER_RESPONSE] * len(sentences)) + "]"
            with _mock_call_ai(batch_resp):
                results = analyzer.batch_analyze_grammar(
                    sentences, "книга", complexity, FAKE_KEY
                )
            assert len(results) == len(sentences), f"Failed at {complexity}"
            for r in results:
                assert isinstance(r, GrammarAnalysis)
                assert r.complexity_level == complexity


class TestRuAnalyzerValidate:
    def test_validate_analysis_returns_float(self):
        analyzer = RuAnalyzer()
        with _mock_call_ai(SAMPLE_BEGINNER_RESPONSE):
            result = analyzer.analyze_grammar(
                "Я читаю книгу.", "читаю", "beginner", FAKE_KEY
            )
        score = analyzer.validate_analysis(
            {"word_explanations": result.word_explanations,
             "overall_structure": "SVO"},
            "Я читаю книгу."
        )
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestRuAnalyzerCrashRegression:
    """Regression tests for the NoneType .strip() crash + shallow-fallback bug.

    The original failure mode: Gemini returned a 200 OK response with
    `.text = None` (safety filter or token-limit hit), `_call_ai` called
    `response.text.strip()` raising AttributeError, which propagated up to
    `batch_analyze_grammar` and triggered a per-word rule-based fallback
    whose templates could produce single-line stubs.

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
            RuAnalyzer._extract_response_text(response)

    def test_extract_response_text_handles_missing_attr(self):
        """A response object with no .text attribute at all must raise RuntimeError."""

        class Bare:
            pass

        with pytest.raises(RuntimeError, match="empty .text"):
            RuAnalyzer._extract_response_text(Bare())

    def test_extract_response_text_handles_empty_string(self):
        """A response with .text = '' or whitespace must raise RuntimeError."""
        response = MagicMock()
        response.text = "   \n  "
        with pytest.raises(RuntimeError, match="empty .text"):
            RuAnalyzer._extract_response_text(response)

    def test_extract_response_text_returns_stripped(self):
        """A normal response is stripped and returned."""
        response = MagicMock()
        response.text = '  {"ok": 1}\n'
        assert RuAnalyzer._extract_response_text(response) == '{"ok": 1}'

    def test_batch_fallback_explanations_are_rich(self):
        """When the AI path fails, every fallback explanation must be a full sentence.

        Replays a Russian sentence to lock in the regression — the bug
        produces stubs like "Я (pronoun): Я (pronoun)"; the fix produces
        multi-clause explanations of >30 chars that mention the word's role
        and at least one morphological feature.
        """
        analyzer = RuAnalyzer()
        broken_sentence = "Я вижу его и говорю с ним."
        with patch.object(RuAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                [broken_sentence], "вижу", "beginner", FAKE_KEY
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
        """Russian 6-case pronoun paradigm must survive the fallback.

        Sentence: "Я вижу его и говорю с ним."
        (I see him and speak with him.)

        Expected fallback tagging:
          - Я  → personal_pronoun, nominative (subject)
          - его → personal_pronoun (genitive/accusative — direct object 3sg.m)
          - ним → personal_pronoun (instrumental — after preposition 'с')
        None of these should be tagged as 'noun'.
        """
        analyzer = RuAnalyzer()
        sentence = "Я вижу его и говорю с ним."
        with patch.object(RuAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                [sentence], "вижу", "intermediate", FAKE_KEY
            )
        explanations = {
            w[0].lower().strip(".,!?"): (w[1], w[3])
            for w in results[0].word_explanations
        }

        # Я must be personal_pronoun, not noun.
        assert "я" in explanations, "Token 'Я' not found in word_explanations"
        role_ya, meaning_ya = explanations["я"]
        assert role_ya in ("personal_pronoun", "pronoun"), (
            f"'Я' was tagged '{role_ya}' — must be personal_pronoun/pronoun, not noun."
        )
        assert "nominative" in meaning_ya.lower(), (
            f"'Я' meaning should mention nominative case; got: {meaning_ya!r}"
        )

        # его (direct object, 3sg.m genitive/accusative) must be pronoun.
        assert "его" in explanations, "Token 'его' not found in word_explanations"
        role_ego, meaning_ego = explanations["его"]
        assert role_ego in ("personal_pronoun", "pronoun"), (
            f"'его' was tagged '{role_ego}' — must be personal_pronoun/pronoun, not noun."
        )

        # ним (instrumental after с) must be pronoun.
        assert "ним" in explanations, "Token 'ним' not found in word_explanations"
        role_nim, meaning_nim = explanations["ним"]
        assert role_nim in ("personal_pronoun", "pronoun"), (
            f"'ним' was tagged '{role_nim}' — must be personal_pronoun/pronoun, not noun."
        )
        assert "instrumental" in meaning_nim.lower(), (
            f"'ним' meaning should mention instrumental case; got: {meaning_nim!r}"
        )

    def test_batch_fallback_quality_regression(self):
        """Run the validator against the fallback output and assert quality_score > 0.7."""
        analyzer = RuAnalyzer()
        broken_sentence = "Я вижу его и говорю с ним."
        with patch.object(RuAnalyzer, "_call_ai", side_effect=Exception("API down")):
            results = analyzer.batch_analyze_grammar(
                [broken_sentence], "вижу", "beginner", FAKE_KEY
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
