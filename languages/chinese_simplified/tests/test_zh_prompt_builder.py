"""Chinese Simplified prompt builder tests."""

from ..domain.zh_config import ZhConfig
from ..domain.zh_prompt_builder import ZhPromptBuilder


def test_build_single_prompt():
    builder = ZhPromptBuilder(ZhConfig())
    prompt = builder.build_single_prompt("你好", "你好", "beginner")
    assert isinstance(prompt, str)
