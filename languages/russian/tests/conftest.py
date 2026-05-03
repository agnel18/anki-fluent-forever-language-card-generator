# languages/russian/tests/conftest.py
"""
Pytest fixtures for Russian analyzer tests.
"""
import pytest
from unittest.mock import MagicMock, patch

from languages.russian.domain.ru_config import RuConfig
from languages.russian.domain.ru_fallbacks import RuFallbacks
from languages.russian.domain.ru_prompt_builder import RuPromptBuilder
from languages.russian.domain.ru_response_parser import RuResponseParser
from languages.russian.domain.ru_validator import RuValidator


@pytest.fixture
def config():
    return RuConfig()


@pytest.fixture
def fallbacks(config):
    return RuFallbacks(config)


@pytest.fixture
def prompt_builder(config):
    return RuPromptBuilder(config)


@pytest.fixture
def response_parser(config, fallbacks):
    return RuResponseParser(config, fallbacks)


@pytest.fixture
def validator(config):
    return RuValidator(config)


# ---------------------------------------------------------------------------
# Sample AI responses
# ---------------------------------------------------------------------------

SAMPLE_BEGINNER_RESPONSE = "{}"

SAMPLE_INTERMEDIATE_RESPONSE = "{}"

SAMPLE_ADVANCED_RESPONSE = "{}"
