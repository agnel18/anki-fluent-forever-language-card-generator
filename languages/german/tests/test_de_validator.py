"""German validator tests."""

from ..domain.de_config import DeConfig
from ..domain.de_validator import DeValidator


def test_validate_result_and_quality():
    validator = DeValidator(DeConfig())
    result = {
        "word_explanations": [["Das", "article", "#AAAAAA", "definite article"]],
        "explanations": {"overall_structure": "simple", "key_features": "basic"}
    }
    validated = validator.validate_result(result, "Das")
    assert "confidence" in validated
    quality = validator.validate_explanation_quality(result)
    assert "quality_score" in quality
