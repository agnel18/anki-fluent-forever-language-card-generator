"""German response parser tests."""

from ..domain.de_config import DeConfig
from ..domain.de_response_parser import DeResponseParser


def test_parse_response():
    parser = DeResponseParser(DeConfig())
    response = '{"words": [{"word": "Das", "grammatical_role": "article", "individual_meaning": "definite"}]}'
    parsed = parser.parse_response(response, "beginner", "Das", "Das")
    assert "word_explanations" in parsed
    assert len(parsed["word_explanations"]) == 1
