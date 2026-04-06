"""Korean response parser tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.korean.domain.ko_config import KoConfig
from languages.korean.infrastructure.ko_fallbacks import KoFallbacks
from languages.korean.domain.ko_response_parser import KoResponseParser


def test_response_parser_creation():
    config = KoConfig()
    fallbacks = KoFallbacks(config)
    parser = KoResponseParser(config, fallbacks)
    assert parser is not None


def test_json_extraction():
    config = KoConfig()
    fallbacks = KoFallbacks(config)
    parser = KoResponseParser(config, fallbacks)

    ai_response = """Here's the analysis:
```json
{"words": [{"word": "먹다", "grammatical_role": "verb", "individual_meaning": "to eat"}]}
```
"""
    result = parser._extract_json(ai_response)
    assert isinstance(result, dict)
    assert "words" in result


def test_json_extraction_direct():
    config = KoConfig()
    fallbacks = KoFallbacks(config)
    parser = KoResponseParser(config, fallbacks)

    ai_response = '{"words": [{"word": "학생", "grammatical_role": "noun", "individual_meaning": "student"}]}'
    result = parser._extract_json(ai_response)
    assert isinstance(result, dict)
    assert "words" in result


def test_parse_response_returns_dict():
    config = KoConfig()
    fallbacks = KoFallbacks(config)
    parser = KoResponseParser(config, fallbacks)

    ai_response = '{"sentence": "저는 학생입니다.", "words": [{"word": "저", "grammatical_role": "pronoun", "individual_meaning": "I (humble)"}, {"word": "는", "grammatical_role": "topic_marker", "individual_meaning": "topic marker"}, {"word": "학생", "grammatical_role": "noun", "individual_meaning": "student"}, {"word": "입니다", "grammatical_role": "copula", "individual_meaning": "is (formal polite)"}]}'
    result = parser.parse_response(ai_response, "beginner", "저는 학생입니다.", "학생")
    assert isinstance(result, dict)
    assert 'word_explanations' in result


def test_parse_response_handles_bad_json():
    config = KoConfig()
    fallbacks = KoFallbacks(config)
    parser = KoResponseParser(config, fallbacks)

    result = parser.parse_response("this is not json at all", "beginner", "테스트 문장", "테스트")
    assert isinstance(result, dict)
    # Should fall back gracefully
    assert 'word_explanations' in result
