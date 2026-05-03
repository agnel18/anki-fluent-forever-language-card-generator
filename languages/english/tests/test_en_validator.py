# languages/english/tests/test_en_validator.py
"""Tests for EnValidator."""
import pytest
from languages.english.domain.en_config import EnConfig
from languages.english.domain.en_validator import EnValidator


@pytest.fixture
def validator():
    return EnValidator(EnConfig())


def _make_result(words, confidence=None, structure="Subject-Verb-Object"):
    result = {
        "word_explanations": words,
        "overall_structure": structure,
        "sentence_structure": structure,
    }
    if confidence is not None:
        result["confidence"] = confidence
    return result


class TestEnValidator:
    def test_empty_result_low_confidence(self, validator):
        result = validator.validate_result({}, "The cat eats fish.")
        assert result.get("confidence", 0) < 0.5

    def test_complete_result_high_confidence(self, validator):
        words = [
            {"word": "The", "role": "article", "color": "#FFD700",
             "meaning": "The (article): Definite article marking 'cat' as a specific noun.",
             "individual_meaning": "Definite article marking 'cat' as a specific noun.",
             "number": "", "tense": "", "case": ""},
            {"word": "cat", "role": "noun", "color": "#FFAA00",
             "meaning": "cat (noun): Singular common noun functioning as grammatical subject.",
             "individual_meaning": "Singular common noun functioning as grammatical subject.",
             "number": "singular", "tense": "", "case": ""},
            {"word": "eats", "role": "verb", "color": "#4ECDC4",
             "meaning": "eats (verb): 3rd-person singular simple present tense of 'eat', agreeing with subject 'cat'.",
             "individual_meaning": "3rd-person singular simple present tense of 'eat', agreeing with subject 'cat'.",
             "number": "singular", "tense": "present", "aspect": "simple", "voice": "active",
             "person": "3", "case": ""},
        ]
        result = validator.validate_result(
            _make_result(words), "The cat eats fish."
        )
        assert result["confidence"] >= 0.7

    def test_confidence_between_0_and_1(self, validator):
        words = [
            {"word": "fish", "role": "noun", "color": "#FFAA00",
             "meaning": "fish (noun): Common noun functioning as direct object of 'eats'.",
             "individual_meaning": "Common noun functioning as direct object of 'eats'.",
             "number": "singular", "tense": "", "case": ""},
        ]
        result = validator.validate_result(_make_result(words), "fish.")
        conf = result["confidence"]
        assert 0.0 <= conf <= 1.0

    def test_invalid_roles_lower_confidence(self, validator):
        words_bad = [
            {"word": "The", "role": "INVALID_ROLE", "color": "#FFD700",
             "meaning": "The (INVALID_ROLE): Definite article.", "individual_meaning": "Definite article."},
            {"word": "cat", "role": "ANOTHER_BAD", "color": "#FFAA00",
             "meaning": "cat (ANOTHER_BAD): Noun.", "individual_meaning": "Noun."},
        ]
        words_good = [
            {"word": "The", "role": "article", "color": "#FFD700",
             "meaning": "The (article): Definite article marking a specific noun.",
             "individual_meaning": "Definite article marking a specific noun.",
             "case": "", "tense": ""},
            {"word": "cat", "role": "noun", "color": "#FFAA00",
             "meaning": "cat (noun): Singular noun, subject of the clause.",
             "individual_meaning": "Singular noun, subject of the clause.",
             "number": "singular", "tense": "", "case": ""},
        ]
        result_bad = validator.validate_result(_make_result(words_bad), "The cat.")
        result_good = validator.validate_result(_make_result(words_good), "The cat.")
        assert result_bad["confidence"] < result_good["confidence"]

    def test_is_fallback_hard_caps_confidence(self, validator):
        """CRITICAL: is_fallback: True must cap confidence at 0.3 regardless of content."""
        words = [
            {"word": "The", "role": "article", "color": "#FFD700",
             "meaning": "The (article): Definite article; marks the following noun 'cat' as specific and previously-mentioned or uniquely identifiable. Closed-class word.",
             "individual_meaning": "Definite article; marks the following noun 'cat' as specific and previously-mentioned or uniquely identifiable. Closed-class word.",
             "case": "", "tense": ""},
            {"word": "cat", "role": "noun", "color": "#FFAA00",
             "meaning": "cat (noun): Singular count noun, functions as subject of the predicate 'eats'. English nouns are uninflected for case.",
             "individual_meaning": "Singular count noun, functions as subject of the predicate 'eats'. English nouns are uninflected for case.",
             "number": "singular", "tense": "", "case": ""},
            {"word": "eats", "role": "verb", "color": "#4ECDC4",
             "meaning": "eats (verb): 3rd-person singular simple present tense of lexical verb 'eat', marked by the -s agreement ending.",
             "individual_meaning": "3rd-person singular simple present tense of lexical verb 'eat', marked by the -s agreement ending.",
             "number": "singular", "tense": "present", "aspect": "simple", "person": "3"},
        ]
        # Even with rich explanations, is_fallback: True must keep confidence <= 0.3
        result = validator.validate_result(
            {
                "word_explanations": words,
                "overall_structure": "SVO",
                "sentence_structure": "SVO",
                "is_fallback": True,
                "confidence": 0.9,  # caller sets high — must be overridden
            },
            "The cat eats fish."
        )
        assert result["confidence"] <= 0.3, (
            f"is_fallback=True should cap confidence at 0.3, got {result['confidence']}"
        )

    def test_validate_analysis_returns_float(self, validator):
        score = validator.validate_analysis(
            {"word_explanations": [
                {"word": "cat", "role": "noun", "color": "#FFAA00",
                 "meaning": "cat (noun): Singular common noun, subject of the clause.",
                 "individual_meaning": "Singular common noun, subject of the clause.",
                 "number": "singular"},
            ], "overall_structure": "SVO"},
            "The cat eats."
        )
        assert isinstance(score, float)

    def test_explanation_quality_no_issues(self, validator):
        """Rich explanations mentioning tense/agreement/case should score ≥ 0.9."""
        words = [
            {
                "word": "I",
                "role": "personal_pronoun",
                "color": "#9370DB",
                "meaning": "I (personal_pronoun): 1st-person singular subject pronoun, nominative case, subject of 'want'.",
                "individual_meaning": "1st-person singular subject pronoun, nominative case, subject of 'want'.",
                "case": "nominative", "number": "singular", "person": "1",
            },
            {
                "word": "want",
                "role": "verb",
                "color": "#4ECDC4",
                "meaning": "want (verb): Lexical verb in 1st-person singular simple present tense; no -s ending because subject is 1st person, not 3rd-person singular. Catenative verb taking infinitival complement.",
                "individual_meaning": "Lexical verb in 1st-person singular simple present tense; no -s ending because subject is 1st person, not 3rd-person singular. Catenative verb taking infinitival complement.",
                "tense": "present", "aspect": "simple", "person": "1", "number": "singular",
            },
        ]
        quality = validator.validate_explanation_quality({"word_explanations": words})
        assert quality["quality_score"] >= 0.9
        assert len(quality["issues"]) == 0

    def test_explanation_quality_flags_stub_explanations(self, validator):
        """Explanations shorter than 20 chars (body) should be flagged as stubs."""
        words = [
            {"word": "cat", "role": "noun", "color": "#FFAA00", "meaning": ""},
        ]
        quality = validator.validate_explanation_quality({"word_explanations": words})
        assert len(quality["issues"]) > 0

    def test_explanation_quality_flags_missing_meaning(self, validator):
        words = [
            {"word": "cat", "role": "noun", "color": "#FFAA00", "meaning": ""},
        ]
        quality = validator.validate_explanation_quality({"word_explanations": words})
        assert len(quality["issues"]) > 0

    def test_explanation_quality_flags_missing_english_feature_on_verb(self, validator):
        """A verb entry with no tense/aspect/agreement info should get penalised."""
        words = [
            {
                "word": "eats",
                "role": "verb",
                "color": "#4ECDC4",
                # Body deliberately lacks any feature keyword
                "meaning": "eats (verb): Refers to the consumption action in the sentence.",
                "individual_meaning": "Refers to the consumption action in the sentence.",
                "tense": "", "aspect": "", "person": "", "number": "",
            },
        ]
        quality = validator.validate_explanation_quality({"word_explanations": words})
        # Should flag the feature gap
        assert quality["feature_gap_count"] >= 1 or len(quality["issues"]) > 0

    def test_explanation_quality_score_range(self, validator):
        words = [
            {"word": "cat", "role": "noun", "color": "#FFAA00",
             "meaning": "cat (noun): Singular count noun in subject position. English nouns are uninflected for case.",
             "individual_meaning": "Singular count noun in subject position. English nouns are uninflected for case.",
             "number": "singular"},
        ]
        quality = validator.validate_explanation_quality({"word_explanations": words})
        assert 0.0 <= quality["quality_score"] <= 1.0

    def test_stub_count_zero_for_rich_explanations(self, validator):
        words = [
            {
                "word": "runs",
                "role": "verb",
                "color": "#4ECDC4",
                "meaning": "runs (verb): 3rd-person singular simple present tense of 'run'; the -s morpheme marks 3sg agreement with the subject.",
                "individual_meaning": "3rd-person singular simple present tense of 'run'; the -s morpheme marks 3sg agreement with the subject.",
                "tense": "present", "aspect": "simple", "person": "3", "number": "singular",
            },
        ]
        quality = validator.validate_explanation_quality({"word_explanations": words})
        assert quality["stub_count"] == 0
