"""German prompt builder tests."""

from ..domain.de_config import DeConfig
from ..domain.de_prompt_builder import DePromptBuilder


def test_build_single_prompt():
    builder = DePromptBuilder(DeConfig())
    prompt = builder.build_single_prompt("Das ist ein Test", "Test", "beginner")
    assert isinstance(prompt, str)
    assert "Test" in prompt
