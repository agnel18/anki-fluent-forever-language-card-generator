"""Hindi response parser tests."""

from ..domain.hi_config import HiConfig
from ..domain.hi_response_parser import HiResponseParser


def test_parse_response():
    parser = HiResponseParser(HiConfig())
    response = '{"words": [{"word": "मैं", "grammatical_role": "pronoun", "individual_meaning": "first person"}]}'
    parsed = parser.parse_response(response, "beginner", "मैं", "मैं")
    assert "word_explanations" in parsed
    assert len(parsed["word_explanations"]) == 1
