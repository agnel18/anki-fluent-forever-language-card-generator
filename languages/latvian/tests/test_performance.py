
"""
Performance tests for lv analyzer.
"""

import pytest
from languages.latvian.lv_analyzer import LvAnalyzer


class TestLvAnalyzerPerformance:
    """Performance tests for analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return LvAnalyzer()

    def test_dummy(self, analyzer):
        """Dummy test."""
        assert analyzer is not None
