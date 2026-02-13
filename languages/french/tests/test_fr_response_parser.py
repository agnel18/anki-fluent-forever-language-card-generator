"""French response parser tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.french.domain.fr_config import FrConfig
from languages.french.domain.fr_fallbacks import FrFallbacks
from languages.french.domain.fr_response_parser import FrResponseParser


def test_response_parser_creation():
    config = FrConfig()
    fallbacks = FrFallbacks(config)
    parser = FrResponseParser(config, fallbacks)
    assert parser is not None


def test_json_extraction():
    config = FrConfig()
    fallbacks = FrFallbacks(config)
    parser = FrResponseParser(config, fallbacks)

    # Test with markdown-wrapped JSON
    ai_response = """Here's the analysis:
```json
{"words": [{"word": "test", "role": "noun", "meaning": "a test"}]}
```
"""
    result = parser._extract_json(ai_response)
    assert isinstance(result, dict)
    assert "words" in result