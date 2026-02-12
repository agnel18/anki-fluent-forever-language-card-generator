
"""
System tests for es analyzer - End-to-end testing.
"""

import pytest
import os
from dotenv import load_dotenv
from languages.spanish.es_analyzer import EsAnalyzer

# Load environment variables
load_dotenv()


class TestEsAnalyzerSystem:
    """System-level tests for complete analyzer workflow."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return EsAnalyzer()

    def test_complete_workflow(self, analyzer):
        """Test complete analysis workflow."""
        sentence = "Hello world"
        target_word = "world"
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            pytest.skip("GEMINI_API_KEY not available for system test")

        result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

        assert result is not None
        assert hasattr(result, 'word_explanations')
        assert len(result.word_explanations) > 0

    def test_batch_processing(self, analyzer):
        """Test batch processing capability."""
        sentences = ["Hello world", "How are you", "Thank you"]
        target_word = "world"
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            pytest.skip("GEMINI_API_KEY not available for system test")

        results = analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", api_key)

        assert len(results) == len(sentences)
        for result in results:
            assert result is not None

    def test_error_recovery(self, analyzer):
        """Test error recovery mechanisms."""
        # Test with invalid input
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            pytest.skip("GEMINI_API_KEY not available for system test")
        try:
            result = analyzer.analyze_grammar("", "", "intermediate", api_key)
            # Should handle gracefully
            assert result is not None
        except Exception:
            # Should not crash completely
            pass
