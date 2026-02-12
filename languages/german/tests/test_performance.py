
"""
Performance tests for de analyzer.
"""

import pytest
from languages.german.de_analyzer import DeAnalyzer


class TestDeAnalyzerPerformance:
    """Performance tests for analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer for testing."""
        return DeAnalyzer()

    def test_dummy(self, analyzer):
        """Dummy test."""
        assert analyzer is not None
