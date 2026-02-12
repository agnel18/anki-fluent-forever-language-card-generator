"""Chinese Traditional response parser tests."""

from ..domain.zh_tw_config import ZhTwConfig
from ..domain.zh_tw_response_parser import ZhTwResponseParser


def test_parse_response():
    parser = ZhTwResponseParser(ZhTwConfig())
    response = '{"words": [{"word": "你好", "grammatical_role": "interjection", "individual_meaning": "greeting"}]}'
    parsed = parser.parse_response(response, "beginner", "你好", "你好")
    assert "word_explanations" in parsed
    assert len(parsed["word_explanations"]) == 1
