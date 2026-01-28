
"""
Performance tests for zh_tw analyzer.
"""

import pytest
from languages.chinese_traditional.zh_tw_analyzer import ZhTwAnalyzer


class TestZhTwAnalyzerPerformance:
    """Performance tests for analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return ZhTwAnalyzer()

    def test_dummy(self, analyzer):
        """Dummy test."""
        assert analyzer is not None
