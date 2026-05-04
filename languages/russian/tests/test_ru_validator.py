# languages/russian/tests/test_ru_validator.py
"""
Tests for RuValidator (Russian validation component).
"""
import json
import pytest
from languages.russian.domain.ru_config import RuConfig
from languages.russian.domain.ru_validator import RuValidator
from .conftest import (
    SAMPLE_BEGINNER_RESPONSE,
    SAMPLE_INTERMEDIATE_RESPONSE,
    SAMPLE_ADVANCED_RESPONSE,
)


@pytest.fixture
def validator():
    return RuValidator(RuConfig())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_word_entry(
    word, role, color="#FFAA00",
    meaning=None, individual_meaning=None,
    case="", gender="", number="", aspect="", tense=""
):
    if meaning is None:
        # Rich meaning format
        body = individual_meaning or f"Detailed grammatical explanation for {word} in {role} role, with case and aspect information."
        meaning = f"{word} ({role}): {body}"
    return {
        "word": word,
        "role": role,
        "color": color,
        "meaning": meaning,
        "individual_meaning": individual_meaning or "",
        "case": case,
        "gender": gender,
        "number": number,
        "aspect": aspect,
        "tense": tense,
    }


def _parse_sample(validator, sample_json, sentence):
    """Parse a sample JSON string and run validate_result."""
    import json
    from languages.russian.domain.ru_config import RuConfig
    from languages.russian.domain.ru_fallbacks import RuFallbacks
    from languages.russian.domain.ru_response_parser import RuResponseParser
    config = RuConfig()
    fallbacks = RuFallbacks(config)
    parser = RuResponseParser(config, fallbacks)
    parsed = parser.parse_response(sample_json, "beginner", sentence)
    return validator.validate_result(parsed, sentence)


# ---------------------------------------------------------------------------
# validate_result — basic contract
# ---------------------------------------------------------------------------

class TestRuValidatorResult:
    def test_validate_result_returns_dict(self, validator):
        result = validator.validate_result(
            {"word_explanations": []}, "Я читаю."
        )
        assert isinstance(result, dict)

    def test_confidence_in_range(self, validator):
        result = _parse_sample(validator, SAMPLE_BEGINNER_RESPONSE, "Я читаю книгу.")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_valid_beginner_response_high_confidence(self, validator):
        result = _parse_sample(validator, SAMPLE_BEGINNER_RESPONSE, "Я читаю книгу.")
        # A well-formed beginner response should have reasonable confidence
        assert result["confidence"] >= 0.5

    def test_valid_advanced_response_confidence(self, validator):
        from languages.russian.domain.ru_config import RuConfig
        from languages.russian.domain.ru_fallbacks import RuFallbacks
        from languages.russian.domain.ru_response_parser import RuResponseParser
        config = RuConfig()
        parser = RuResponseParser(config, RuFallbacks(config))
        parsed = parser.parse_response(
            SAMPLE_ADVANCED_RESPONSE, "advanced",
            "Книга, которую она читала, была интересной."
        )
        result = validator.validate_result(
            parsed, "Книга, которую она читала, была интересной."
        )
        assert 0.0 <= result["confidence"] <= 1.0

    def test_empty_result_low_confidence(self, validator):
        result = validator.validate_result({}, "Я читаю.")
        assert result["confidence"] == 0.0

    def test_none_like_result_low_confidence(self, validator):
        result = validator.validate_result(None, "Я читаю.")
        assert result.get("confidence", 0.0) == 0.0


# ---------------------------------------------------------------------------
# CRITICAL: is_fallback short-circuit
# ---------------------------------------------------------------------------

class TestRuValidatorFallbackShortCircuit:
    def test_is_fallback_caps_confidence_at_0_3(self, validator):
        """CRITICAL: is_fallback=True must short-circuit confidence to ≤ 0.3."""
        fallback_result = {
            "word_explanations": [
                _make_word_entry(
                    "Я", "personal_pronoun",
                    meaning="Я (personal_pronoun): Personal pronoun, 1st-person singular, nominative case. Subject.",
                    case="nominative",
                )
            ],
            "overall_structure": "SVO",
            "sentence_structure": "SVO",
            "grammar_notes": "Test.",
            "confidence": 0.95,  # Would be high — but must be capped
            "is_fallback": True,
        }
        result = validator.validate_result(fallback_result, "Я читаю.")
        assert result["confidence"] <= 0.3, (
            f"is_fallback=True must cap confidence at 0.3, got {result['confidence']}"
        )

    def test_is_fallback_false_does_not_cap(self, validator):
        """is_fallback=False should not force confidence to 0.3."""
        result = _parse_sample(validator, SAMPLE_BEGINNER_RESPONSE, "Я читаю книгу.")
        # A valid AI response should not be capped to 0.3
        assert result["confidence"] > 0.3, (
            f"Valid AI response should not be capped, got confidence={result['confidence']}"
        )


# ---------------------------------------------------------------------------
# validate_explanation_quality
# ---------------------------------------------------------------------------

class TestRuValidatorExplanationQuality:
    def test_quality_report_returns_dict(self, validator):
        from languages.russian.domain.ru_config import RuConfig
        from languages.russian.domain.ru_fallbacks import RuFallbacks
        from languages.russian.domain.ru_response_parser import RuResponseParser
        config = RuConfig()
        parser = RuResponseParser(config, RuFallbacks(config))
        parsed = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Я читаю книгу."
        )
        quality = validator.validate_explanation_quality(parsed)
        assert isinstance(quality, dict)
        assert "quality_score" in quality
        assert "stub_count" in quality

    def test_rich_fixture_quality_score_high(self, validator):
        """Well-formed responses from the canonical fixture should score high."""
        from languages.russian.domain.ru_config import RuConfig
        from languages.russian.domain.ru_fallbacks import RuFallbacks
        from languages.russian.domain.ru_response_parser import RuResponseParser
        config = RuConfig()
        parser = RuResponseParser(config, RuFallbacks(config))
        parsed = parser.parse_response(
            SAMPLE_BEGINNER_RESPONSE, "beginner", "Я читаю книгу."
        )
        quality = validator.validate_explanation_quality(parsed)
        assert quality["quality_score"] >= 0.9, (
            f"Rich fixture should score ≥ 0.9, got: {quality}"
        )
        assert quality["stub_count"] == 0, (
            f"No stubs expected in rich fixture, got: {quality}"
        )

    def test_stub_explanation_flagged(self, validator):
        """An explanation body shorter than 20 chars must be flagged as a stub."""
        stub_result = {
            "word_explanations": [
                {
                    "word": "книга",
                    "role": "noun",
                    "color": "#FFAA00",
                    # Short stub — should be flagged
                    "meaning": "книга (noun): noun",
                    "individual_meaning": "noun",
                }
            ]
        }
        quality = validator.validate_explanation_quality(stub_result)
        assert quality["stub_count"] >= 1, (
            f"Expected at least 1 stub flagged, got: {quality}"
        )

    def test_inflected_word_without_russian_features_flagged(self, validator):
        """An inflected noun without case/gender/number keywords should be flagged."""
        result = {
            "word_explanations": [
                {
                    "word": "книгу",
                    "role": "noun",
                    "color": "#FFAA00",
                    # Long enough (>20 chars) but NO Russian-feature keywords
                    "meaning": "книгу (noun): This is a word that means something important in the sentence.",
                    "individual_meaning": "This is a word that means something important in the sentence.",
                }
            ]
        }
        quality = validator.validate_explanation_quality(result)
        assert quality["feature_gap_count"] >= 1, (
            f"Expected feature gap flagged for inflected noun, got: {quality}"
        )

    def test_inflected_word_with_case_keyword_not_flagged(self, validator):
        """An inflected noun that mentions 'accusative' should pass the feature check."""
        result = {
            "word_explanations": [
                {
                    "word": "книгу",
                    "role": "noun",
                    "color": "#FFAA00",
                    "meaning": "книгу (noun): Accusative singular feminine of книга, direct object of the verb.",
                    "individual_meaning": "Accusative singular feminine of книга, direct object of the verb.",
                }
            ]
        }
        quality = validator.validate_explanation_quality(result)
        assert quality["feature_gap_count"] == 0, (
            f"Noun with 'accusative' should not have feature gaps: {quality}"
        )

    def test_verb_with_aspect_not_flagged(self, validator):
        """A verb entry that mentions 'imperfective' should pass the feature check."""
        result = {
            "word_explanations": [
                {
                    "word": "читаю",
                    "role": "verb",
                    "color": "#4ECDC4",
                    "meaning": "читаю (verb): Imperfective present 1st-person singular of читать, meaning I am reading.",
                    "individual_meaning": "Imperfective present 1st-person singular of читать, meaning I am reading.",
                }
            ]
        }
        quality = validator.validate_explanation_quality(result)
        assert quality["feature_gap_count"] == 0, (
            f"Verb with 'imperfective' should not have feature gaps: {quality}"
        )

    def test_quality_score_in_range(self, validator):
        result = {
            "word_explanations": [
                _make_word_entry(
                    "Я", "personal_pronoun",
                    meaning="Я (personal_pronoun): Personal pronoun, 1st-person singular, nominative case. Subject of the clause.",
                    individual_meaning="Personal pronoun, 1st-person singular, nominative case. Subject of the clause.",
                    case="nominative",
                )
            ]
        }
        quality = validator.validate_explanation_quality(result)
        assert 0.0 <= quality["quality_score"] <= 1.0

    def test_missing_meaning_flagged(self, validator):
        """An entry with no meaning at all must be flagged as an issue."""
        result = {
            "word_explanations": [
                {
                    "word": "книга",
                    "role": "noun",
                    "color": "#FFAA00",
                    "meaning": "",  # Empty meaning
                    "individual_meaning": "",
                }
            ]
        }
        quality = validator.validate_explanation_quality(result)
        assert len(quality["issues"]) >= 1


# ---------------------------------------------------------------------------
# Validate_analysis method (abstract-method compliance)
# ---------------------------------------------------------------------------

class TestRuValidatorAnalysisMethod:
    def test_validate_analysis_returns_float(self, validator):
        score = validator.validate_analysis(
            {"word_explanations": [], "overall_structure": "SVO"},
            "Я читаю."
        )
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
