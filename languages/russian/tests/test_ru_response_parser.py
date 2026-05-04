# languages/russian/tests/test_ru_response_parser.py
"""
Tests for RuResponseParser (Russian response parsing).
"""
import json
import pytest
from languages.russian.domain.ru_config import RuConfig
from languages.russian.domain.ru_fallbacks import RuFallbacks
from languages.russian.domain.ru_response_parser import RuResponseParser
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
)


@pytest.fixture
def parser():
    config = RuConfig()
    fallbacks = RuFallbacks(config)
    return RuResponseParser(config, fallbacks)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wrap_markdown(json_str: str) -> str:
    return f"```json\n{json_str}\n```"


def _wrap_plain_code(json_str: str) -> str:
    return f"```\n{json_str}\n```"


# ---------------------------------------------------------------------------
# Level 1 — Direct JSON parsing
# ---------------------------------------------------------------------------

class TestRuResponseParserDirectJson:
    def test_parse_beginner_response(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Я читаю книгу."
        )
        assert isinstance(result, dict)
        assert "word_explanations" in result
        assert len(result["word_explanations"]) > 0

    def test_parse_intermediate_response(self, parser):
        result = parser.parse_response(
            SAMPLE_INTERMEDIATE_RESPONSE, "intermediate", "Мне нужно написать письмо."
        )
        assert isinstance(result, dict)
        assert len(result["word_explanations"]) > 0

    def test_parse_advanced_response(self, parser):
        result = parser.parse_response(
            SAMPLE_ADVANCED_RESPONSE, "advanced",
            "Книга, которую она читала, была интересной."
        )
        assert isinstance(result, dict)
        assert len(result["word_explanations"]) > 0

    def test_individual_meaning_preserved_in_meaning(self, parser):
        """The individual_meaning field should be incorporated into the displayed meaning."""
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Я читаю книгу."
        )
        # Find the entry for "Я"
        ya_items = [
            item for item in result["word_explanations"]
            if item.get("word") == "Я"
        ]
        assert ya_items, "No entry for 'Я' found"
        meaning = ya_items[0].get("meaning", "")
        # Should follow the "{word} ({role}): {individual_meaning}" contract
        assert "Я" in meaning
        assert "personal_pronoun" in meaning.lower() or "pronoun" in meaning.lower()

    def test_individual_meaning_format_contract(self, parser):
        """Every word entry meaning must follow '{word} ({role}): {explanation}'."""
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Я читаю книгу."
        )
        for item in result["word_explanations"]:
            word = item.get("word", "")
            role = item.get("role", "")
            meaning = item.get("meaning", "")
            if word and role and word not in (".", ","):
                expected_prefix = f"{word} ({role}):"
                assert meaning.startswith(expected_prefix), (
                    f"Meaning for '{word}' does not start with '{expected_prefix}': {meaning!r}"
                )

    def test_cyrillic_content_preserved(self, parser):
        """Cyrillic characters in word and meaning fields must survive normalization."""
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Я читаю книгу."
        )
        words = [item["word"] for item in result["word_explanations"]]
        # At least some Cyrillic words should be present
        cyrillic_words = [w for w in words if any("Ѐ" <= c <= "ӿ" for c in w)]
        assert len(cyrillic_words) >= 2, (
            f"Expected Cyrillic words preserved, got: {words}"
        )

    def test_confidence_from_response(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Я читаю книгу."
        )
        confidence = result.get("confidence", 0.0)
        assert 0.0 <= confidence <= 1.0

    def test_overall_structure_present(self, parser):
        result = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Я читаю книгу."
        )
        assert result.get("overall_structure") or result.get("sentence_structure")


# ---------------------------------------------------------------------------
# Level 2 — Markdown-wrapped JSON
# ---------------------------------------------------------------------------

class TestRuResponseParserMarkdown:
    def test_parse_markdown_json_block(self, parser):
        wrapped = _wrap_markdown(SAMPLE_BEGINNER_RESPONSE)
        result = parser.parse_response(wrapped, "beginner", "Я читаю книгу.")
        assert isinstance(result, dict)
        assert len(result["word_explanations"]) > 0

    def test_parse_plain_code_block(self, parser):
        wrapped = _wrap_plain_code(SAMPLE_BEGINNER_RESPONSE)
        result = parser.parse_response(wrapped, "beginner", "Я читаю книгу.")
        assert isinstance(result, dict)
        assert len(result["word_explanations"]) > 0


# ---------------------------------------------------------------------------
# Level 5 — Fallback on empty / garbage input
# ---------------------------------------------------------------------------

class TestRuResponseParserFallback:
    def test_empty_response_returns_fallback(self, parser):
        result = parser.parse_response("", "beginner", "Я читаю.")
        assert isinstance(result, dict)
        assert "word_explanations" in result
        assert len(result["word_explanations"]) > 0

    def test_garbage_response_returns_fallback(self, parser):
        result = parser.parse_response(
            "This is not JSON at all, just random text!",
            "beginner", "Я читаю."
        )
        assert isinstance(result, dict)
        assert "word_explanations" in result

    def test_none_like_empty_response(self, parser):
        result = parser.parse_response("   \n  ", "beginner", "Я читаю.")
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Prefix-stripping — model may add its own prefix
# ---------------------------------------------------------------------------

class TestRuResponseParserPrefixStripping:
    def test_strips_duplicate_prefix(self, parser):
        """If the model already prefixed with '{word} ({role}):', strip it once."""
        data = {
            "sentence": "Я читаю.",
            "overall_structure": "SVO",
            "sentence_structure": "SVO",
            "word_explanations": [
                {
                    "word": "Я",
                    "grammatical_role": "personal_pronoun",
                    "color": "#9370DB",
                    # Model already added the prefix — parser must not double-prefix
                    "individual_meaning": "Я (personal_pronoun): Personal pronoun, 1st-person singular, nominative case.",
                    "case": "nominative",
                    "gender": "",
                    "number": "singular",
                    "aspect": "",
                    "tense": "",
                    "lemma": "я",
                }
            ],
            "grammar_notes": "Test.",
            "confidence": 0.85,
        }
        result = parser.parse_response(
            json.dumps(data, ensure_ascii=False), "beginner", "Я читаю."
        )
        ya_items = [
            item for item in result["word_explanations"] if item.get("word") == "Я"
        ]
        assert ya_items
        meaning = ya_items[0]["meaning"]
        # The prefix should appear exactly once, not twice
        assert meaning.count("Я (personal_pronoun):") == 1, (
            f"Prefix appeared multiple times in: {meaning!r}"
        )


# ---------------------------------------------------------------------------
# Legacy meaning field fallback
# ---------------------------------------------------------------------------

class TestRuResponseParserLegacyMeaning:
    def test_legacy_meaning_field_falls_back_gracefully(self, parser):
        """A response with only 'meaning' (no 'individual_meaning') still parses."""
        data = {
            "sentence": "Я читаю.",
            "overall_structure": "SVO",
            "sentence_structure": "SVO",
            "word_explanations": [
                {
                    "word": "Я",
                    "grammatical_role": "personal_pronoun",
                    "color": "#9370DB",
                    "meaning": "Personal pronoun I, nominative singular, subject of the clause.",
                    "case": "nominative",
                    "number": "singular",
                    "lemma": "я",
                }
            ],
            "grammar_notes": "Test.",
            "confidence": 0.8,
        }
        result = parser.parse_response(
            json.dumps(data, ensure_ascii=False), "beginner", "Я читаю."
        )
        assert len(result["word_explanations"]) > 0
        ya_item = next(
            (item for item in result["word_explanations"] if item.get("word") == "Я"),
            None
        )
        assert ya_item is not None
        assert ya_item["meaning"]


# ---------------------------------------------------------------------------
# Batch parsing
# ---------------------------------------------------------------------------

class TestRuResponseParserBatch:
    def test_batch_parse_returns_correct_count(self, parser):
        sentences = [
            "Я читаю книгу.",
            "Она пишет письмо.",
            "Мы идём домой.",
        ]
        batch_json = json.dumps(
            [json.loads(SAMPLE_BEGINNER_RESPONSE)] * 3,
            ensure_ascii=False
        )
        results = parser.parse_batch_response(batch_json, sentences, "beginner")
        assert len(results) == 3
        for r in results:
            assert isinstance(r, dict)
            assert "word_explanations" in r

    def test_batch_parse_two_sentences(self, parser):
        sentences = ["Я читаю.", "Она пишет."]
        batch_json = json.dumps(
            [json.loads(SAMPLE_BEGINNER_RESPONSE)] * 2,
            ensure_ascii=False
        )
        results = parser.parse_batch_response(batch_json, sentences, "beginner")
        assert len(results) == 2

    def test_batch_parse_fallback_on_empty(self, parser):
        sentences = ["Я читаю.", "Она пишет."]
        results = parser.parse_batch_response("", sentences, "beginner")
        assert len(results) == 2
        for r in results:
            assert "word_explanations" in r

    def test_batch_parse_fallback_on_garbage(self, parser):
        sentences = ["Я читаю.", "Она пишет."]
        results = parser.parse_batch_response("garbage text", sentences, "beginner")
        assert len(results) == 2

    def test_batch_parse_single_object_as_length_one(self, parser):
        """A single JSON object (not array) is treated as a length-1 batch."""
        sentences = ["Я читаю книгу."]
        results = parser.parse_batch_response(
            SAMPLE_BEGINNER_RESPONSE, sentences, "beginner"
        )
        assert len(results) == 1


# ---------------------------------------------------------------------------
# Normalization — grammatical_role vs role key
# ---------------------------------------------------------------------------

class TestRuResponseParserNormalization:
    def test_grammatical_role_key_accepted(self, parser):
        """The parser must accept 'grammatical_role' (the AI schema key) as well as 'role'."""
        data = {
            "sentence": "Я читаю.",
            "overall_structure": "SVO",
            "sentence_structure": "SVO",
            "word_explanations": [
                {
                    "word": "Я",
                    "grammatical_role": "personal_pronoun",  # AI uses 'grammatical_role'
                    "color": "#9370DB",
                    "individual_meaning": "Personal pronoun, nominative singular, subject.",
                    "case": "nominative",
                    "number": "singular",
                }
            ],
            "grammar_notes": "Test.",
            "confidence": 0.85,
        }
        result = parser.parse_response(
            json.dumps(data, ensure_ascii=False), "beginner", "Я читаю."
        )
        ya_item = next(
            (item for item in result["word_explanations"] if item.get("word") == "Я"),
            None
        )
        assert ya_item is not None
        assert ya_item["role"] == "personal_pronoun"
