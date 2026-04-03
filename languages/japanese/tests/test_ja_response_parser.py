"""Japanese response parser tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.japanese.domain.ja_config import JaConfig
from languages.japanese.domain.ja_fallbacks import JaFallbacks
from languages.japanese.domain.ja_response_parser import JaResponseParser


def test_response_parser_creation():
    config = JaConfig()
    fallbacks = JaFallbacks(config)
    parser = JaResponseParser(config, fallbacks)
    assert parser is not None


def test_json_extraction():
    config = JaConfig()
    fallbacks = JaFallbacks(config)
    parser = JaResponseParser(config, fallbacks)

    ai_response = """Here's the analysis:
```json
{"words": [{"word": "食べる", "reading": "たべる", "grammatical_role": "verb", "individual_meaning": "to eat"}]}
```
"""
    result = parser._extract_json(ai_response)
    assert isinstance(result, dict)
    assert "words" in result


def test_json_extraction_direct():
    config = JaConfig()
    fallbacks = JaFallbacks(config)
    parser = JaResponseParser(config, fallbacks)

    ai_response = '{"words": [{"word": "猫", "reading": "ねこ", "grammatical_role": "noun", "individual_meaning": "cat"}]}'
    result = parser._extract_json(ai_response)
    assert isinstance(result, dict)
    assert "words" in result


def test_parse_response_returns_dict():
    config = JaConfig()
    fallbacks = JaFallbacks(config)
    parser = JaResponseParser(config, fallbacks)

    ai_response = '{"sentence": "猫がいる", "words": [{"word": "猫", "reading": "ねこ", "grammatical_role": "noun", "individual_meaning": "cat"}, {"word": "が", "grammatical_role": "subject_particle", "individual_meaning": "subject marker"}, {"word": "いる", "grammatical_role": "verb", "individual_meaning": "to exist (animate)"}]}'
    result = parser.parse_response(ai_response, "beginner", "猫がいる", "猫")
    assert isinstance(result, dict)
    assert 'word_explanations' in result


def test_parse_response_handles_bad_json():
    config = JaConfig()
    fallbacks = JaFallbacks(config)
    parser = JaResponseParser(config, fallbacks)

    result = parser.parse_response("this is not json at all", "beginner", "テスト文", "テスト")
    assert isinstance(result, dict)
    # Should fall back gracefully
    assert 'word_explanations' in result
