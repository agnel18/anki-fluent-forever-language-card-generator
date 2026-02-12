"""Chinese Traditional validator tests."""

from ..domain.zh_tw_config import ZhTwConfig
from ..domain.zh_tw_validator import ZhTwValidator


def test_validate_result_and_quality():
    validator = ZhTwValidator(ZhTwConfig())
    result = {
        "word_explanations": [["你好", "interjection", "#FFAA00", "greeting"]],
        "explanations": {"overall_structure": "simple", "key_features": "basic"}
    }
    validated = validator.validate_result(result, "你好")
    assert "confidence" in validated
    quality = validator.validate_explanation_quality(result)
    assert "quality_score" in quality
