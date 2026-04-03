"""Japanese validator tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.japanese.domain.ja_config import JaConfig
from languages.japanese.domain.ja_validator import JaValidator


def test_validator_creation():
    config = JaConfig()
    validator = JaValidator(config)
    assert validator is not None


def test_validate_result_returns_dict():
    config = JaConfig()
    validator = JaValidator(config)

    result = {
        "word_explanations": [
            ["私", "pronoun", "#4FC3F7", "I/me"],
            ["は", "topic_particle", "#81C784", "(topic marker)"],
            ["本", "noun", "#4FC3F7", "book"],
            ["を", "object_particle", "#81C784", "(object marker)"],
            ["読む", "verb", "#FF8A65", "read"],
        ],
        "html_output": "<div>test</div>",
        "confidence": 0.8,
        "elements": {},
        "explanations": {}
    }

    validated = validator.validate_result(result, "私は本を読む")
    assert isinstance(validated, dict)
    assert 'confidence' in validated
    assert isinstance(validated['confidence'], float)
    assert 0.0 <= validated['confidence'] <= 1.0


def test_confidence_with_good_coverage():
    config = JaConfig()
    validator = JaValidator(config)

    result = {
        "word_explanations": [
            ["猫", "noun", "#4FC3F7", "cat"],
            ["が", "subject_particle", "#81C784", "subject marker"],
            ["いる", "verb", "#FF8A65", "to exist"],
        ],
        "elements": {},
        "explanations": {},
        "confidence": 0.7
    }

    validated = validator.validate_result(result, "猫がいる")
    # Full coverage should give decent confidence
    assert validated['confidence'] >= 0.5


def test_confidence_with_no_explanations():
    config = JaConfig()
    validator = JaValidator(config)

    result = {
        "word_explanations": [],
        "elements": {},
        "explanations": {},
        "confidence": 0.0
    }

    validated = validator.validate_result(result, "テスト文")
    assert validated['confidence'] < 0.5


def test_validate_explanation_quality():
    config = JaConfig()
    validator = JaValidator(config)

    result = {
        "word_explanations": [
            ["食べ", "verb", "#FF8A65", "eat (te-form stem)"],
            ["ます", "auxiliary_verb", "#CE93D8", "polite suffix"],
        ],
        "explanations": {
            "overall_structure": "Polite verb form showing masu-desu politeness",
            "key_features": "Verb conjugation from 食べる to masu-form"
        }
    }

    quality = validator.validate_explanation_quality(result)
    assert isinstance(quality, dict)
    assert 'quality_score' in quality
    assert 0.0 <= quality['quality_score'] <= 1.0
