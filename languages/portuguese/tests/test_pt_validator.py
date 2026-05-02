# languages/portuguese/tests/test_pt_validator.py
"""Tests for PtValidator — confidence scoring for Portuguese analysis."""
import pytest
from languages.portuguese.domain.pt_config import PtConfig
from languages.portuguese.domain.pt_validator import PtValidator


@pytest.fixture
def validator():
    return PtValidator(PtConfig())


# ---------------------------------------------------------------------------
# Helper — builds a well-formed parsed_data dict
# ---------------------------------------------------------------------------

def _make_well_formed_result(words, structure="SVO", register="neutral"):
    """
    Build a result dict that mirrors what PtResponseParser._normalize produces.
    word_explanations is a list-of-lists: [word, role, color, meaning].
    word_details is a list-of-dicts with all meta fields.
    """
    word_explanations = []
    word_details = []
    for w in words:
        word_explanations.append([w["word"], w["role"], w.get("color", "#FFAA00"), w.get("meaning", w["word"])])
        detail = {
            "word": w["word"],
            "grammatical_role": w["role"],
            "role": w["role"],
            "color": w.get("color", "#FFAA00"),
            "meaning": w.get("meaning", w["word"]),
            "gender": w.get("gender", ""),
            "number": w.get("number", ""),
            "person": w.get("person", ""),
            "tense": w.get("tense", ""),
            "mood": w.get("mood", ""),
            "copula_type": w.get("copula_type", ""),
            "clitic_position": w.get("clitic_position", ""),
            "contraction_parts": w.get("contraction_parts", []),
            "register": w.get("register", ""),
            "is_target": False,
        }
        word_details.append(detail)
    return {
        "word_explanations": word_explanations,
        "word_details": word_details,
        "overall_structure": structure,
        "sentence_structure": structure,
        "register": register,
    }


class TestPtValidatorBasic:
    def test_empty_result_low_confidence(self, validator):
        result = validator.validate_result({}, "O gato dorme.")
        assert result.get("confidence", 1.0) < 0.5

    def test_confidence_always_between_0_and_1(self, validator):
        words = [
            {"word": "O", "role": "article", "color": "#AA44FF", "meaning": "the",
             "gender": "masculine", "number": "singular"},
            {"word": "gato", "role": "noun", "color": "#FFAA00", "meaning": "cat",
             "gender": "masculine", "number": "singular"},
        ]
        result = validator.validate_result(_make_well_formed_result(words), "O gato.")
        conf = result["confidence"]
        assert 0.0 <= conf <= 1.0

    def test_validate_analysis_returns_float(self, validator):
        data = {
            "word_explanations": [["gato", "noun", "#FFAA00", "cat"]],
            "overall_structure": "SVO",
        }
        score = validator.validate_analysis(data, "O gato dorme.")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestPtValidatorThreshold:
    # Behavior 5: well-formed data must score >= 0.85
    def test_well_formed_data_meets_production_threshold(self, validator):
        """
        A complete, correct Portuguese analysis with all meta-fields
        must return confidence >= 0.85 (CLAUDE.md production requirement).
        """
        words = [
            {"word": "Ela", "role": "personal_pronoun", "color": "#FF4444",
             "meaning": "she", "gender": "feminine", "number": "singular", "person": "3"},
            {"word": "vai", "role": "auxiliary_verb", "color": "#228B22",
             "meaning": "goes (ir)", "tense": "present", "person": "3", "number": "singular"},
            {"word": "ao", "role": "contraction", "color": "#FF7F50",
             "meaning": "to the (a + o)",
             "contraction_parts": ["a", "o"]},
            {"word": "mercado", "role": "noun", "color": "#FFAA00",
             "meaning": "market", "gender": "masculine", "number": "singular"},
            {"word": "comprar", "role": "verb", "color": "#44FF44",
             "meaning": "to buy (infinitive)"},
            {"word": "pão", "role": "noun", "color": "#FFAA00",
             "meaning": "bread", "gender": "masculine", "number": "singular"},
        ]
        result = validator.validate_result(
            _make_well_formed_result(words, register="neutral"),
            "Ela vai ao mercado comprar pão.",
        )
        assert result["confidence"] >= 0.85, (
            f"Well-formed data scored {result['confidence']:.3f} — "
            "must be >= 0.85 per CLAUDE.md production requirement"
        )

    def test_copula_with_type_boosts_confidence(self, validator):
        """
        A copula entry with copula_type populated should score higher than
        one without it (bonus applies).
        """
        words_good = [
            {"word": "Ela", "role": "personal_pronoun", "color": "#FF4444",
             "meaning": "she", "gender": "feminine"},
            {"word": "é", "role": "copula", "color": "#00B894",
             "meaning": "is (ser)", "copula_type": "ser"},
            {"word": "estudante", "role": "noun", "color": "#FFAA00",
             "meaning": "student", "gender": "feminine"},
        ]
        words_bad = [
            {"word": "Ela", "role": "personal_pronoun", "color": "#FF4444",
             "meaning": "she", "gender": "feminine"},
            {"word": "é", "role": "copula", "color": "#00B894",
             "meaning": "is (ser)", "copula_type": ""},  # missing type
            {"word": "estudante", "role": "noun", "color": "#FFAA00",
             "meaning": "student", "gender": "feminine"},
        ]
        score_good = validator.validate_result(
            _make_well_formed_result(words_good), "Ela é estudante."
        )["confidence"]
        score_bad = validator.validate_result(
            _make_well_formed_result(words_bad), "Ela é estudante."
        )["confidence"]
        assert score_good >= score_bad

    def test_invalid_roles_lower_confidence(self, validator):
        """Unknown/invalid roles should score lower than valid ones."""
        words_valid = [
            {"word": "O", "role": "article", "color": "#AA44FF", "meaning": "the"},
            {"word": "gato", "role": "noun", "color": "#FFAA00", "meaning": "cat",
             "gender": "masculine"},
            {"word": "dorme", "role": "verb", "color": "#44FF44", "meaning": "sleeps"},
        ]
        words_invalid = [
            {"word": "O", "role": "MADE_UP_ROLE", "color": "#AA44FF", "meaning": "the"},
            {"word": "gato", "role": "ANOTHER_BAD", "color": "#FFAA00", "meaning": "cat"},
            {"word": "dorme", "role": "NOT_REAL", "color": "#44FF44", "meaning": "sleeps"},
        ]
        score_valid = validator.validate_result(
            _make_well_formed_result(words_valid), "O gato dorme."
        )["confidence"]
        score_invalid = validator.validate_result(
            _make_well_formed_result(words_invalid), "O gato dorme."
        )["confidence"]
        assert score_valid > score_invalid


class TestPtValidatorExplanationQuality:
    def test_quality_no_issues_on_well_formed(self, validator):
        words = [
            {"word": "gato", "role": "noun", "color": "#FFAA00", "meaning": "cat",
             "gender": "masculine"},
            {"word": "dorme", "role": "verb", "color": "#44FF44", "meaning": "sleeps"},
        ]
        result = _make_well_formed_result(words)
        quality = validator.validate_explanation_quality(result)
        assert quality["quality_score"] >= 0.9
        assert len(quality["issues"]) == 0

    def test_quality_flags_missing_meaning(self, validator):
        """Entries with empty meaning should be flagged."""
        words = [
            {"word": "gato", "role": "noun", "color": "#FFAA00", "meaning": ""},
        ]
        result = _make_well_formed_result(words)
        quality = validator.validate_explanation_quality(result)
        assert len(quality["issues"]) > 0

    def test_quality_flags_missing_color(self, validator):
        """Entries with empty color should be flagged."""
        data = {
            "word_explanations": [["gato", "noun", "", "cat"]],  # empty color
            "word_details": [],
        }
        quality = validator.validate_explanation_quality(data)
        assert len(quality["issues"]) > 0

    def test_quality_flags_unknown_role(self, validator):
        data = {
            "word_explanations": [
                ["gato", "MADE_UP_ROLE_XYZ", "#FFAA00", "cat"]
            ],
            "word_details": [],
        }
        quality = validator.validate_explanation_quality(data)
        assert len(quality["issues"]) > 0

    def test_quality_flags_copula_missing_type(self, validator):
        """A copula word_details entry without copula_type should be flagged."""
        data = {
            "word_explanations": [["é", "copula", "#00B894", "is"]],
            "word_details": [
                {
                    "word": "é",
                    "grammatical_role": "copula",
                    "role": "copula",
                    "color": "#00B894",
                    "meaning": "is",
                    "copula_type": "",  # missing
                    "contraction_parts": [],
                    "clitic_position": "",
                }
            ],
        }
        quality = validator.validate_explanation_quality(data)
        assert len(quality["issues"]) > 0

    def test_quality_flags_contraction_missing_parts(self, validator):
        data = {
            "word_explanations": [["ao", "contraction", "#FF7F50", "to the"]],
            "word_details": [
                {
                    "word": "ao",
                    "grammatical_role": "contraction",
                    "role": "contraction",
                    "color": "#FF7F50",
                    "meaning": "to the",
                    "copula_type": "",
                    "contraction_parts": [],  # missing
                    "clitic_position": "",
                }
            ],
        }
        quality = validator.validate_explanation_quality(data)
        assert len(quality["issues"]) > 0

    def test_quality_flags_clitic_missing_position(self, validator):
        data = {
            "word_explanations": [["me", "clitic_pronoun", "#E91E63", "me"]],
            "word_details": [
                {
                    "word": "me",
                    "grammatical_role": "clitic_pronoun",
                    "role": "clitic_pronoun",
                    "color": "#E91E63",
                    "meaning": "me",
                    "copula_type": "",
                    "contraction_parts": [],
                    "clitic_position": "",  # missing
                }
            ],
        }
        quality = validator.validate_explanation_quality(data)
        assert len(quality["issues"]) > 0

    def test_quality_returns_recommendations(self, validator):
        quality = validator.validate_explanation_quality({})
        assert "recommendations" in quality
        assert isinstance(quality["recommendations"], list)


class TestPtValidatorValidateResult:
    def test_validate_result_sets_confidence_key(self, validator):
        words = [
            {"word": "gato", "role": "noun", "color": "#FFAA00", "meaning": "cat",
             "gender": "masculine"},
        ]
        result = validator.validate_result(
            _make_well_formed_result(words), "O gato."
        )
        assert "confidence" in result
        assert isinstance(result["confidence"], float)

    def test_validate_analysis_scalar_equals_validate_result(self, validator):
        data = {
            "word_explanations": [["gato", "noun", "#FFAA00", "cat"]],
            "word_details": [],
            "overall_structure": "SVO",
        }
        result_conf = validator.validate_result(dict(data), "gato.")["confidence"]
        scalar_conf = validator.validate_analysis(dict(data), "gato.")
        assert abs(result_conf - scalar_conf) < 0.001
