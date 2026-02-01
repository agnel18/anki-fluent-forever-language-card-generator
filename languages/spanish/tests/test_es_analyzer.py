# Test Spanish Analyzer
# Main facade tests for Spanish grammar analysis

import pytest
import json
from unittest.mock import patch, MagicMock
from ..es_analyzer import EsAnalyzer

class TestEsAnalyzer:
    """Basic tests for Spanish analyzer"""

    @pytest.fixture
    def analyzer(self):
        return EsAnalyzer()

    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer.language_code == "es"
        assert analyzer.language_name == "Spanish"
        assert analyzer.es_config is not None
        assert analyzer.prompt_builder is not None
        assert analyzer.response_parser is not None
        assert analyzer.validator is not None
        assert analyzer.fallbacks is not None

    def test_language_config(self, analyzer):
        """Test language configuration"""
        config = analyzer.language_config
        assert config.code == "es"
        assert config.name == "Spanish"
        assert config.native_name == "Español"
        assert config.family == "Indo-European (Romance)"
        assert config.script_type == "alphabetic"
        assert config.complexity_rating == "medium"
        assert "gender_agreement" in config.key_features
        assert "beginner" in config.supported_complexity_levels

    def test_simple_prompt_generation(self, analyzer):
        """Test prompt generation without API call"""
        prompt = analyzer.get_grammar_prompt("beginner", "El gato come pescado", "gato")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "El gato come pescado" in prompt
        assert "gato" in prompt

    def test_color_scheme(self, analyzer):
        """Test color scheme generation"""
        colors = analyzer.get_color_scheme("beginner")
        assert isinstance(colors, dict)
        assert 'noun' in colors
        assert 'verb' in colors
        assert 'adjective' in colors

    def test_fallback_analysis(self, analyzer):
        """Test fallback analysis creation"""
        # This tests the fallback mechanism without API calls
        fallback = analyzer.fallbacks.create_fallback("El gato come", "beginner", "gato")
        assert 'words' in fallback
        assert 'overall_analysis' in fallback
        assert 'confidence' in fallback
        assert len(fallback['words']) > 0

    @pytest.mark.parametrize("sentence,expected_words", [
        ("El gato come", 3),
        ("La casa es grande", 4),
        ("Yo estudio español", 3),
    ])
    def test_fallback_word_count(self, analyzer, sentence, expected_words):
        """Test that fallback creates correct number of words"""
        fallback = analyzer.fallbacks.create_fallback(sentence, "beginner")
        assert len(fallback['words']) == expected_words

    def test_supported_complexities(self, analyzer):
        """Test supported complexity levels"""
        complexities = analyzer.get_supported_complexities()
        assert 'beginner' in complexities
        assert 'intermediate' in complexities
        assert 'advanced' in complexities

    def test_language_info(self, analyzer):
        """Test language information retrieval"""
        info = analyzer.get_language_info()
        assert info['code'] == 'es'
        assert info['name'] == 'Spanish'
        assert info['native_name'] == 'Español'
        assert info['is_rtl'] == False
        assert 'gender_agreement' in info['features']

    def test_spanish_text_validation(self, analyzer):
        """Test Spanish text validation"""
        assert analyzer.validate_spanish_text("El niño come manzanas") == True  # Has ñ
        assert analyzer.validate_spanish_text("El niño come manzanas") == True  # Has ñ
        assert analyzer.validate_spanish_text("¿Cómo estás?") == True  # Has special chars
        assert analyzer.validate_spanish_text("Hola mundo") == False  # No special chars

    @patch('languages.spanish.es_analyzer.EsAnalyzer._call_ai')
    def test_fallback_analysis_when_ai_fails(self, mock_call_ai, analyzer):
        """Test fallback analysis when AI call fails"""
        # Mock AI call to fail
        mock_call_ai.return_value = None

        result = analyzer.analyze_grammar(
            sentence="El gato come pescado",
            target_word="gato",
            complexity="beginner",
            gemini_api_key="mock_key"
        )

        # Should return fallback result
        assert result.sentence == "El gato come pescado"
        assert result.target_word == "gato"
        assert result.language_code == "es"
        assert result.complexity_level == "beginner"
        assert result.confidence_score < 0.5  # Low confidence for fallback
        assert result.is_rtl == False
        assert len(result.word_explanations) > 0  # Should still have basic analysis

    def test_invalid_inputs(self, analyzer):
        """Test handling of invalid inputs"""
        # Empty sentence
        result = analyzer.analyze_grammar("", "test", "beginner", "key")
        assert result.confidence_score < 0.5

        # Empty target word
        result = analyzer.analyze_grammar("test sentence", "", "beginner", "key")
        assert result.confidence_score < 0.5

        # Invalid complexity
        result = analyzer.analyze_grammar("test", "test", "invalid", "key")
        assert result.confidence_score < 0.5

    @patch('languages.spanish.es_analyzer.EsAnalyzer._call_ai')
    def test_full_analysis_workflow(self, mock_call_ai, analyzer):
        """Test complete analysis workflow with mocked AI"""
        # Mock successful AI response
        mock_call_ai.return_value = '''{
            "words": [
                {"word": "El", "grammatical_role": "determiner", "meaning": "El (determiner): the; definite article"},
                {"word": "gato", "grammatical_role": "noun", "meaning": "gato (noun): cat; subject of sentence"},
                {"word": "come", "grammatical_role": "verb", "meaning": "come (verb): eats; main action"}
            ],
            "explanations": {
                "overall_structure": "Simple subject-verb sentence",
                "key_features": "Definite article agreement"
            }
        }'''

        result = analyzer.analyze_grammar(
            sentence="El gato come",
            target_word="gato",
            complexity="beginner",
            gemini_api_key="mock_key"
        )

        # Verify result structure
        assert result.sentence == "El gato come"
        assert result.target_word == "gato"
        assert result.language_code == "es"
        assert result.complexity_level == "beginner"
        assert len(result.word_explanations) > 0
        assert result.confidence_score > 0
        assert result.html_output is not None
        assert result.is_rtl == False
        assert 'dir="ltr"' in result.html_output  # LTR HTML