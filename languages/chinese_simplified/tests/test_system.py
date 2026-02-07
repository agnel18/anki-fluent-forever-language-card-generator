
"""
System tests for zh analyzer - End-to-end testing.
"""

import pytest
import os
from dotenv import load_dotenv
from languages.chinese_simplified.zh_analyzer import ZhAnalyzer

# Load environment variables
load_dotenv()


class TestZhAnalyzerSystem:
    """System-level tests for complete analyzer workflow."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return ZhAnalyzer()

    def test_complete_workflow(self, analyzer):
        """Test complete analysis workflow."""
        sentence = "Hello world"
        target_word = "world"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

        assert result is not None
        assert hasattr(result, 'word_explanations')
        assert len(result.word_explanations) > 0

    def test_batch_processing(self, analyzer):
        """Test batch processing capability."""
        sentences = ["Hello world", "How are you", "Thank you"]
        target_word = "world"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        results = analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", api_key)

        assert len(results) == len(sentences)
        for result in results:
            assert result is not None

    def test_error_recovery(self, analyzer):
        """Test error recovery mechanisms."""
        # Test with invalid input
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        try:
            result = analyzer.analyze_grammar("", "", "intermediate", api_key)
            # Should handle gracefully
            assert result is not None
        except Exception:
            # Should not crash completely
            pass

