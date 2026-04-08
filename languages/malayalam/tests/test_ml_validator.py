"""Malayalam validator tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.malayalam.domain.ml_config import MlConfig
from languages.malayalam.domain.ml_validator import MlValidator


def test_validator_creation():
    config = MlConfig()
    validator = MlValidator(config)
    assert validator is not None


def test_validate_result_returns_dict():
    config = MlConfig()
    validator = MlValidator(config)

    result = {
        "word_explanations": [
            ["ഞാൻ", "pronoun", "#4FC3F7", "I (first person singular)"],
            ["വെള്ളം", "noun", "#FFAA00", "water (direct object)"],
            ["കുടിക്കുന്നു", "verb", "#44FF44", "drink (present tense)"],
        ],
        "html_output": "<div>test</div>",
        "confidence": 0.8,
        "elements": {},
        "explanations": {}
    }

    validated = validator.validate_result(result, "ഞാൻ വെള്ളം കുടിക്കുന്നു")
    assert isinstance(validated, dict)
    assert 'confidence' in validated
    assert isinstance(validated['confidence'], float)
    assert 0.0 <= validated['confidence'] <= 1.0


def test_confidence_with_good_coverage():
    config = MlConfig()
    validator = MlValidator(config)

    result = {
        "word_explanations": [
            ["ഞാൻ", "pronoun", "#4FC3F7", "I"],
            ["വെള്ളം", "noun", "#FFAA00", "water"],
            ["കുടിക്കുന്നു", "verb", "#44FF44", "drink (present tense)"],
        ],
        "elements": {},
        "explanations": {},
        "confidence": 0.7
    }

    validated = validator.validate_result(result, "ഞാൻ വെള്ളം കുടിക്കുന്നു")
    # Full coverage with verb and noun should give decent confidence
    assert validated['confidence'] >= 0.5


def test_confidence_with_no_explanations():
    config = MlConfig()
    validator = MlValidator(config)

    result = {
        "word_explanations": [],
        "elements": {},
        "explanations": {},
        "confidence": 0.0
    }

    validated = validator.validate_result(result, "ടെസ്റ്റ് വാക്യം")
    assert validated['confidence'] < 0.5


def test_validate_explanation_quality():
    config = MlConfig()
    validator = MlValidator(config)

    result = {
        "word_explanations": [
            ["കുടിക്കുന്നു", "verb", "#44FF44", "drink (present tense, habitual/continuous)"],
            ["വെള്ളം", "noun", "#FFAA00", "water (accusative case, direct object)"],
        ],
        "explanations": {
            "overall_structure": "Basic SOV sentence with pronoun subject and present tense verb",
            "key_features": "Agglutinative verb form with present tense suffix"
        }
    }

    quality = validator.validate_explanation_quality(result)
    assert isinstance(quality, dict)
    assert 'quality_score' in quality
    assert 0.0 <= quality['quality_score'] <= 1.0


def test_high_confidence_with_valid_patterns():
    config = MlConfig()
    validator = MlValidator(config)

    result = {
        "word_explanations": [
            ["കുട്ടികൾ", "noun", "#FFAA00", "children (nominative, plural)"],
            ["സ്കൂളിൽ", "noun", "#FFAA00", "in school (locative case suffix -ഇൽ)"],
            ["പുസ്തകം", "noun", "#FFAA00", "book (accusative, direct object)"],
            ["വായിക്കുന്നു", "verb", "#44FF44", "read (present tense, habitual)"],
        ],
        "elements": {},
        "explanations": {
            "overall_structure": "SOV sentence with locative case"
        },
        "confidence": 0.8
    }

    validated = validator.validate_result(result, "കുട്ടികൾ സ്കൂളിൽ പുസ്തകം വായിക്കുന്നു")
    assert validated['confidence'] >= 0.85
