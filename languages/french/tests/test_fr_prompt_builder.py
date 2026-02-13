"""French prompt builder tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.french.domain.fr_config import FrConfig
from languages.french.domain.fr_prompt_builder import FrPromptBuilder


def test_prompt_builder_creation():
    config = FrConfig()
    builder = FrPromptBuilder(config)
    assert builder is not None


def test_single_prompt_generation():
    config = FrConfig()
    builder = FrPromptBuilder(config)
    prompt = builder.build_single_prompt("Je mange une pomme", "mange", "beginner")
    assert isinstance(prompt, str)
    assert "Je mange une pomme" in prompt
    assert "mange" in prompt


def test_batch_prompt_generation():
    config = FrConfig()
    builder = FrPromptBuilder(config)
    sentences = ["Je mange", "Tu manges", "Il mange"]
    prompt = builder.build_batch_prompt(sentences, "mange", "beginner")
    assert isinstance(prompt, str)
    assert "Je mange" in prompt