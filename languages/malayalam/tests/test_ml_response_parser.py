"""Malayalam response parser tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.malayalam.domain.ml_config import MlConfig
from languages.malayalam.domain.ml_fallbacks import MlFallbacks
from languages.malayalam.domain.ml_response_parser import MlResponseParser


def test_response_parser_creation():
    config = MlConfig()
    fallbacks = MlFallbacks(config)
    parser = MlResponseParser(config, fallbacks)
    assert parser is not None


def test_json_extraction():
    config = MlConfig()
    fallbacks = MlFallbacks(config)
    parser = MlResponseParser(config, fallbacks)

    ai_response = """Here's the analysis:
```json
{"words": [{"word": "കഴിക്കുക", "grammatical_role": "verb", "individual_meaning": "to eat"}]}
```
"""
    result = parser._extract_json(ai_response)
    assert isinstance(result, dict)
    assert "words" in result


def test_json_extraction_direct():
    config = MlConfig()
    fallbacks = MlFallbacks(config)
    parser = MlResponseParser(config, fallbacks)

    ai_response = '{"words": [{"word": "വെള്ളം", "grammatical_role": "noun", "individual_meaning": "water"}]}'
    result = parser._extract_json(ai_response)
    assert isinstance(result, dict)
    assert "words" in result


def test_parse_response_returns_dict():
    config = MlConfig()
    fallbacks = MlFallbacks(config)
    parser = MlResponseParser(config, fallbacks)

    ai_response = '{"sentence": "ഞാൻ വെള്ളം കുടിക്കുന്നു", "words": [{"word": "ഞാൻ", "grammatical_role": "pronoun", "individual_meaning": "I (first person singular)"}, {"word": "വെള്ളം", "grammatical_role": "noun", "individual_meaning": "water (direct object)"}, {"word": "കുടിക്കുന്നു", "grammatical_role": "verb", "individual_meaning": "drink (present tense)"}]}'
    result = parser.parse_response(ai_response, "beginner", "ഞാൻ വെള്ളം കുടിക്കുന്നു", "കുടിക്കുക")
    assert isinstance(result, dict)
    assert 'word_explanations' in result


def test_parse_response_handles_bad_json():
    config = MlConfig()
    fallbacks = MlFallbacks(config)
    parser = MlResponseParser(config, fallbacks)

    result = parser.parse_response("this is not json at all", "beginner", "ടെസ്റ്റ് വാക്യം", "ടെസ്റ്റ്")
    assert isinstance(result, dict)
    assert 'word_explanations' in result


def test_parse_batch_response():
    config = MlConfig()
    fallbacks = MlFallbacks(config)
    parser = MlResponseParser(config, fallbacks)

    ai_response = '[{"sentence": "ഞാൻ വെള്ളം കുടിക്കുന്നു", "words": [{"word": "ഞാൻ", "grammatical_role": "pronoun", "individual_meaning": "I"}, {"word": "വെള്ളം", "grammatical_role": "noun", "individual_meaning": "water"}, {"word": "കുടിക്കുന്നു", "grammatical_role": "verb", "individual_meaning": "drinks"}]}]'
    sentences = ["ഞാൻ വെള്ളം കുടിക്കുന്നു"]
    results = parser.parse_batch_response(ai_response, sentences, "beginner", "കുടിക്കുക")
    assert isinstance(results, list)
    assert len(results) == 1
    assert 'word_explanations' in results[0]


def test_json_repair():
    config = MlConfig()
    fallbacks = MlFallbacks(config)
    parser = MlResponseParser(config, fallbacks)

    # Test with trailing comma (common AI error)
    bad_json = '{"words": [{"word": "ഞാൻ", "grammatical_role": "pronoun",}]}'
    cleaned = parser._clean_json_response(bad_json)
    assert isinstance(cleaned, str)
