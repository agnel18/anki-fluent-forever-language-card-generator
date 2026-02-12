"""Chinese Simplified validator tests."""

from ..domain.zh_config import ZhConfig
from ..domain.zh_validator import ZhValidator


def test_validate_result_and_quality():
    validator = ZhValidator(ZhConfig())
    result = {
        "word_explanations": [["你好", "interjection", "#FFAA00", "greeting"]],
        "explanations": {"overall_structure": "simple", "key_features": "basic"}
    }
    validated = validator.validate_result(result, "你好")
    assert "confidence" in validated
    quality = validator.validate_explanation_quality(result)
    assert "quality_score" in quality
