# languages/latvian/tests/test_lv_response_parser.py
"""Tests for LvResponseParser."""
import json
import pytest
from languages.latvian.domain.lv_config import LvConfig
from languages.latvian.domain.lv_fallbacks import LvFallbacks
from languages.latvian.domain.lv_response_parser import LvResponseParser
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
)


@pytest.fixture
def parser():
    cfg = LvConfig()
    fb = LvFallbacks(cfg)
    return LvResponseParser(cfg, fb)


class TestLvResponseParser:
    def test_parse_valid_json(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Es runāju latviski."
        )
        assert "word_explanations" in result
        assert len(result["word_explanations"]) > 0

    def test_parse_returns_confidence(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Es runāju latviski."
        )
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_parse_word_explanations_structure(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Es runāju latviski."
        )
        for item in result["word_explanations"]:
            assert "word" in item
            assert "role" in item
            assert "color" in item
            assert "meaning" in item

    def test_parse_markdown_json(self, parser):
        md_response = f"```json\n{SAMPLE_BEGINNER_RESPONSE}\n```"
        result = parser.parse_response(md_response, "beginner", "Es runāju latviski.")
        assert "word_explanations" in result
        assert len(result["word_explanations"]) > 0

    def test_empty_response_uses_fallback(self, parser):
        result = parser.parse_response("", "beginner", "Es runāju.")
        assert "word_explanations" in result
        # Fallback confidence is lower
        assert result["confidence"] < 0.5

    def test_invalid_json_uses_fallback(self, parser):
        result = parser.parse_response("NOT JSON AT ALL", "beginner", "Es runāju.")
        assert "word_explanations" in result

    def test_parse_batch_response(self, parser):
        batch = f"[{SAMPLE_BEGINNER_RESPONSE}, {SAMPLE_INTERMEDIATE_RESPONSE}]"
        results = parser.parse_batch_response(
            batch,
            ["Es runāju latviski.", "Man jāmācās latviešu valoda."],
            "intermediate",
        )
        assert len(results) == 2
        for r in results:
            assert "word_explanations" in r

    def test_batch_empty_response_fallback(self, parser):
        sentences = ["Es runāju.", "Viņš iet."]
        results = parser.parse_batch_response("", sentences, "beginner")
        assert len(results) == 2
        for r in results:
            assert r["confidence"] < 0.5

    def test_intermediate_response_has_debitive(self, parser):
        result = parser.parse_response(
            SAMPLE_INTERMEDIATE_RESPONSE,
            "intermediate",
            "Man jāmācās latviešu valoda.",
        )
        roles = [item["role"] for item in result["word_explanations"]]
        assert "debitive" in roles

    def test_advanced_response_has_participle(self, parser):
        result = parser.parse_response(
            SAMPLE_ADVANCED_RESPONSE,
            "advanced",
            "Uzrakstītā vēstule tika nosūtīta vakar.",
        )
        roles = [item["role"] for item in result["word_explanations"]]
        assert "participle" in roles

    def test_both_structure_keys_present(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Es runāju latviski."
        )
        assert "overall_structure" in result
        assert "sentence_structure" in result
