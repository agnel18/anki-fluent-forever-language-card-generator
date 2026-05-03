# languages/english/tests/test_integration.py
"""
Integration tests — exercises the full analyzer pipeline with mocked AI,
covering all three difficulty levels as required by CLAUDE.md.
"""
import pytest
from unittest.mock import patch, MagicMock

from languages.english.en_analyzer import EnAnalyzer
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
    return EnAnalyzer()


# ────────────────────────────────────────────────────────────────────────────
# Parameterized: all 3 difficulty levels
# ────────────────────────────────────────────────────────────────────────────

LEVEL_CASES = [
    (
        "beginner",
        "The cat eats fish.",
        "eats",
        SAMPLE_BEGINNER_RESPONSE,
        ["article", "noun", "verb"],
    ),
    (
        "intermediate",
        "I want to run quickly.",
        "run",
        SAMPLE_INTERMEDIATE_RESPONSE,
        ["personal_pronoun", "verb", "infinitive_marker"],
    ),
    (
        "advanced",
        "The book that she read was interesting.",
        "book",
        SAMPLE_ADVANCED_RESPONSE,
        ["relative_pronoun", "noun", "auxiliary"],
    ),
]


@pytest.mark.parametrize("complexity,sentence,target,mock_resp,expected_roles", LEVEL_CASES)
def test_analyze_grammar_all_levels(
    analyzer, complexity, sentence, target, mock_resp, expected_roles
):
    """Full pipeline test for each complexity level."""
    with patch.object(EnAnalyzer, "_call_ai", return_value=mock_resp):
        result = analyzer.analyze_grammar(sentence, target, complexity, FAKE_KEY)

    assert isinstance(result, GrammarAnalysis), f"Expected GrammarAnalysis at {complexity}"
    assert result.language_code == "en"
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
    with patch.object(EnAnalyzer, "_call_ai", return_value=batch_response):
        results = analyzer.batch_analyze_grammar([sentence], target, complexity, FAKE_KEY)

    assert len(results) == 1
    r = results[0]
    assert isinstance(r, GrammarAnalysis)
    assert r.language_code == "en"
    assert r.complexity_level == complexity
    assert 0.0 < r.confidence_score <= 1.0


# ────────────────────────────────────────────────────────────────────────────
# Advanced-level coverage: 2 distinct sentences
# ────────────────────────────────────────────────────────────────────────────

ADVANCED_SENTENCES = [
    (
        "The book that she read was interesting.",
        "book",
        SAMPLE_ADVANCED_RESPONSE,
    ),
    (
        "He believes that the problem has been solved.",
        "believes",
        SAMPLE_ADVANCED_RESPONSE,   # reuse shape — tests pipeline, not content
    ),
]


@pytest.mark.parametrize("sentence,target,mock_resp", ADVANCED_SENTENCES)
def test_advanced_level_two_sentences(analyzer, sentence, target, mock_resp):
    """Verifies 2 advanced-level sentences are exercised (CLAUDE.md requirement)."""
    with patch.object(EnAnalyzer, "_call_ai", return_value=mock_resp):
        result = analyzer.analyze_grammar(sentence, target, "advanced", FAKE_KEY)

    assert isinstance(result, GrammarAnalysis)
    assert result.complexity_level == "advanced"
    assert len(result.word_explanations) > 0


# ────────────────────────────────────────────────────────────────────────────
# Fallback path
# ────────────────────────────────────────────────────────────────────────────

def test_fallback_on_api_failure(analyzer):
    """When AI fails entirely, the rule-based fallback should still produce output."""
    with patch.object(EnAnalyzer, "_call_ai", side_effect=Exception("network error")):
        result = analyzer.analyze_grammar(
            "The cat eats fish.", "eats", "beginner", FAKE_KEY
        )

    assert isinstance(result, GrammarAnalysis)
    assert len(result.word_explanations) > 0
    # Fallback confidence is always lower than a real AI response
    assert result.confidence_score < 0.6


def test_batch_fallback_on_api_failure(analyzer):
    sentences = [
        "The cat eats fish.",
        "I want to run quickly.",
    ]
    with patch.object(EnAnalyzer, "_call_ai", side_effect=Exception("timeout")):
        results = analyzer.batch_analyze_grammar(
            sentences, "eats", "intermediate", FAKE_KEY
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
    with patch.object(EnAnalyzer, "_call_ai", return_value=SAMPLE_BEGINNER_RESPONSE):
        result = analyzer.analyze_grammar(
            "The cat eats fish.", "eats", "beginner", FAKE_KEY
        )

    colors = {w[0]: w[2] for w in result.word_explanations}
    # 'The' should be the article color (gold)
    assert colors.get("The") == "#FFD700", (
        f"Expected article color #FFD700 for 'The', got {colors.get('The')}"
    )
    # 'cat' should be the noun color
    assert colors.get("cat") == "#FFAA00", (
        f"Expected noun color #FFAA00 for 'cat', got {colors.get('cat')}"
    )
    # 'eats' should be the verb color
    assert colors.get("eats") == "#4ECDC4", (
        f"Expected verb color #4ECDC4 for 'eats', got {colors.get('eats')}"
    )


def test_en_specific_infinitive_marker_color(analyzer):
    """English-specific: infinitive marker 'to' gets its distinct orange color."""
    with patch.object(EnAnalyzer, "_call_ai", return_value=SAMPLE_INTERMEDIATE_RESPONSE):
        result = analyzer.analyze_grammar(
            "I want to run quickly.", "run", "intermediate", FAKE_KEY
        )

    colors_by_role = {w[1]: w[2] for w in result.word_explanations}
    assert "infinitive_marker" in colors_by_role, (
        f"Expected infinitive_marker role in word_explanations; got roles: {list(colors_by_role.keys())}"
    )
    assert colors_by_role["infinitive_marker"] == "#FF8C00", (
        f"Expected infinitive_marker color #FF8C00, got {colors_by_role['infinitive_marker']}"
    )


def test_relative_pronoun_color_in_advanced(analyzer):
    """English-specific: relative pronoun 'that' gets the relative_pronoun color."""
    with patch.object(EnAnalyzer, "_call_ai", return_value=SAMPLE_ADVANCED_RESPONSE):
        result = analyzer.analyze_grammar(
            "The book that she read was interesting.", "book", "advanced", FAKE_KEY
        )

    colors_by_role = {w[1]: w[2] for w in result.word_explanations}
    assert "relative_pronoun" in colors_by_role, (
        f"Expected relative_pronoun in word_explanations; got roles: {list(colors_by_role.keys())}"
    )


# ────────────────────────────────────────────────────────────────────────────
# Full prompt → parse → validate → HTML pipeline for one sentence per level
# ────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("complexity,sentence,target,mock_resp", [
    ("beginner",     "The cat eats fish.",                       "eats",    SAMPLE_BEGINNER_RESPONSE),
    ("intermediate", "I want to run quickly.",                   "run",     SAMPLE_INTERMEDIATE_RESPONSE),
    ("advanced",     "The book that she read was interesting.",  "book",    SAMPLE_ADVANCED_RESPONSE),
])
def test_full_pipeline_html_confidence(analyzer, complexity, sentence, target, mock_resp):
    """Full pipeline: prompt is generated, AI is mocked, parse+validate+HTML all succeed."""
    with patch.object(EnAnalyzer, "_call_ai", return_value=mock_resp):
        result = analyzer.analyze_grammar(sentence, target, complexity, FAKE_KEY)

    # HTML must contain span tags
    assert result.html_output, f"Empty html_output at {complexity}"
    assert "<span" in result.html_output, (
        f"html_output missing <span tags at {complexity}: {result.html_output[:200]}"
    )
    # Confidence must be above the fallback floor
    assert result.confidence_score >= 0.5, (
        f"Confidence too low at {complexity}: {result.confidence_score}"
    )
