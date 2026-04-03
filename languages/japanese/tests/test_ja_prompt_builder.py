"""Japanese prompt builder tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.japanese.domain.ja_config import JaConfig
from languages.japanese.domain.ja_prompt_builder import JaPromptBuilder


def test_prompt_builder_creation():
    config = JaConfig()
    builder = JaPromptBuilder(config)
    assert builder is not None


def test_single_prompt_generation():
    config = JaConfig()
    builder = JaPromptBuilder(config)
    prompt = builder.build_single_prompt("私は本を読む", "読む", "beginner")
    assert isinstance(prompt, str)
    assert "私は本を読む" in prompt
    assert "読む" in prompt


def test_batch_prompt_generation():
    config = JaConfig()
    builder = JaPromptBuilder(config)
    sentences = ["私は本を読む", "猫が好きです", "東京に行きます"]
    prompt = builder.build_batch_prompt(sentences, "本", "beginner")
    assert isinstance(prompt, str)
    assert "私は本を読む" in prompt


def test_prompt_contains_complexity():
    config = JaConfig()
    builder = JaPromptBuilder(config)
    prompt = builder.build_single_prompt("食べます", "食べる", "intermediate")
    assert isinstance(prompt, str)
    assert "intermediate" in prompt.lower() or "中級" in prompt


def test_prompt_roles_list():
    config = JaConfig()
    builder = JaPromptBuilder(config)
    roles = builder._get_grammatical_roles_list("beginner")
    assert isinstance(roles, str)
    assert len(roles) > 0
    assert "noun" in roles or "verb" in roles


def test_prompt_roles_increase_with_complexity():
    config = JaConfig()
    builder = JaPromptBuilder(config)
    beginner = builder._get_grammatical_roles_list("beginner")
    intermediate = builder._get_grammatical_roles_list("intermediate")
    advanced = builder._get_grammatical_roles_list("advanced")
    assert len(advanced) >= len(intermediate) >= len(beginner)
