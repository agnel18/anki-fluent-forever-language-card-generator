# languages/english/tests/conftest.py
"""
Pytest fixtures for English analyzer tests.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.english.domain.en_config import EnConfig
from languages.english.domain.en_fallbacks import EnFallbacks
from languages.english.domain.en_prompt_builder import EnPromptBuilder
from languages.english.domain.en_response_parser import EnResponseParser
from languages.english.domain.en_validator import EnValidator


@pytest.fixture
def config():
    return EnConfig()


@pytest.fixture
def fallbacks(config):
    return EnFallbacks(config)


@pytest.fixture
def prompt_builder(config):
    return EnPromptBuilder(config)


@pytest.fixture
def response_parser(config, fallbacks):
    return EnResponseParser(config, fallbacks)


@pytest.fixture
def validator(config):
    return EnValidator(config)


# ---------------------------------------------------------------------------
# Sample AI responses
# ---------------------------------------------------------------------------

SAMPLE_BEGINNER_RESPONSE = "{}"

SAMPLE_INTERMEDIATE_RESPONSE = "{}"

SAMPLE_ADVANCED_RESPONSE = "{}"
