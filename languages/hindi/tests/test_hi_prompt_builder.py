"""Hindi prompt builder tests."""

from ..domain.hi_config import HiConfig
from ..domain.hi_prompt_builder import HiPromptBuilder


def test_build_single_prompt():
    builder = HiPromptBuilder(HiConfig())
    prompt = builder.build_single_prompt("यह एक वाक्य है", "वाक्य", "beginner")
    assert isinstance(prompt, str)
    assert "वाक्य" in prompt
