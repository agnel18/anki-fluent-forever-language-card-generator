
"""
Performance tests for arabic analyzer.
"""

import pytest
from languages.arabic.ar_analyzer import ArAnalyzer


class TestArAnalyzerPerformance:
    """Performance tests for analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return ArAnalyzer()

    def test_dummy(self, analyzer):
        """Dummy test."""
        assert analyzer is not None
