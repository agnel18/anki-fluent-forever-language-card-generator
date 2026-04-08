"""Malayalam prompt builder tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.malayalam.domain.ml_config import MlConfig
from languages.malayalam.domain.ml_prompt_builder import MlPromptBuilder


def test_prompt_builder_creation():
    config = MlConfig()
    builder = MlPromptBuilder(config)
    assert builder is not None


def test_single_prompt_generation():
    config = MlConfig()
    builder = MlPromptBuilder(config)
    prompt = builder.build_single_prompt("ഞാൻ വെള്ളം കുടിക്കുന്നു", "കുടിക്കുക", "beginner")
    assert isinstance(prompt, str)
    assert "ഞാൻ വെള്ളം കുടിക്കുന്നു" in prompt
    assert "കുടിക്കുക" in prompt


def test_batch_prompt_generation():
    config = MlConfig()
    builder = MlPromptBuilder(config)
    sentences = ["ഞാൻ വെള്ളം കുടിക്കുന്നു", "കുട്ടികൾ സ്കൂളിൽ പഠിക്കുന്നു", "അവൾ പുസ്തകം വായിച്ചു"]
    prompt = builder.build_batch_prompt(sentences, "വെള്ളം", "beginner")
    assert isinstance(prompt, str)
    assert "ഞാൻ വെള്ളം കുടിക്കുന്നു" in prompt


def test_prompt_contains_complexity():
    config = MlConfig()
    builder = MlPromptBuilder(config)
    prompt = builder.build_single_prompt("ഞാൻ കഴിക്കുന്നു", "കഴിക്കുക", "intermediate")
    assert isinstance(prompt, str)
    assert "intermediate" in prompt.lower()


def test_prompt_roles_list():
    config = MlConfig()
    builder = MlPromptBuilder(config)
    roles = builder._get_grammatical_roles_list("beginner")
    assert isinstance(roles, str)
    assert len(roles) > 0
    assert "noun" in roles or "verb" in roles


def test_prompt_roles_increase_with_complexity():
    config = MlConfig()
    builder = MlPromptBuilder(config)
    beginner = builder._get_grammatical_roles_list("beginner")
    intermediate = builder._get_grammatical_roles_list("intermediate")
    advanced = builder._get_grammatical_roles_list("advanced")
    assert len(advanced) >= len(intermediate) >= len(beginner)
