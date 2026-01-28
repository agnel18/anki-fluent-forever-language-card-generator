# tests/conftest.py
"""
Pytest configuration for {Language} analyzer tests.

GOLD STANDARD TESTING SETUP:
This configuration follows the patterns used by Chinese Simplified and Hindi analyzers.
It provides fixtures and configuration for comprehensive testing.

CONFIGURATION FEATURES:
- Test data fixtures (sample sentences, expected results)
- Mock AI responses for consistent testing
- Gold standard result loading for comparison
- Performance benchmarking setup
- Coverage and reporting configuration

INTEGRATION:
- Used by run_all_tests.py for comprehensive execution
- Supports parallel test execution
- Provides fixtures for all test types (unit, integration, system)
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock
# from languages.{language}.{language}_analyzer import {Language}Analyzer
# from languages.{language}.{language}_config import {Language}Config


@pytest.fixture(scope="session")
def test_data_dir():
    """Directory containing test data files."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_sentences():
    """Load sample test sentences for the language."""
    test_data = {
        "simple": [
            "Hello world",
            "The cat sits",
            "I eat food"
        ],
        "intermediate": [
            "The quick brown fox jumps over the lazy dog",
            "She reads interesting books every day",
            "We visited the beautiful museum yesterday"
        ],
        "complex": [
            "The sophisticated algorithm processes complex linguistic patterns with remarkable efficiency",
            "Despite numerous challenges, the research team achieved breakthrough results",
            "Multiple factors contribute to the phenomenon's observed characteristics"
        ]
    }
    return test_data


@pytest.fixture(scope="session")
def mock_ai_responses():
    """Mock AI responses for consistent testing."""
    return {
        "simple_success": {
            "sentence": "Hello world",
            "words": [
                {"word": "Hello", "grammatical_role": "interjection", "individual_meaning": "greeting"},
                {"word": "world", "grammatical_role": "noun", "individual_meaning": "the earth or everyone"}
            ],
            "explanations": {
                "overall_structure": "Simple greeting sentence",
                "key_features": "Basic subject-complement structure"
            }
        },
        "error_response": {
            "error": "API temporarily unavailable"
        },
        "malformed_response": "Invalid JSON response"
    }


@pytest.fixture(scope="session")
def gold_standard_results():
    """Load gold standard test results for comparison."""
    # This would load results from Chinese Simplified and Hindi analyzers
    # for comparison testing
    gold_standards = {
        "zh": {
            "sentence": "你好世界",
            "word_explanations": [
                ["你好", "interjection", "#FFEAA7", "greeting"],
                ["世界", "noun", "#FFAA00", "the world"]
            ],
            "confidence": 0.95
        },
        "hi": {
            "sentence": "नमस्ते दुनिया",
            "word_explanations": [
                ["नमस्ते", "interjection", "#FFEAA7", "greeting"],
                ["दुनिया", "noun", "#FFAA00", "the world"]
            ],
            "confidence": 0.92
        }
    }
    return gold_standards


@pytest.fixture
def analyzer():
    """Create analyzer instance for testing."""
    # return {Language}Analyzer()
    return Mock()  # Replace with actual analyzer


@pytest.fixture
def config():
    """Create config instance for testing."""
    # return {Language}Config()
    return Mock()  # Replace with actual config


@pytest.fixture
def mock_ai_call():
    """Mock AI call for testing."""
    def _mock_response(*args, **kwargs):
        return json.dumps({
            "sentence": "Test sentence",
            "words": [
                {"word": "Test", "grammatical_role": "noun", "individual_meaning": "a trial"},
                {"word": "sentence", "grammatical_role": "noun", "individual_meaning": "a grammatical unit"}
            ],
            "explanations": {
                "overall_structure": "Simple noun phrase",
                "key_features": "Basic grammatical structure"
            }
        })
    return _mock_response


@pytest.fixture
def performance_benchmark():
    """Performance benchmarking fixture."""
    import time

    class BenchmarkTimer:
        def __enter__(self):
            self.start = time.perf_counter()
            return self

        def __exit__(self, *args):
            self.duration = time.perf_counter() - self.start

    return BenchmarkTimer()


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests for component interaction")
    config.addinivalue_line("markers", "system: End-to-end system tests")
    config.addinivalue_line("markers", "performance: Performance and benchmarking tests")
    config.addinivalue_line("markers", "gold_standard: Tests comparing with gold standard analyzers")
    config.addinivalue_line("markers", "regression: Tests preventing bug reintroduction")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on file naming."""
    for item in items:
        if "test_" in item.nodeid:
            if "integration" in item.nodeid:
                item.add_marker(pytest.mark.integration)
            elif "system" in item.nodeid:
                item.add_marker(pytest.mark.system)
            elif "performance" in item.nodeid:
                item.add_marker(pytest.mark.performance)
            elif "gold_standard" in item.nodeid:
                item.add_marker(pytest.mark.gold_standard)
            elif "regression" in item.nodeid:
                item.add_marker(pytest.mark.regression)
            else:
                item.add_marker(pytest.mark.unit)


# Coverage configuration
@pytest.fixture(scope="session", autouse=True)
def configure_coverage():
    """Configure coverage settings."""
    if "COVERAGE_PROCESS_START" in os.environ:
        import coverage
        coverage.process_startup()


# Custom test result recording
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Record test results for reporting."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        # Store result for aggregation
        test_results = getattr(item.config, "_test_results", [])
        test_results.append({
            "nodeid": item.nodeid,
            "outcome": report.outcome,
            "duration": report.duration,
            "markers": [m.name for m in item.own_markers]
        })
        item.config._test_results = test_results