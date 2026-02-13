"""French analyzer integration tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.french.fr_analyzer import FrAnalyzer


def test_analyzer_integration():
    """Test that all components work together."""
    analyzer = FrAnalyzer()

    # Test that all components are properly initialized
    assert analyzer.config is not None
    assert analyzer.prompt_builder is not None
    assert analyzer.response_parser is not None
    assert analyzer.validator is not None

    # Test that config has required attributes
    assert hasattr(analyzer.config, 'name')
    assert hasattr(analyzer.config, 'code')
    assert hasattr(analyzer.config, 'supported_complexity_levels')