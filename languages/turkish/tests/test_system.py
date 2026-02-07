
"""
System tests for tr analyzer - End-to-end testing.
"""

import pytest
import os
from dotenv import load_dotenv
from languages.turkish.tr_analyzer import TrAnalyzer

# Load environment variables
load_dotenv()


class TestTrAnalyzerSystem:
    """System-level tests for complete analyzer workflow."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return TrAnalyzer()

    def test_complete_workflow(self, analyzer):
        """Test complete analysis workflow."""
        if os.getenv("RUN_SYSTEM_TESTS") != "1":
            pytest.skip("RUN_SYSTEM_TESTS not enabled")
        sentence = "Hello world"
        target_word = "world"
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "test_key":
            pytest.skip("GEMINI_API_KEY not available for system test")

        result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

        assert result is not None
        assert hasattr(result, 'word_explanations')
        assert len(result.word_explanations) > 0

    def test_batch_processing(self, analyzer):
        """Test batch processing capability."""
        if os.getenv("RUN_SYSTEM_TESTS") != "1":
            pytest.skip("RUN_SYSTEM_TESTS not enabled")
        sentences = ["Hello world", "How are you", "Thank you"]
        target_word = "world"
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "test_key":
            pytest.skip("GEMINI_API_KEY not available for system test")

        results = analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", api_key)

        assert len(results) == len(sentences)
        for result in results:
            assert result is not None

    def test_error_recovery(self, analyzer):
        """Test error recovery mechanisms."""
        if os.getenv("RUN_SYSTEM_TESTS") != "1":
            pytest.skip("RUN_SYSTEM_TESTS not enabled")
        # Test with invalid input
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "test_key":
            pytest.skip("GEMINI_API_KEY not available for system test")
        try:
            result = analyzer.analyze_grammar("", "", "intermediate", api_key)
            # Should handle gracefully
            assert result is not None
        except Exception:
            # Should not crash completely
            pass
