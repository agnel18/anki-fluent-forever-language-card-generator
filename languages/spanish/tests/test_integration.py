# Test Spanish Integration
# Integration tests for Spanish analyzer components

import pytest
from ..es_analyzer import EsAnalyzer
from ..domain.es_config import EsConfig
from ..domain.es_prompt_builder import EsPromptBuilder
from ..domain.es_response_parser import EsResponseParser
from ..domain.es_validator import EsValidator
from ..infrastructure.es_fallbacks import EsFallbacks

class TestEsIntegration:
    """Integration tests for Spanish analyzer"""

    @pytest.fixture
    def analyzer(self):
        return EsAnalyzer()

    def test_full_analysis_workflow_simulation(self, analyzer):
        """Test complete analysis workflow without API calls"""
        sentence = "El gato come pescado"
        target_word = "gato"
        complexity = "beginner"

        # Test prompt generation
        prompt = analyzer.get_grammar_prompt(complexity, sentence, target_word)
        assert isinstance(prompt, str)
        assert sentence in prompt

        # Test fallback analysis (simulates failed API)
        fallback_result = analyzer.fallbacks.create_fallback(sentence, complexity, target_word)
        assert 'words' in fallback_result
        assert 'overall_analysis' in fallback_result
        assert len(fallback_result['words']) == 4  # El, gato, come, pescado

        # Test validation of fallback result
        validated = analyzer.validator.validate_result(fallback_result, sentence)
        assert 'confidence' in validated
        assert validated['confidence'] < 0.5  # Fallback confidence should be low

    def test_component_integration(self, analyzer):
        """Test that all components work together"""
        # Test that analyzer has all required components
        assert hasattr(analyzer, 'es_config')
        assert hasattr(analyzer, 'prompt_builder')
        assert hasattr(analyzer, 'response_parser')
        assert hasattr(analyzer, 'validator')
        assert hasattr(analyzer, 'fallbacks')

        # Test component initialization
        assert analyzer.es_config is not None
        assert analyzer.prompt_builder is not None
        assert analyzer.response_parser is not None
        assert analyzer.validator is not None
        assert analyzer.fallbacks is not None

    def test_prompt_to_parser_integration(self, analyzer):
        """Test integration between prompt builder and response parser"""
        sentence = "Hola mundo"
        target_word = "mundo"
        complexity = "beginner"

        # Generate prompt
        prompt = analyzer.prompt_builder.build_single_prompt(sentence, target_word, complexity)

        # Simulate AI response (JSON that parser should handle)
        mock_response = '''{
            "words": [
                {
                    "word": "Hola",
                    "grammatical_role": "interjection",
                    "meaning": "Hola (interjection): hello; greeting at start of sentence"
                },
                {
                    "word": "mundo",
                    "grammatical_role": "noun",
                    "meaning": "mundo (noun): world; direct object of implied verb"
                }
            ],
            "overall_analysis": {
                "sentence_structure": "Simple greeting + noun phrase",
                "key_features": "Interjection usage"
            }
        }'''

        # Parse the response
        parsed = analyzer.response_parser.parse_response(mock_response, complexity, sentence, target_word)

        # Validate the result
        validated = analyzer.validator.validate_result(parsed, sentence)

        # Check integration
        assert 'words' in validated
        assert 'confidence' in validated
        assert len(validated['words']) == 2

    def test_fallback_integration(self, analyzer):
        """Test fallback system integration"""
        sentence = "Buenos días"
        complexity = "beginner"

        # Create fallback
        fallback = analyzer.fallbacks.create_fallback(sentence, complexity)

        # Should have proper structure
        assert 'words' in fallback
        assert 'overall_analysis' in fallback
        assert 'confidence' in fallback

        # Words should be classified
        for word_data in fallback['words']:
            assert 'word' in word_data
            assert 'grammatical_role' in word_data
            assert 'meaning' in word_data

    def test_color_scheme_integration(self, analyzer):
        """Test color scheme integration across components"""
        complexity = "intermediate"

        # Get color scheme from analyzer
        colors = analyzer.get_color_scheme(complexity)

        # Get roles for same complexity
        roles = analyzer.es_config.get_grammatical_roles(complexity)

        # Should have colors for all roles
        for role in roles.keys():
            assert role in colors, f"Missing color for role: {role}"

    @pytest.mark.parametrize("sentence,target,complexity", [
        ("El perro ladra", "perro", "beginner"),
        ("La casa es bonita", "bonita", "intermediate"),
        ("Estoy estudiando español", "estudiando", "advanced"),
    ])
    def test_various_sentences_fallback(self, analyzer, sentence, target, complexity):
        """Test fallback analysis with various sentence types"""
        fallback = analyzer.fallbacks.create_fallback(sentence, complexity, target)

        assert 'words' in fallback
        assert len(fallback['words']) > 0

        # All words should have required fields
        for word_data in fallback['words']:
            assert 'word' in word_data
            assert 'grammatical_role' in word_data
            assert 'meaning' in word_data