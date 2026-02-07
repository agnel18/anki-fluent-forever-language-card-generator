"""
Pytest configuration and fixtures for the language learning app tests.
"""

import os
import sys
import warnings
import pytest

# Add the streamlit_app directory to the Python path
streamlit_app_path = os.path.join(os.path.dirname(__file__), '..', 'streamlit_app')
sys.path.insert(0, streamlit_app_path)

# Set up environment variables for testing
os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')

# Silence third-party deprecations during tests
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"google\.genai\..*")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment."""
    # Ensure we're in the right directory
    test_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(test_dir)
    os.chdir(project_root)

    yield

    # Cleanup if needed
    pass