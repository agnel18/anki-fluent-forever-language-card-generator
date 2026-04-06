"""Korean prompt builder tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.korean.domain.ko_config import KoConfig
from languages.korean.domain.ko_prompt_builder import KoPromptBuilder


def test_prompt_builder_creation():
    config = KoConfig()
    builder = KoPromptBuilder(config)
    assert builder is not None


def test_single_prompt_generation():
    config = KoConfig()
    builder = KoPromptBuilder(config)
    prompt = builder.build_single_prompt("저는 학생입니다.", "학생", "beginner")
    assert isinstance(prompt, str)
    assert "저는 학생입니다." in prompt
    assert "학생" in prompt


def test_batch_prompt_generation():
    config = KoConfig()
    builder = KoPromptBuilder(config)
    sentences = ["저는 학생입니다.", "오늘 날씨가 좋아요.", "한국어를 배우고 있어요."]
    prompt = builder.build_batch_prompt(sentences, "학생", "beginner")
    assert isinstance(prompt, str)
    assert "저는 학생입니다." in prompt


def test_prompt_contains_complexity():
    config = KoConfig()
    builder = KoPromptBuilder(config)
    prompt = builder.build_single_prompt("밥을 먹어요.", "먹다", "intermediate")
    assert isinstance(prompt, str)
    assert "intermediate" in prompt.lower()


def test_prompt_roles_list():
    config = KoConfig()
    builder = KoPromptBuilder(config)
    roles = builder._get_grammatical_roles_list("beginner")
    assert isinstance(roles, str)
    assert len(roles) > 0
    assert "noun" in roles or "verb" in roles


def test_prompt_roles_increase_with_complexity():
    config = KoConfig()
    builder = KoPromptBuilder(config)
    beginner = builder._get_grammatical_roles_list("beginner")
    intermediate = builder._get_grammatical_roles_list("intermediate")
    advanced = builder._get_grammatical_roles_list("advanced")
    assert len(advanced) >= len(intermediate) >= len(beginner)
