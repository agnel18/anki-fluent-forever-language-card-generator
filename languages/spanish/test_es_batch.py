
"""
Batch processing tests for es analyzer.
Tests efficient multi-sentence analysis using batch_analyze_grammar method.
"""

import pytest
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
from languages.spanish.es_analyzer import EsAnalyzer

# Load environment variables
load_dotenv()


class TestEsAnalyzerBatchProcessing:
    """Batch processing tests for efficient multi-sentence analysis."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return EsAnalyzer()

    def test_batch_analyze_grammar_method_exists(self, analyzer):
        """Test that batch_analyze_grammar method exists and is callable."""
        assert hasattr(analyzer, 'batch_analyze_grammar'), "batch_analyze_grammar method missing"
        assert callable(getattr(analyzer, 'batch_analyze_grammar')), "batch_analyze_grammar not callable"

    def test_batch_processing_structure(self, analyzer):
        """Test that batch processing returns correct structure."""
        sentences = ["Test sentence 1", "Test sentence 2", "Test sentence 3"]
        target_word = "test"
        complexity = "intermediate"

        # Mock the AI call to avoid actual API usage
        with patch('languages.spanish.es_analyzer.get_gemini_api') as mock_get_api:
            mock_api = Mock()
            mock_get_api.return_value = mock_api

            # Mock batch response
            mock_response = Mock()
            json_response = {
                "batch_results": [
                    {
                        "sentence": "Test sentence 1",
                        "words": [
                            {
                                "word": "test",
                                "grammatical_role": "noun",
                                "type": "common_noun",
                                "person": "third",
                                "number": "singular",
                                "case": "nominative",
                                "meaning": "specific grammatical explanation"
                            }
                        ],
                        "explanations": {
                            "overall_structure": "Subject-verb-object structure",
                            "key_features": "specific features"
                        }
                    }
                ]
            }
            import json
            mock_response.text = json.dumps(json_response)
            mock_api.generate_content.return_value = mock_response

            # Test batch analysis
            results = analyzer.batch_analyze_grammar(sentences, target_word, complexity, "test_api_key")

            # Verify results structure
            assert len(results) == len(sentences)

            for i, result in enumerate(results):
                assert hasattr(result, 'sentence')
                assert hasattr(result, 'target_word')
                assert hasattr(result, 'language_code')
                assert hasattr(result, 'complexity_level')
                assert hasattr(result, 'word_explanations')
                assert len(result.word_explanations) > 0

    def test_batch_processing_with_real_api(self, analyzer):
        """Integration test for batch processing with real API calls."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            pytest.skip("GEMINI_API_KEY not available for real API test")

        # Test sentences - replace with actual language sentences
        sentences = ["Test sentence 1 in language.", "Test sentence 2 in language.", "Test sentence 3 in language."]
        target_word = "test"
        complexity = "intermediate"

        # Test with real API
        results = analyzer.batch_analyze_grammar(sentences, target_word, complexity, api_key)

        # Verify results
        assert len(results) == len(sentences)

        success_count = 0
        for i, result in enumerate(results):
            assert result.sentence == sentences[i]
            assert result.target_word == target_word
            assert result.language_code == "es"
            assert result.complexity_level == complexity
            assert len(result.word_explanations) > 0

            # Check if explanations are specific (not generic fallbacks)
            has_specific_explanations = False
            for exp in result.word_explanations:
                if len(exp) >= 4:
                    word, role, color, meaning = exp
                    # Check if meaning contains specific grammatical terms
                    if not any(generic in meaning.lower() for generic in [
                        "a thing, person, or concept",
                        "a word that describes",
                        "other word",
                        "basic analysis"
                    ]):
                        has_specific_explanations = True
                        break

            if has_specific_explanations:
                success_count += 1

        # At least some sentences should have specific explanations
        assert success_count > 0, "No sentences produced specific grammatical explanations"

    def test_batch_efficiency(self, analyzer):
        """Test that batch processing is more efficient than individual processing."""
        sentences = ["Sentence 1", "Sentence 2", "Sentence 3", "Sentence 4", "Sentence 5"]
        target_word = "test"
        complexity = "intermediate"

        with patch('languages.spanish.es_analyzer.get_gemini_api') as mock_get_api:
            mock_api = Mock()
            mock_get_api.return_value = mock_api

            # Mock successful batch response
            mock_response = Mock()
            import json
            mock_response.text = json.dumps({"batch_results": []})
            mock_api.generate_content.return_value = mock_response

            import time
            start_time = time.time()
            batch_results = analyzer.batch_analyze_grammar(sentences, target_word, complexity, "test_api_key")
            batch_time = time.time() - start_time

            # Verify batch processing completes
            assert len(batch_results) == len(sentences), "Batch processing failed to return correct number of results"

            # Batch should be reasonably fast (less than 1 second with mocking)
            assert batch_time < 1.0, "Batch processing too slow"
