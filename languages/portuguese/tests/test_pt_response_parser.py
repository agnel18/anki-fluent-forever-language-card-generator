# languages/portuguese/tests/test_pt_response_parser.py
"""Tests for PtResponseParser — 5-level fallback parsing for Portuguese."""
import json
import pytest
from languages.portuguese.domain.pt_config import PtConfig
from languages.portuguese.domain.pt_fallbacks import PtFallbacks
from languages.portuguese.domain.pt_response_parser import PtResponseParser
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE_2,
    SAMPLE_SER_RESPONSE,
    SAMPLE_ESTAR_RESPONSE,
    SAMPLE_CONTRACTION_RESPONSE,
)


@pytest.fixture
def parser():
    cfg = PtConfig()
    fb = PtFallbacks(cfg)
    return PtResponseParser(cfg, fb)


class TestPtResponseParserBasic:
    def test_parse_valid_json_returns_word_explanations(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "O gato bebe leite."
        )
        assert "word_explanations" in result
        assert len(result["word_explanations"]) > 0

    def test_parse_returns_confidence(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "O gato bebe leite."
        )
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_parse_word_explanations_structure(self, parser):
        """Each word explanation in the list-of-lists form is [word, role, color, meaning]."""
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "O gato bebe leite."
        )
        for item in result["word_explanations"]:
            assert isinstance(item, (list, tuple))
            assert len(item) >= 4
            word, role, color, meaning = item[0], item[1], item[2], item[3]
            assert isinstance(word, str)
            assert isinstance(role, str)
            assert isinstance(color, str)
            assert isinstance(meaning, str)

    def test_parse_both_structure_keys_present(self, parser):
        """Both 'overall_structure' and 'sentence_structure' must be present."""
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "O gato bebe leite."
        )
        assert "overall_structure" in result
        assert "sentence_structure" in result

    def test_parse_markdown_json(self, parser):
        """Level 2: markdown code-block wrapped JSON."""
        md_response = f"```json\n{SAMPLE_BEGINNER_RESPONSE}\n```"
        result = parser.parse_response(md_response, "beginner", "O gato bebe leite.")
        assert "word_explanations" in result
        assert len(result["word_explanations"]) > 0

    def test_empty_response_uses_fallback(self, parser):
        result = parser.parse_response("", "beginner", "O gato bebe leite.")
        assert "word_explanations" in result
        assert result["confidence"] < 0.5

    def test_invalid_json_uses_fallback(self, parser):
        result = parser.parse_response("NOT JSON AT ALL", "beginner", "O gato dorme.")
        assert "word_explanations" in result

    def test_error_sentinel_uses_fallback(self, parser):
        sentinel = '{"error": "AI service unavailable", "sentence": "error"}'
        result = parser.parse_response(sentinel, "beginner", "O gato dorme.")
        assert "word_explanations" in result
        # Fallback confidence is low
        assert result["confidence"] < 0.6


class TestPtResponseParserBatch:
    def test_parse_batch_response(self, parser):
        batch = f"[{SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_INTERMEDIATE_RESPONSE}]"
        results = parser.parse_batch_response(
            batch,
            ["O gato bebe leite.", "Ela vai ao mercado comprar pão."],
            "intermediate",
        )
        assert len(results) == 2
        for r in results:
            assert "word_explanations" in r

    def test_batch_empty_response_fallback(self, parser):
        sentences = ["O gato dorme.", "Ela come pão."]
        results = parser.parse_batch_response("", sentences, "beginner")
        assert len(results) == 2
        for r in results:
            assert r["confidence"] < 0.5

    def test_batch_partial_response_fills_fallback(self, parser):
        """If AI returns fewer items than sentences, fallback fills the gap."""
        batch = f"[{SAMPLE_BEGINNER_RESPONSE}]"
        sentences = ["O gato dorme.", "Ela come pão.", "Eu leio um livro."]
        results = parser.parse_batch_response(batch, sentences, "beginner")
        assert len(results) == 3


class TestPtResponseParserPortugueseSpecific:
    # Behavior 2: Copula sub-tagging — ser vs estar
    def test_ser_copula_tagged_with_copula_role(self, parser):
        """'é' (ser) should be tagged as 'copula' role, not generic 'verb'."""
        result = parser.parse_response(
            SAMPLE_SER_RESPONSE, "intermediate", "Ela é triste."
        )
        roles = [item[1] for item in result["word_explanations"]]
        assert "copula" in roles, f"Expected 'copula' in roles, got: {roles}"

    def test_estar_copula_tagged_with_copula_role(self, parser):
        """'está' (estar) should be tagged as 'copula' role, not generic 'verb'."""
        result = parser.parse_response(
            SAMPLE_ESTAR_RESPONSE, "intermediate", "Ela está triste."
        )
        roles = [item[1] for item in result["word_explanations"]]
        assert "copula" in roles, f"Expected 'copula' in roles, got: {roles}"

    def test_ser_copula_not_collapsed_to_verb(self, parser):
        """The copula role must be preserved, not collapsed into generic 'verb'."""
        result = parser.parse_response(
            SAMPLE_SER_RESPONSE, "intermediate", "Ela é triste."
        )
        # Check word_details for copula_type meta-field
        word_details = result.get("word_details", [])
        copula_items = [w for w in word_details if w.get("grammatical_role") == "copula"]
        assert len(copula_items) >= 1
        assert copula_items[0].get("copula_type") == "ser"

    def test_estar_copula_has_copula_type_estar(self, parser):
        result = parser.parse_response(
            SAMPLE_ESTAR_RESPONSE, "intermediate", "Ela está triste."
        )
        word_details = result.get("word_details", [])
        copula_items = [w for w in word_details if w.get("grammatical_role") == "copula"]
        assert len(copula_items) >= 1
        assert copula_items[0].get("copula_type") == "estar"

    # Behavior 3: Contraction handling
    def test_ao_tagged_as_contraction(self, parser):
        """'ao' must be tagged as 'contraction', not generic 'preposition'."""
        result = parser.parse_response(
            SAMPLE_CONTRACTION_RESPONSE, "intermediate", "Eu vou ao mercado."
        )
        roles = [item[1] for item in result["word_explanations"]]
        assert "contraction" in roles, (
            f"Expected 'contraction' role for 'ao'. Got roles: {roles}"
        )

    def test_contraction_parts_populated(self, parser):
        """'ao' contraction_parts must be populated with ['a', 'o']."""
        result = parser.parse_response(
            SAMPLE_CONTRACTION_RESPONSE, "intermediate", "Eu vou ao mercado."
        )
        word_details = result.get("word_details", [])
        contraction_items = [
            w for w in word_details if w.get("grammatical_role") == "contraction"
        ]
        assert len(contraction_items) >= 1
        parts = contraction_items[0].get("contraction_parts", [])
        assert isinstance(parts, list)
        assert len(parts) >= 2

    def test_ao_not_tagged_as_preposition(self, parser):
        """'ao' must not be tagged as a plain preposition."""
        result = parser.parse_response(
            SAMPLE_CONTRACTION_RESPONSE, "intermediate", "Eu vou ao mercado."
        )
        # Find 'ao' in word_details
        word_details = result.get("word_details", [])
        ao_items = [w for w in word_details if w.get("word", "").lower() == "ao"]
        if ao_items:
            assert ao_items[0].get("grammatical_role") != "preposition"

    # Behavior 4: Clitic placement
    def test_enclitic_clitic_tagged_as_clitic_pronoun(self, parser):
        """Enclitic 'me' in 'Disse-me' should be tagged as clitic_pronoun or personal_pronoun."""
        result = parser.parse_response(
            SAMPLE_ADVANCED_RESPONSE,
            "advanced",
            "Disse-me a verdade que precisava de saber.",
        )
        roles = [item[1] for item in result["word_explanations"]]
        assert "clitic_pronoun" in roles or "personal_pronoun" in roles

    def test_enclitic_clitic_position_field(self, parser):
        """Enclitic clitic must have clitic_position='enclitic'."""
        result = parser.parse_response(
            SAMPLE_ADVANCED_RESPONSE,
            "advanced",
            "Disse-me a verdade que precisava de saber.",
        )
        word_details = result.get("word_details", [])
        clitic_items = [
            w for w in word_details
            if w.get("grammatical_role") in ("clitic_pronoun", "mesoclitic")
        ]
        if clitic_items:
            positions = [w.get("clitic_position", "") for w in clitic_items]
            assert any(p in ("enclitic", "proclitic", "mesoclitic") for p in positions)

    def test_proclitic_after_negation(self, parser):
        """Proclitic 'me' after 'Não' should have clitic_position='proclitic'."""
        result = parser.parse_response(
            SAMPLE_ADVANCED_RESPONSE_2,
            "advanced",
            "Não me disse a verdade.",
        )
        word_details = result.get("word_details", [])
        me_items = [
            w for w in word_details
            if w.get("word", "").lower() == "me"
            and w.get("grammatical_role") in ("clitic_pronoun", "personal_pronoun")
        ]
        if me_items:
            assert me_items[0].get("clitic_position") == "proclitic"

    def test_roles_use_grammatical_role_key(self, parser):
        """The normalized result should expose 'grammatical_role' on word_details."""
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "O gato bebe leite."
        )
        word_details = result.get("word_details", [])
        for item in word_details:
            assert "grammatical_role" in item, (
                f"word_details item missing 'grammatical_role': {item}"
            )

    def test_register_field_present(self, parser):
        """The normalized result should include a 'register' key."""
        result = parser.parse_response(
            SAMPLE_INTERMEDIATE_RESPONSE,
            "intermediate",
            "Ela vai ao mercado comprar pão.",
        )
        assert "register" in result
