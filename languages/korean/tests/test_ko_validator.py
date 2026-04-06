"""Korean validator tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.korean.domain.ko_config import KoConfig
from languages.korean.domain.ko_validator import KoValidator


def test_validator_creation():
    config = KoConfig()
    validator = KoValidator(config)
    assert validator is not None


def test_validate_result_returns_dict():
    config = KoConfig()
    validator = KoValidator(config)

    result = {
        "word_explanations": [
            ["저", "pronoun", "#FF4444", "I (humble form)"],
            ["는", "topic_marker", "#1E90FF", "topic marker particle"],
            ["학생", "noun", "#FFAA00", "student"],
            ["입니다", "copula", "#AA44FF", "is (formal polite copula)"],
        ],
        "html_output": "<div>test</div>",
        "confidence": 0.8,
        "elements": {},
        "explanations": {}
    }

    validated = validator.validate_result(result, "저는 학생입니다.")
    assert isinstance(validated, dict)
    assert 'confidence' in validated
    assert isinstance(validated['confidence'], float)
    assert 0.0 <= validated['confidence'] <= 1.0


def test_confidence_with_good_coverage():
    config = KoConfig()
    validator = KoValidator(config)

    result = {
        "word_explanations": [
            ["비", "noun", "#FFAA00", "rain"],
            ["가", "subject_marker", "#4169E1", "subject marker"],
            ["와요", "verb", "#44FF44", "comes (polite)"],
        ],
        "elements": {},
        "explanations": {},
        "confidence": 0.7
    }

    validated = validator.validate_result(result, "비가 와요.")
    # Full coverage should give decent confidence
    assert validated['confidence'] >= 0.5


def test_confidence_with_no_explanations():
    config = KoConfig()
    validator = KoValidator(config)

    result = {
        "word_explanations": [],
        "elements": {},
        "explanations": {},
        "confidence": 0.0
    }

    validated = validator.validate_result(result, "테스트 문장")
    assert validated['confidence'] < 0.5


def test_validate_explanation_quality():
    config = KoConfig()
    validator = KoValidator(config)

    result = {
        "word_explanations": [
            ["먹", "verb", "#44FF44", "eat (verb stem, polite conjugation)"],
            ["어요", "sentence_final_ending", "#CD853F", "polite speech level ending"],
        ],
        "explanations": {
            "overall_structure": "Simple SOV sentence with polite speech level ending",
            "key_features": "Verb conjugation from 먹다 to polite form 먹어요"
        }
    }

    quality = validator.validate_explanation_quality(result)
    assert isinstance(quality, dict)
    assert 'quality_score' in quality
    assert 0.0 <= quality['quality_score'] <= 1.0
