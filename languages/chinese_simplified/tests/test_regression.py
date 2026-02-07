
"""
Regression tests for zh analyzer.

These tests prevent reintroduction of previously fixed bugs.
"""

import pytest
import os
from dotenv import load_dotenv
from languages.chinese_simplified.zh_analyzer import ZhAnalyzer

# Load environment variables
load_dotenv()


class TestZhAnalyzerRegression:
    """Regression tests for known issues."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return ZhAnalyzer()

    def test_api_key_validation(self, analyzer):
        """Test that API key validation works correctly."""
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        
        # Should not crash with valid key
        result = analyzer.analyze_grammar("Test sentence", "test", "intermediate", api_key)
        assert result is not None

    def test_empty_input_handling(self, analyzer):
        """Test handling of empty inputs."""
        api_key = os.getenv('GEMINI_API_KEY', 'test_key')
        
        # Should handle empty inputs gracefully
        result = analyzer.analyze_grammar("", "", "intermediate", api_key)
        assert result is not None

