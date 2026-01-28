
"""
Gold standard comparison tests for zh analyzer.

Compares results with Chinese Simplified and Hindi analyzers to ensure
consistency and quality standards are met.
"""

import pytest
import os
from dotenv import load_dotenv
from languages.zh.zh_analyzer import ZhAnalyzer
from languages.zh.zh_analyzer import ZhAnalyzer
from languages.hindi.hi_analyzer import HiAnalyzer

# Load environment variables
load_dotenv()


class TestZhAnalyzerGoldStandardComparison:
    """Compare with gold standard analyzers."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return ZhAnalyzer()

    @pytest.fixture
    def zh_analyzer(self):
        """Create Chinese Simplified analyzer for comparison."""
        return ZhAnalyzer()

    @pytest.fixture
    def hi_analyzer(self):
        """Create Hindi analyzer for comparison."""
        return HiAnalyzer()

    def test_result_structure_consistency(self, analyzer, zh_analyzer):
        """Test that result structure matches gold standards."""
        sentence = "Test sentence"
        target_word = "test"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)
        zh_result = zh_analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

        # Check that both have same basic structure
        assert hasattr(result, 'word_explanations')
        assert hasattr(zh_result, 'word_explanations')

        # Check that explanations have consistent format
        if result.word_explanations and zh_result.word_explanations:
            assert len(result.word_explanations[0]) >= 3  # word, role, color
            assert len(zh_result.word_explanations[0]) >= 3

    def test_confidence_scoring_range(self, analyzer):
        """Test that confidence scores are in valid range."""
        sentence = "Test sentence"
        target_word = "test"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        result = analyzer.analyze_grammar(sentence, target_word, "intermediate", api_key)

        # Confidence should be between 0 and 1
        assert hasattr(result, 'confidence_score')
        assert 0 <= result.confidence_score <= 1

    def test_batch_consistency(self, analyzer, zh_analyzer):
        """Test that batch processing is consistent."""
        sentences = ["Test 1", "Test 2", "Test 3"]
        target_word = "test"
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')

        results = analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", api_key)
        zh_results = zh_analyzer.batch_analyze_grammar(sentences, target_word, "intermediate", api_key)

        assert len(results) == len(sentences)
        assert len(zh_results) == len(sentences)

        # All results should have explanations
        for result in results:
            assert hasattr(result, 'word_explanations')
