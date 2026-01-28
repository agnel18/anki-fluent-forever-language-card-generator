
"""
Performance tests for zh analyzer.
"""

import pytest
from languages.zh.zh_analyzer import ZhAnalyzer


class TestZhAnalyzerPerformance:
    """Performance tests for analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return ZhAnalyzer()

    def test_dummy(self, analyzer):
        """Dummy test."""
        assert analyzer is not None
