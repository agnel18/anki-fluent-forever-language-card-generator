# languages/english/tests/test_en_response_parser.py
"""Tests for EnResponseParser."""
import json
import pytest
from languages.english.domain.en_config import EnConfig
from languages.english.domain.en_fallbacks import EnFallbacks
from languages.english.domain.en_response_parser import EnResponseParser
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
)


@pytest.fixture
def parser():
    cfg = EnConfig()
    fb = EnFallbacks(cfg)
    return EnResponseParser(cfg, fb)


class TestEnResponseParser:
    def test_parse_valid_json(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "The cat eats fish."
        )
        assert "word_explanations" in result
        assert len(result["word_explanations"]) > 0

    def test_parse_returns_confidence(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "The cat eats fish."
        )
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_parse_word_explanations_structure(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "The cat eats fish."
        )
        for item in result["word_explanations"]:
            assert "word" in item
            assert "role" in item
            assert "color" in item
            assert "meaning" in item

    def test_parse_markdown_json(self, parser):
        md_response = f"```json\n{SAMPLE_BEGINNER_RESPONSE}\n```"
        result = parser.parse_response(md_response, "beginner", "The cat eats fish.")
        assert "word_explanations" in result
        assert len(result["word_explanations"]) > 0

    def test_empty_response_uses_fallback(self, parser):
        result = parser.parse_response("", "beginner", "The cat eats fish.")
        assert "word_explanations" in result
        # Fallback confidence is lower
        assert result["confidence"] < 0.5

    def test_invalid_json_uses_fallback(self, parser):
        result = parser.parse_response("NOT JSON AT ALL", "beginner", "The cat eats fish.")
        assert "word_explanations" in result

    def test_parse_batch_response(self, parser):
        batch = f"[{SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_INTERMEDIATE_RESPONSE}]"
        results = parser.parse_batch_response(
            batch,
            ["The cat eats fish.", "I want to run quickly."],
            "intermediate",
        )
        assert len(results) == 2
        for r in results:
            assert "word_explanations" in r

    def test_batch_empty_response_fallback(self, parser):
        sentences = ["The cat eats fish.", "She reads a book."]
        results = parser.parse_batch_response("", sentences, "beginner")
        assert len(results) == 2
        for r in results:
            assert r["confidence"] < 0.5

    def test_intermediate_response_has_infinitive_marker(self, parser):
        """Intermediate response for 'I want to run quickly.' should have infinitive_marker."""
        result = parser.parse_response(
            SAMPLE_INTERMEDIATE_RESPONSE,
            "intermediate",
            "I want to run quickly.",
        )
        roles = [item["role"] for item in result["word_explanations"]]
        assert "infinitive_marker" in roles, (
            f"Expected infinitive_marker in intermediate parse, got: {roles}"
        )

    def test_advanced_response_has_relative_pronoun(self, parser):
        """Advanced response should have relative_pronoun for 'that'."""
        result = parser.parse_response(
            SAMPLE_ADVANCED_RESPONSE,
            "advanced",
            "The book that she read was interesting.",
        )
        roles = [item["role"] for item in result["word_explanations"]]
        assert "relative_pronoun" in roles, (
            f"Expected relative_pronoun in advanced parse, got: {roles}"
        )

    def test_both_structure_keys_present(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "The cat eats fish."
        )
        assert "overall_structure" in result
        assert "sentence_structure" in result

    def test_individual_meaning_preserved_in_meaning_field(self, parser):
        """individual_meaning must be incorporated into the meaning field as a rich explanation."""
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "The cat eats fish."
        )
        # Find 'eats' entry
        eats_entry = next(
            (item for item in result["word_explanations"] if item["word"] == "eats"),
            None,
        )
        assert eats_entry is not None, "Expected 'eats' in word_explanations"
        meaning = eats_entry["meaning"]
        # The meaning field should contain the rich explanation, not just the word
        assert len(meaning) > 30, f"Expected rich meaning for 'eats', got: {meaning!r}"
        # It should include the word and role as prefix
        assert "eats" in meaning

    def test_grammatical_role_key_accepted(self, parser):
        """Parser must accept 'grammatical_role' key from model (not only 'role')."""
        # Build a minimal JSON with 'grammatical_role' (as the schema specifies)
        response = json.dumps({
            "sentence": "Cats run.",
            "overall_structure": "SV",
            "sentence_structure": "SV",
            "word_explanations": [
                {
                    "word": "Cats",
                    "grammatical_role": "noun",
                    "color": "#FFAA00",
                    "individual_meaning": "Plural common noun, subject of 'run'. English nouns add -s for the regular plural.",
                    "number": "plural",
                }
            ],
            "grammar_notes": "Simple SV.",
            "confidence": 0.9,
        })
        result = parser.parse_response(response, "beginner", "Cats run.")
        assert len(result["word_explanations"]) > 0
        assert result["word_explanations"][0]["role"] == "noun"

    def test_prefix_stripping_if_model_doubles_prefix(self, parser):
        """Parser must not double-prefix if model includes '{word} ({role}):' in individual_meaning."""
        response = json.dumps({
            "sentence": "Cats run.",
            "overall_structure": "SV",
            "sentence_structure": "SV",
            "word_explanations": [
                {
                    "word": "Cats",
                    "grammatical_role": "noun",
                    "color": "#FFAA00",
                    # Model already added the prefix inside individual_meaning
                    "individual_meaning": "Cats (noun): Plural common noun, subject of 'run'. English nouns add -s for plural.",
                    "number": "plural",
                }
            ],
            "grammar_notes": "SV.",
            "confidence": 0.9,
        })
        result = parser.parse_response(response, "beginner", "Cats run.")
        entry = result["word_explanations"][0]
        # After stripping the prefix, the displayed meaning should NOT double-prefix
        assert "Cats (noun): Cats (noun):" not in entry["meaning"], (
            f"Double prefix detected in meaning: {entry['meaning']!r}"
        )

    def test_legacy_meaning_field_fallback(self, parser):
        """When individual_meaning is absent, parser falls back gracefully to 'meaning'."""
        response = json.dumps({
            "sentence": "Cats run.",
            "overall_structure": "SV",
            "sentence_structure": "SV",
            "word_explanations": [
                {
                    "word": "Cats",
                    "role": "noun",
                    "color": "#FFAA00",
                    # No individual_meaning — only legacy 'meaning'
                    "meaning": "Plural noun, subject of 'run', formed by adding -s to 'cat'.",
                }
            ],
            "grammar_notes": "SV.",
            "confidence": 0.85,
        })
        result = parser.parse_response(response, "beginner", "Cats run.")
        assert len(result["word_explanations"]) > 0
        assert result["word_explanations"][0]["word"] == "Cats"

    def test_batch_response_fallback_for_extra_sentences(self, parser):
        """If AI returns fewer items than input sentences, remaining use fallback."""
        # One-item response for two sentences
        batch = f"[{SAMPLE_BEGINNER_RESPONSE}]"
        sentences = ["The cat eats fish.", "She reads a book."]
        results = parser.parse_batch_response(batch, sentences, "beginner")
        assert len(results) == 2
        # Second item should be fallback but still valid
        assert "word_explanations" in results[1]
