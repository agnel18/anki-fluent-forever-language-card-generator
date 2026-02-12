"""Hindi validator tests."""

from ..domain.hi_config import HiConfig
from ..domain.hi_validator import HiValidator


def test_validate_result_and_quality():
    validator = HiValidator(HiConfig())
    result = {
        "word_explanations": [["मैं", "pronoun", "#FF4444", "first person"]],
        "explanations": {"overall_structure": "simple", "key_features": "basic"}
    }
    validated = validator.validate_result(result, "मैं")
    assert "confidence" in validated
    quality = validator.validate_explanation_quality(result)
    assert "quality_score" in quality
