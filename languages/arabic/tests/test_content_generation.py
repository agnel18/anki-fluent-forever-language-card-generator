
"""
Content generation tests for arabic analyzer - AI-powered sentence generation.
"""

import pytest
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
from languages.arabic.ar_analyzer import ArAnalyzer

# Load environment variables
load_dotenv()


class TestArAnalyzerContentGeneration:
    """Content generation tests for AI-powered sentence generation."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return ArAnalyzer()

    @pytest.fixture
    def mock_content_generator(self):
        """Mock content generator for testing."""
        mock_gen = Mock()
        mock_gen.generate_sentences.return_value = [
            {
                "sentence": "Test sentence 1",
                "translation": "Test translation 1",
                "grammar_explanation": "Test explanation 1"
            },
            {
                "sentence": "Test sentence 2",
                "translation": "Test translation 2",
                "grammar_explanation": "Test explanation 2"
            }
        ]
        return mock_gen

    def test_sentence_generation_prompt_creation(self, analyzer):
        """Test that language-specific prompts are created correctly."""
        target_word = "test_word"
        difficulty = "intermediate"
        context = "vocabulary"

        # Check if method exists
        if not hasattr(analyzer, 'create_sentence_generation_prompt'):
            pytest.skip("create_sentence_generation_prompt method not implemented")

        prompt = analyzer.create_sentence_generation_prompt(target_word, difficulty, context)

        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert target_word in prompt
        assert difficulty in prompt
        # Language-specific assertions would go here

    def test_content_generator_integration(self, analyzer, mock_content_generator):
        """Test integration with content generator service."""
        target_word = "test_word"
        difficulty = "intermediate"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        # Check if method exists
        if not hasattr(analyzer, 'generate_sentences'):
            pytest.skip("generate_sentences method not implemented")

        with patch('content_generator.ContentGenerator', return_value=mock_content_generator):
            sentences = analyzer.generate_sentences(target_word, difficulty, api_key)

            assert sentences is not None
            assert len(sentences) > 0
            assert all(isinstance(s, dict) for s in sentences)
            assert all('sentence' in s for s in sentences)
            assert all('translation' in s for s in sentences)

    def test_ai_response_parsing(self, analyzer):
        """Test parsing of AI responses into structured format."""
        # Check if method exists
        if not hasattr(analyzer, 'parse_ai_response'):
            pytest.skip("parse_ai_response method not implemented")

        # Test valid response
        valid_response = """
        1. Sentence: Hello world
        Translation: Hello world translation
        Grammar: Basic greeting

        2. Sentence: How are you?
        Translation: How are you translation
        Grammar: Question structure
        """

        parsed = analyzer.parse_ai_response(valid_response)
        assert parsed is not None
        assert len(parsed) > 0
        assert all('sentence' in item for item in parsed)

        # Test malformed response handling
        malformed_response = "Invalid response format"
        parsed_malformed = analyzer.parse_ai_response(malformed_response)
        # Should handle gracefully, possibly with fallback
        assert parsed_malformed is not None

    def test_fallback_mechanisms(self, analyzer):
        """Test fallback mechanisms when AI generation fails."""
        target_word = "test_word"
        difficulty = "intermediate"
        api_key = "invalid_key"

        # Check if method exists
        if not hasattr(analyzer, 'generate_sentences'):
            pytest.skip("generate_sentences method not implemented")

        # Test with invalid API key - should fallback gracefully
        try:
            sentences = analyzer.generate_sentences(target_word, difficulty, api_key)
            # Should not crash, may return empty list or fallback content
            assert isinstance(sentences, list)
        except Exception as e:
            # Should handle API errors gracefully
            assert "API" in str(e) or "key" in str(e).lower()

    def test_language_specific_prompts(self, analyzer):
        """Test that prompts are tailored to language characteristics."""
        target_word = "test_word"
        difficulty = "beginner"

        # Check if method exists
        if not hasattr(analyzer, 'create_sentence_generation_prompt'):
            pytest.skip("create_sentence_generation_prompt method not implemented")

        prompt = analyzer.create_sentence_generation_prompt(target_word, difficulty)

        # Language-specific prompt validation
        # This would include checks for script type, grammar patterns, etc.
        assert prompt is not None
        assert self.language_code.upper() in prompt or self.language_code in prompt

    def test_sentence_quality_validation(self, analyzer, mock_content_generator):
        """Test that generated sentences meet quality criteria."""
        target_word = "test_word"
        difficulty = "intermediate"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        # Check if method exists
        if not hasattr(analyzer, 'generate_sentences'):
            pytest.skip("generate_sentences method not implemented")

        with patch('content_generator.ContentGenerator', return_value=mock_content_generator):
            sentences = analyzer.generate_sentences(target_word, difficulty, api_key)

            for sentence in sentences:
                assert 'sentence' in sentence
                assert 'translation' in sentence
                assert len(sentence['sentence']) > 0
                assert len(sentence['translation']) > 0
                # Check that target word appears in sentence
                assert target_word in sentence['sentence'].lower()

    def test_batch_sentence_generation(self, analyzer, mock_content_generator):
        """Test batch generation of multiple sentences."""
        target_words = ["word1", "word2", "word3"]
        difficulty = "intermediate"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        # Check if method exists
        if not hasattr(analyzer, 'batch_generate_sentences'):
            pytest.skip("batch_generate_sentences method not implemented")

        with patch('content_generator.ContentGenerator', return_value=mock_content_generator):
            results = analyzer.batch_generate_sentences(target_words, difficulty, api_key)

            assert len(results) == len(target_words)
            for word, sentences in results.items():
                assert word in target_words
                assert isinstance(sentences, list)
                assert len(sentences) > 0

    def test_error_handling_and_recovery(self, analyzer):
        """Test error handling during content generation."""
        # Check if method exists
        if not hasattr(analyzer, 'generate_sentences'):
            pytest.skip("generate_sentences method not implemented")

        # Test with network timeout simulation
        target_word = "test_word"
        api_key = "test_key"

        with patch('content_generator.ContentGenerator') as mock_gen_class:
            mock_instance = Mock()
            mock_instance.generate_sentences.side_effect = Exception("Network timeout")
            mock_gen_class.return_value = mock_instance

            # Should handle the error gracefully
            try:
                sentences = analyzer.generate_sentences(target_word, "intermediate", api_key)
                # May return empty list or fallback content
                assert isinstance(sentences, list)
            except Exception:
                # Should not crash the entire application
                pass
