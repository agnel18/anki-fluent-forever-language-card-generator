"""Hungarian prompt builder tests."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.hungarian.domain.hu_config import HuConfig
from languages.hungarian.domain.hu_prompt_builder import HuPromptBuilder


def test_prompt_builder_creation():
    config = HuConfig()
    builder = HuPromptBuilder(config)
    assert builder is not None


def test_single_prompt_beginner():
    config = HuConfig()
    builder = HuPromptBuilder(config)
    prompt = builder.build_single_prompt("A fiú almát eszik.", "eszik", "beginner")
    assert isinstance(prompt, str)
    assert "A fiú almát eszik." in prompt
    assert "eszik" in prompt
    assert "beginner" in prompt


def test_single_prompt_intermediate():
    config = HuConfig()
    builder = HuPromptBuilder(config)
    prompt = builder.build_single_prompt("Megírtam a levelet.", "megír", "intermediate")
    assert isinstance(prompt, str)
    assert "Megírtam a levelet." in prompt
    assert "intermediate" in prompt


def test_single_prompt_advanced():
    config = HuConfig()
    builder = HuPromptBuilder(config)
    prompt = builder.build_single_prompt(
        "A barátomnak adnám a könyvemet, ha kérné.",
        "kér",
        "advanced"
    )
    assert isinstance(prompt, str)
    assert "advanced" in prompt


def test_batch_prompt():
    config = HuConfig()
    builder = HuPromptBuilder(config)
    sentences = [
        "A fiú almát eszik.",
        "Minden nap tanulok magyarul.",
        "A könyvet a polcra tettem."
    ]
    prompt = builder.build_batch_prompt(sentences, "tanul", "intermediate")
    assert isinstance(prompt, str)
    assert "1." in prompt
    assert "2." in prompt
    assert "3." in prompt


def test_prompt_contains_hungarian_grammar_terms():
    config = HuConfig()
    builder = HuPromptBuilder(config)
    prompt = builder.build_single_prompt("A macska az asztalon ül.", "ül", "intermediate")
    # Should mention Hungarian-specific concepts
    assert any(term in prompt.lower() for term in ['case', 'conjugat', 'preverb', 'postposition', 'vowel harmony'])


def test_grammatical_roles_list_beginner():
    config = HuConfig()
    builder = HuPromptBuilder(config)
    roles = builder._get_grammatical_roles_list("beginner")
    assert "noun" in roles
    assert "verb" in roles
    assert "preverb" in roles
    assert "postposition" in roles


def test_grammatical_roles_list_advanced():
    config = HuConfig()
    builder = HuPromptBuilder(config)
    roles = builder._get_grammatical_roles_list("advanced")
    assert "causative verb" in roles
    assert "potential verb" in roles
    assert "possessive suffix" in roles
    assert "essive formal" in roles
    assert "terminative" in roles


def test_fallback_prompt_on_error():
    """Prompt builder should return a basic fallback prompt if template rendering fails."""
    config = HuConfig()
    builder = HuPromptBuilder(config)
    # Force a bad template
    builder.single_template = None
    prompt = builder.build_single_prompt("Test sentence.", "test", "beginner")
    assert isinstance(prompt, str)
    assert len(prompt) > 10
