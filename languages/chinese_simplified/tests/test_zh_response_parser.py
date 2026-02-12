"""Chinese Simplified response parser tests."""

from ..domain.zh_config import ZhConfig
from ..domain.zh_response_parser import ZhResponseParser


def test_parse_response():
    parser = ZhResponseParser(ZhConfig())
    response = '{"words": [{"word": "你好", "grammatical_role": "interjection", "individual_meaning": "greeting"}]}'
    parsed = parser.parse_response(response, "beginner", "你好", "你好")
    assert "word_explanations" in parsed
    assert len(parsed["word_explanations"]) == 1
