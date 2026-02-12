
"""
Performance tests for es analyzer.
"""

import pytest
from languages.spanish.es_analyzer import EsAnalyzer


class TestEsAnalyzerPerformance:
    """Performance tests for analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return EsAnalyzer()

    def test_dummy(self, analyzer):
        """Dummy test."""
        assert analyzer is not None
