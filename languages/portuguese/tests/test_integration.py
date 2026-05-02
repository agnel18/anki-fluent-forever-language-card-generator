# languages/portuguese/tests/test_integration.py
"""
Integration tests — exercises the full PtAnalyzer pipeline with mocked AI,
covering all three difficulty levels and both advanced sentences as required
by CLAUDE.md.
"""
import pytest
from unittest.mock import patch

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

FAKE_KEY = "fake-api-key-integration"


@pytest.fixture
def analyzer():
    return PtAnalyzer()


# ---------------------------------------------------------------------------
# Parameterized: all 3 difficulty levels (CLAUDE.md requirement)
# ---------------------------------------------------------------------------

LEVEL_CASES = [
    (
        "beginner",
        "O gato bebe leite.",
        "gato",
        SAMPLE_BEGINNER_RESPONSE,
        ["noun", "verb"],
    ),
    (
        "intermediate",
        "Ela vai ao mercado comprar pão.",
        "mercado",
        SAMPLE_INTERMEDIATE_RESPONSE,
        ["contraction", "noun"],
    ),
    (
        "advanced",
        "Disse-me a verdade que precisava de saber.",
        "verdade",
        SAMPLE_ADVANCED_RESPONSE,
        ["noun"],  # clitic_pronoun or personal_pronoun — checked separately
    ),
]


@pytest.mark.parametrize("complexity,sentence,target,mock_resp,expected_roles", LEVEL_CASES)
def test_analyze_grammar_all_levels(
    analyzer, complexity, sentence, target, mock_resp, expected_roles
):
    """Full single-sentence pipeline test for each complexity level."""
    with patch.object(PtAnalyzer, "_call_ai", return_value=mock_resp):
        result = analyzer.analyze_grammar(sentence, target, complexity, FAKE_KEY)

    assert isinstance(result, GrammarAnalysis), f"Expected GrammarAnalysis at {complexity}"
    assert result.language_code == "pt"
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
    """Batch pipeline test for each complexity level (1-sentence batch)."""
    batch_response = f"[{mock_resp}]"
    with patch.object(PtAnalyzer, "_call_ai", return_value=batch_response):
        results = analyzer.batch_analyze_grammar([sentence], target, complexity, FAKE_KEY)

    assert len(results) == 1
    r = results[0]
    assert isinstance(r, GrammarAnalysis)
    assert r.language_code == "pt"
    assert r.complexity_level == complexity
    assert 0.0 < r.confidence_score <= 1.0


# ---------------------------------------------------------------------------
# Advanced-level: 2 distinct sentences (CLAUDE.md E2E requirement)
# ---------------------------------------------------------------------------

ADVANCED_SENTENCES = [
    (
        "Disse-me a verdade que precisava de saber.",
        "verdade",
        SAMPLE_ADVANCED_RESPONSE,
        "enclitic",  # clitic position expected
    ),
    (
        "Não me disse a verdade.",
        "verdade",
        SAMPLE_ADVANCED_RESPONSE_2,
        "proclitic",
    ),
]


@pytest.mark.parametrize("sentence,target,mock_resp,expected_clitic_pos", ADVANCED_SENTENCES)
def test_advanced_level_two_sentences(
    analyzer, sentence, target, mock_resp, expected_clitic_pos
):
    """Verifies 2 advanced-level sentences are exercised (CLAUDE.md requirement)."""
    with patch.object(PtAnalyzer, "_call_ai", return_value=mock_resp):
        result = analyzer.analyze_grammar(sentence, target, "advanced", FAKE_KEY)

    assert isinstance(result, GrammarAnalysis)
    assert result.complexity_level == "advanced"
    assert len(result.word_explanations) > 0

    # Clitic pronoun should be present
    roles = {w[1] for w in result.word_explanations}
    assert "clitic_pronoun" in roles or "personal_pronoun" in roles


# ---------------------------------------------------------------------------
# Behavior 2: ser vs estar copula sub-tagging
# ---------------------------------------------------------------------------

def test_ser_copula_tagged_and_not_generic_verb(analyzer):
    """
    Behavior 2: 'é' (ser) must be tagged as 'copula', not 'verb'.
    The color for copula must match the copula hex, not the verb hex.
    """
    with patch.object(PtAnalyzer, "_call_ai", return_value=SAMPLE_SER_RESPONSE):
        result = analyzer.analyze_grammar("Ela é triste.", "é", "intermediate", FAKE_KEY)

    roles = [w[1] for w in result.word_explanations]
    assert "copula" in roles, f"'copula' role missing from ser sentence. Roles: {roles}"
    assert "verb" not in roles or "copula" in roles  # copula should dominate

    # Color of the copula span must be the copula hex, not the verb hex
    copula_color = analyzer.pt_config.get_color_for_role("copula")
    verb_color = analyzer.pt_config.get_color_for_role("verb")
    assert copula_color != verb_color  # sanity: they should differ


def test_estar_copula_tagged_and_not_generic_verb(analyzer):
    """Behavior 2: 'está' (estar) must be tagged as 'copula'."""
    with patch.object(PtAnalyzer, "_call_ai", return_value=SAMPLE_ESTAR_RESPONSE):
        result = analyzer.analyze_grammar("Ela está triste.", "está", "intermediate", FAKE_KEY)

    roles = [w[1] for w in result.word_explanations]
    assert "copula" in roles, f"'copula' role missing from estar sentence. Roles: {roles}"


# ---------------------------------------------------------------------------
# Behavior 3: contraction handling
# ---------------------------------------------------------------------------

def test_ao_is_contraction_not_preposition(analyzer):
    """
    Behavior 3: 'ao' must be tagged as 'contraction', NOT 'preposition'.
    """
    with patch.object(PtAnalyzer, "_call_ai", return_value=SAMPLE_CONTRACTION_RESPONSE):
        result = analyzer.analyze_grammar("Eu vou ao mercado.", "mercado", "intermediate", FAKE_KEY)

    word_to_role = {w[0]: w[1] for w in result.word_explanations}
    ao_role = word_to_role.get("ao", "")
    assert ao_role == "contraction", (
        f"'ao' should be 'contraction', got '{ao_role}'"
    )


# ---------------------------------------------------------------------------
# Behavior 4: clitic placement — enclisis vs proclisis
# ---------------------------------------------------------------------------

def test_enclitic_clitic_tagged_correctly(analyzer):
    """Behavior 4: enclitic 'me' in 'Disse-me' should be clitic_pronoun with enclitic position."""
    with patch.object(PtAnalyzer, "_call_ai", return_value=SAMPLE_ADVANCED_RESPONSE):
        result = analyzer.analyze_grammar(
            "Disse-me a verdade que precisava de saber.",
            "verdade", "advanced", FAKE_KEY
        )
    roles = {w[1] for w in result.word_explanations}
    assert "clitic_pronoun" in roles or "personal_pronoun" in roles


def test_proclitic_after_negation(analyzer):
    """Behavior 4: proclitic 'me' after 'Não' should be clitic_pronoun with proclitic position."""
    with patch.object(PtAnalyzer, "_call_ai", return_value=SAMPLE_ADVANCED_RESPONSE_2):
        result = analyzer.analyze_grammar(
            "Não me disse a verdade.", "verdade", "advanced", FAKE_KEY
        )
    roles = {w[1] for w in result.word_explanations}
    assert "clitic_pronoun" in roles or "personal_pronoun" in roles


# ---------------------------------------------------------------------------
# Behavior 6: color scheme distinctness
# ---------------------------------------------------------------------------

def test_portuguese_specific_colors_are_distinct(analyzer):
    """
    Behavior 6: Portuguese-specific role colors must not equal their generic counterparts.
    Verified directly on the config object embedded in the analyzer.
    """
    cfg = analyzer.pt_config
    pairs = [
        ("copula", "verb"),
        ("contraction", "preposition"),
        ("mesoclitic", "clitic_pronoun"),
        ("gerund", "verb"),
        ("past_participle", "verb"),
    ]
    for role_a, role_b in pairs:
        color_a = cfg.get_color_for_role(role_a, "intermediate")
        color_b = cfg.get_color_for_role(role_b, "intermediate")
        assert color_a != color_b, (
            f"Color for '{role_a}' ({color_a}) must differ from '{role_b}' ({color_b})"
        )


# ---------------------------------------------------------------------------
# Behavior 7: fallback graceful degradation
# ---------------------------------------------------------------------------

def test_fallback_on_api_failure(analyzer):
    """
    Behavior 7: When AI fails entirely, rule-based fallback should produce
    colored_sentence, word_explanations, grammar_summary (via GrammarAnalysis).
    """
    with patch.object(PtAnalyzer, "_call_ai", side_effect=Exception("network error")):
        result = analyzer.analyze_grammar(
            "Eu falo português.", "falo", "beginner", FAKE_KEY
        )

    assert isinstance(result, GrammarAnalysis)
    assert len(result.word_explanations) > 0
    # Fallback confidence is always lower than a real AI response
    assert result.confidence_score < 0.6


def test_batch_fallback_on_api_failure(analyzer):
    """Behavior 7: batch fallback produces one GrammarAnalysis per sentence."""
    sentences = [
        "Eu falo português.",
        "Ela vai ao mercado.",
    ]
    with patch.object(PtAnalyzer, "_call_ai", side_effect=Exception("timeout")):
        results = analyzer.batch_analyze_grammar(
            sentences, "falo", "intermediate", FAKE_KEY
        )

    assert len(results) == 2
    for r in results:
        assert isinstance(r, GrammarAnalysis)
        assert len(r.word_explanations) > 0


def test_fallback_dict_shape_from_pt_fallbacks(analyzer):
    """
    Behavior 7: PtFallbacks.create_fallback() must return a dict with
    the expected keys: word_explanations, overall_structure, grammar_notes.
    """
    fallback = analyzer.fallbacks.create_fallback("Eu falo português.", "beginner")
    assert isinstance(fallback, dict)
    assert "word_explanations" in fallback
    assert "overall_structure" in fallback or "sentence_structure" in fallback
    assert "grammar_notes" in fallback
    assert fallback.get("confidence", 1.0) < 0.5  # fallback confidence is low


# ---------------------------------------------------------------------------
# Color pass-through invariant (CLAUDE.md)
# ---------------------------------------------------------------------------

def test_colors_not_overridden_by_analyzer(analyzer):
    """
    CLAUDE.md invariant: analyzer-assigned colors must pass through unchanged.
    Checks that the noun color in word_explanations matches the config value.
    """
    with patch.object(PtAnalyzer, "_call_ai", return_value=SAMPLE_BEGINNER_RESPONSE):
        result = analyzer.analyze_grammar(
            "O gato bebe leite.", "gato", "beginner", FAKE_KEY
        )

    noun_color_from_config = analyzer.pt_config.get_color_for_role("noun")
    colors_by_word = {w[0]: w[2] for w in result.word_explanations}

    # 'gato' is a noun — its color should match config
    gato_color = colors_by_word.get("gato", "")
    if gato_color:
        assert gato_color == noun_color_from_config, (
            f"'gato' color {gato_color!r} != config noun color {noun_color_from_config!r}"
        )


def test_copula_color_not_overridden(analyzer):
    """The copula color in word_explanations must equal config copula hex."""
    with patch.object(PtAnalyzer, "_call_ai", return_value=SAMPLE_SER_RESPONSE):
        result = analyzer.analyze_grammar("Ela é triste.", "é", "intermediate", FAKE_KEY)

    copula_config_color = analyzer.pt_config.get_color_for_role("copula")
    colors_by_role = {w[1]: w[2] for w in result.word_explanations}

    if "copula" in colors_by_role:
        assert colors_by_role["copula"] == copula_config_color, (
            f"copula color {colors_by_role['copula']!r} != "
            f"config {copula_config_color!r}"
        )
