# languages/latvian/tests/test_lv_validator.py
"""Tests for LvValidator."""
import pytest
from languages.latvian.domain.lv_config import LvConfig
from languages.latvian.domain.lv_validator import LvValidator


@pytest.fixture
def validator():
    return LvValidator(LvConfig())


def _make_result(words, confidence=None, structure="S-V-O"):
    result = {
        "word_explanations": words,
        "overall_structure": structure,
        "sentence_structure": structure,
    }
    if confidence is not None:
        result["confidence"] = confidence
    return result


class TestLvValidator:
    def test_empty_result_low_confidence(self, validator):
        result = validator.validate_result({}, "Es runāju.")
        assert result.get("confidence", 0) < 0.5

    def test_complete_result_high_confidence(self, validator):
        words = [
            {"word": "Es", "role": "personal_pronoun", "color": "#9370DB",
             "meaning": "I", "case": "nominative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
            {"word": "runāju", "role": "verb", "color": "#4ECDC4",
             "meaning": "speak", "case": "", "gender": "", "number": "singular", "tense": "present", "definite_form": ""},
            {"word": "latviski", "role": "adverb", "color": "#FF6347",
             "meaning": "in Latvian", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
        ]
        result = validator.validate_result(
            _make_result(words), "Es runāju latviski."
        )
        assert result["confidence"] >= 0.7

    def test_confidence_between_0_and_1(self, validator):
        words = [
            {"word": "māja", "role": "noun", "color": "#FFAA00",
             "meaning": "house", "case": "nominative", "gender": "feminine", "number": "singular", "tense": "", "definite_form": ""},
        ]
        result = validator.validate_result(_make_result(words), "māja.")
        conf = result["confidence"]
        assert 0.0 <= conf <= 1.0

    def test_invalid_roles_lower_confidence(self, validator):
        words = [
            {"word": "Es", "role": "INVALID_ROLE", "color": "#9370DB",
             "meaning": "I", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
            {"word": "iet", "role": "ANOTHER_BAD", "color": "#4ECDC4",
             "meaning": "go", "case": "", "gender": "", "number": "", "tense": "", "definite_form": ""},
        ]
        result = validator.validate_result(_make_result(words), "Es iet.")
        result2 = validator.validate_result(
            _make_result([
                {"word": "Es", "role": "personal_pronoun", "color": "#9370DB",
                 "meaning": "I", "case": "nominative", "gender": "", "number": "singular", "tense": "", "definite_form": ""},
                {"word": "iet", "role": "verb", "color": "#4ECDC4",
                 "meaning": "go", "case": "", "gender": "", "number": "", "tense": "present", "definite_form": ""},
            ]),
            "Es iet."
        )
        assert result["confidence"] < result2["confidence"]

    def test_validate_analysis_returns_float(self, validator):
        score = validator.validate_analysis(
            {"word_explanations": [
                {"word": "Es", "role": "pronoun", "color": "#9370DB",
                 "meaning": "I", "case": "nominative", "gender": "", "number": "singular", "tense": "", "definite_form": ""}
            ], "overall_structure": "SVO"},
            "Es runāju."
        )
        assert isinstance(score, float)

    def test_explanation_quality_no_issues(self, validator):
        words = [
            {"word": "Es", "role": "personal_pronoun", "color": "#9370DB",
             "meaning": "I"},
            {"word": "runāju", "role": "verb", "color": "#4ECDC4",
             "meaning": "speak"},
        ]
        quality = validator.validate_explanation_quality({"word_explanations": words})
        assert quality["quality_score"] >= 0.9
        assert len(quality["issues"]) == 0

    def test_explanation_quality_flags_missing_meaning(self, validator):
        words = [
            {"word": "Es", "role": "personal_pronoun", "color": "#9370DB", "meaning": ""},
        ]
        quality = validator.validate_explanation_quality({"word_explanations": words})
        assert len(quality["issues"]) > 0
