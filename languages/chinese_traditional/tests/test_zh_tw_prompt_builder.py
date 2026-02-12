"""Chinese Traditional prompt builder tests."""

from ..domain.zh_tw_config import ZhTwConfig
from ..domain.zh_tw_prompt_builder import ZhTwPromptBuilder


def test_build_single_prompt():
    builder = ZhTwPromptBuilder(ZhTwConfig())
    prompt = builder.build_single_prompt("你好", "你好", "beginner")
    assert isinstance(prompt, str)
