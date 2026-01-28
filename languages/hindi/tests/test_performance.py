
"""
Performance tests for hi analyzer.
"""

import pytest
from languages.hindi.hi_analyzer import HiAnalyzer


class TestHiAnalyzerPerformance:
    """Performance tests for analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return HiAnalyzer()

    def test_dummy(self, analyzer):
        """Dummy test."""
        assert analyzer is not None
