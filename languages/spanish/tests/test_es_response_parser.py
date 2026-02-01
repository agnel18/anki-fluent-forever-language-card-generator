# Test Spanish Response Parser
# Tests for EsResponseParser class

import pytest
import json
from ..domain.es_config import EsConfig
from ..domain.es_response_parser import EsResponseParser

class TestEsResponseParser:
    """Tests for Spanish response parser"""

    @pytest.fixture
    def config(self):
        return EsConfig()

    @pytest.fixture
    def response_parser(self, config):
        return EsResponseParser(config)

    def test_initialization(self, response_parser, config):
        """Test response parser initializes correctly"""
        assert response_parser.config == config

    def test_parse_valid_json_response(self, response_parser):
        """Test parsing valid JSON response"""
        valid_response = '''{
            "words": [
                {
                    "word": "El",
                    "grammatical_role": "determiner",
                    "meaning": "El (determiner): the; definite article"
                },
                {
                    "word": "gato",
                    "grammatical_role": "noun",
                    "meaning": "gato (noun): cat; subject of sentence"
                }
            ],
            "overall_analysis": {
                "sentence_structure": "Basic SVO structure",
                "key_features": "Definite article usage"
            }
        }'''

        result = response_parser.parse_response(valid_response, "beginner", "El gato come", "gato")

        assert 'words' in result
        assert len(result['words']) == 2
        assert result['words'][0]['word'] == "El"
        assert result['words'][0]['grammatical_role'] == "determiner"

    def test_parse_markdown_json_response(self, response_parser):
        """Test parsing JSON wrapped in markdown code blocks"""
        markdown_response = '''Here's the analysis:
```json
{
    "words": [
        {
            "word": "Hola",
            "grammatical_role": "interjection",
            "meaning": "Hola (interjection): hello; greeting"
        }
    ],
    "overall_analysis": {
        "sentence_structure": "Single word greeting",
        "key_features": "Informal greeting"
    }
}
```
That's the result.'''

        result = response_parser.parse_response(markdown_response, "beginner", "Hola", "Hola")

        assert 'words' in result
        assert len(result['words']) == 1
        assert result['words'][0]['word'] == "Hola"

    def test_fallback_for_invalid_response(self, response_parser):
        """Test fallback creation for invalid responses"""
        invalid_response = "This is not JSON at all, just plain text."

        result = response_parser.parse_response(invalid_response, "beginner", "El gato", "gato")

        # Should return fallback analysis
        assert 'words' in result
        assert 'overall_analysis' in result
        assert 'confidence' in result
        assert result['confidence'] == 0.3  # Fallback confidence

    def test_fallback_word_classification(self, response_parser):
        """Test fallback word classification"""
        fallback = response_parser._create_fallback_analysis("El gato come", "beginner", "gato")

        words = fallback['words']
        assert len(words) == 3  # El, gato, come

        # Check classifications
        el_word = next(w for w in words if w['word'] == 'El')
        assert el_word['grammatical_role'] == 'determiner'

        gato_word = next(w for w in words if w['word'] == 'gato')
        assert gato_word['grammatical_role'] == 'noun'

        come_word = next(w for w in words if w['word'] == 'come')
        assert come_word['grammatical_role'] == 'verb'

    def test_spanish_tokenization(self, response_parser):
        """Test Spanish text tokenization"""
        sentence = "El gato come pescado."
        words = response_parser._tokenize_spanish(sentence)
        # Should split on spaces and handle punctuation
        assert "El" in words
        assert "gato" in words
        assert "come" in words
        assert "pescado." in words  # Punctuation attached

    def test_spanish_word_classification(self, response_parser):
        """Test Spanish word classification logic"""
        # Test determiners
        assert response_parser._classify_spanish_word("el") == "determiner"
        assert response_parser._classify_spanish_word("una") == "determiner"

        # Test prepositions
        assert response_parser._classify_spanish_word("de") == "preposition"
        assert response_parser._classify_spanish_word("con") == "preposition"

        # Test pronouns
        assert response_parser._classify_spanish_word("yo") == "pronoun"
        assert response_parser._classify_spanish_word("me") == "pronoun"

        # Test verbs
        assert response_parser._classify_spanish_word("comer") == "verb"
        assert response_parser._classify_spanish_word("hablo") == "verb"

        # Test default to noun
        assert response_parser._classify_spanish_word("casa") == "noun"