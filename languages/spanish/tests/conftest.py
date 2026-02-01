# Pytest configuration for Spanish analyzer tests
import pytest
import sys
import os

# Add the project root to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Add streamlit_app to path for shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'streamlit_app'))

@pytest.fixture
def spanish_config():
    """Fixture providing Spanish configuration for tests"""
    from ..domain.es_config import EsConfig
    return EsConfig()

@pytest.fixture
def spanish_analyzer():
    """Fixture providing Spanish analyzer instance for tests"""
    from ..es_analyzer import EsAnalyzer
    return EsAnalyzer()