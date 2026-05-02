# languages/latvian/tests/test_integration.py
"""
Integration tests — exercises the full analyzer pipeline with mocked AI,
covering all three difficulty levels as required by CLAUDE.md.
"""
import pytest
from unittest.mock import patch, MagicMock

from languages.latvian.lv_analyzer import LvAnalyzer
from streamlit_app.language_analyzers.base_analyzer import GrammarAnalysis
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
)

FAKE_KEY = "fake-api-key-integration"

# ────────────────────────────────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def analyzer():
    return LvAnalyzer()


# ────────────────────────────────────────────────────────────────────────────
# Parameterized: all 3 difficulty levels
# ────────────────────────────────────────────────────────────────────────────

LEVEL_CASES = [
    (
        "beginner",
        "Es runāju latviski.",
        "runāju",
        SAMPLE_BEGINNER_RESPONSE,
        ["personal_pronoun", "verb", "adverb"],
    ),
    (
        "intermediate",
        "Man jāmācās latviešu valoda.",
        "jāmācās",
        SAMPLE_INTERMEDIATE_RESPONSE,
        ["personal_pronoun", "debitive", "noun"],
    ),
    (
        "advanced",
        "Uzrakstītā vēstule tika nosūtīta vakar.",
        "vēstule",
        SAMPLE_ADVANCED_RESPONSE,
        ["participle", "noun", "auxiliary"],
    ),
]


@pytest.mark.parametrize("complexity,sentence,target,mock_resp,expected_roles", LEVEL_CASES)
def test_analyze_grammar_all_levels(
    analyzer, complexity, sentence, target, mock_resp, expected_roles
):
    """Full pipeline test for each complexity level."""
    with patch.object(LvAnalyzer, "_call_ai", return_value=mock_resp):
        result = analyzer.analyze_grammar(sentence, target, complexity, FAKE_KEY)

    assert isinstance(result, GrammarAnalysis), f"Expected GrammarAnalysis at {complexity}"
    assert result.language_code == "lv"
    assert result.complexity_level == complexity
    assert result.sentence == sentence
    assert result.target_word == target
    assert 0.0 < result.confidence_score <= 1.0
    assert len(result.word_explanations) > 0

    actual_roles = {w[1] for w in result.word_explanations}
    for role in expected_roles:
        assert role in actual_roles, (
            f"Expected role '{role}' missing at {complexity}. Got: {actual_roles}"
        )

    # HTML output must be populated
    assert result.html_output and "<span" in result.html_output


@pytest.mark.parametrize("complexity,sentence,target,mock_resp,expected_roles", LEVEL_CASES)
def test_batch_analyze_all_levels(
    analyzer, complexity, sentence, target, mock_resp, expected_roles
):
    """Batch pipeline test for each complexity level (1 sentence per batch)."""
    batch_response = f"[{mock_resp}]"
    with patch.object(LvAnalyzer, "_call_ai", return_value=batch_response):
        results = analyzer.batch_analyze_grammar([sentence], target, complexity, FAKE_KEY)

    assert len(results) == 1
    r = results[0]
    assert isinstance(r, GrammarAnalysis)
    assert r.language_code == "lv"
    assert r.complexity_level == complexity
    assert 0.0 < r.confidence_score <= 1.0


# ────────────────────────────────────────────────────────────────────────────
# Advanced-level coverage: 2 distinct sentences required by CLAUDE.md
# ────────────────────────────────────────────────────────────────────────────

ADVANCED_SENTENCES = [
    (
        "Uzrakstītā vēstule tika nosūtīta vakar.",
        "vēstule",
        SAMPLE_ADVANCED_RESPONSE,
    ),
    (
        "Ja viņš būtu studējis vairāk, viņš būtu nokārtojis eksāmenu.",
        "nokārtojis",
        SAMPLE_ADVANCED_RESPONSE,   # reuse shape — tests pipeline, not content
    ),
]


@pytest.mark.parametrize("sentence,target,mock_resp", ADVANCED_SENTENCES)
def test_advanced_level_two_sentences(analyzer, sentence, target, mock_resp):
    """Verifies 2 advanced-level sentences are exercised (CLAUDE.md requirement)."""
    with patch.object(LvAnalyzer, "_call_ai", return_value=mock_resp):
        result = analyzer.analyze_grammar(sentence, target, "advanced", FAKE_KEY)

    assert isinstance(result, GrammarAnalysis)
    assert result.complexity_level == "advanced"
    assert len(result.word_explanations) > 0


# ────────────────────────────────────────────────────────────────────────────
# Fallback path
# ────────────────────────────────────────────────────────────────────────────

def test_fallback_on_api_failure(analyzer):
    """When AI fails entirely, the rule-based fallback should still produce output."""
    with patch.object(LvAnalyzer, "_call_ai", side_effect=Exception("network error")):
        result = analyzer.analyze_grammar(
            "Es runāju latviski.", "runāju", "beginner", FAKE_KEY
        )

    assert isinstance(result, GrammarAnalysis)
    assert len(result.word_explanations) > 0
    # Fallback confidence is always lower than a real AI response
    assert result.confidence_score < 0.6


def test_batch_fallback_on_api_failure(analyzer):
    sentences = [
        "Es runāju latviski.",
        "Man jāmācās latviešu valoda.",
    ]
    with patch.object(LvAnalyzer, "_call_ai", side_effect=Exception("timeout")):
        results = analyzer.batch_analyze_grammar(
            sentences, "runāju", "intermediate", FAKE_KEY
        )

    assert len(results) == 2
    for r in results:
        assert isinstance(r, GrammarAnalysis)
        assert len(r.word_explanations) > 0


# ────────────────────────────────────────────────────────────────────────────
# Grammar coloring invariant (CLAUDE.md: analyzer colors must not be overridden)
# ────────────────────────────────────────────────────────────────────────────

def test_colors_not_overridden(analyzer):
    """
    Analyzer-assigned colors must pass through unchanged.
    CLAUDE.md invariant: grammar_processor must not re-map POS colors.
    This test verifies the analyzer itself returns the expected hex colors.
    """
    with patch.object(LvAnalyzer, "_call_ai", return_value=SAMPLE_BEGINNER_RESPONSE):
        result = analyzer.analyze_grammar(
            "Es runāju latviski.", "runāju", "beginner", FAKE_KEY
        )

    colors = {w[0]: w[2] for w in result.word_explanations}
    assert colors.get("Es") == "#9370DB"   # personal_pronoun
    assert colors.get("runāju") == "#4ECDC4"  # verb


def test_lv_specific_debitive_color(analyzer):
    with patch.object(LvAnalyzer, "_call_ai", return_value=SAMPLE_INTERMEDIATE_RESPONSE):
        result = analyzer.analyze_grammar(
            "Man jāmācās latviešu valoda.", "jāmācās", "intermediate", FAKE_KEY
        )

    colors_by_role = {w[1]: w[2] for w in result.word_explanations}
    assert "debitive" in colors_by_role
    assert colors_by_role["debitive"] == "#FF1493"
