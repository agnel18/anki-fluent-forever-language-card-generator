
"""
Performance tests for tr analyzer.
"""

import pytest
from languages.turkish.tr_analyzer import TrAnalyzer


class TestTrAnalyzerPerformance:
    """Performance tests for analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return TrAnalyzer()

    def test_dummy(self, analyzer):
        """Dummy test."""
        assert analyzer is not None
