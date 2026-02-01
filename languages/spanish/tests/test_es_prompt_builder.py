# Test Spanish Prompt Builder
# Tests for EsPromptBuilder class

import pytest
from ..domain.es_config import EsConfig
from ..domain.es_prompt_builder import EsPromptBuilder

class TestEsPromptBuilder:
    """Tests for Spanish prompt builder"""

    @pytest.fixture
    def config(self):
        return EsConfig()

    @pytest.fixture
    def prompt_builder(self, config):
        return EsPromptBuilder(config)

    def test_initialization(self, prompt_builder, config):
        """Test prompt builder initializes correctly"""
        assert prompt_builder.config == config
        assert prompt_builder.single_template is not None
        assert prompt_builder.batch_template is not None

    def test_single_prompt_generation(self, prompt_builder):
        """Test single sentence prompt generation"""
        sentence = "El gato come pescado"
        target_word = "gato"
        complexity = "beginner"

        prompt = prompt_builder.build_single_prompt(sentence, target_word, complexity)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert sentence in prompt
        assert target_word in prompt
        assert complexity in prompt
        assert "JSON" in prompt  # Should contain JSON format instructions

    def test_batch_prompt_generation(self, prompt_builder):
        """Test batch sentence prompt generation"""
        sentences = ["El gato come", "La casa es grande"]
        target_word = "casa"
        complexity = "intermediate"

        prompt = prompt_builder.build_batch_prompt(sentences, target_word, complexity)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "El gato come" in prompt
        assert "La casa es grande" in prompt
        assert target_word in prompt
        assert complexity in prompt

    def test_complexity_instructions(self, prompt_builder):
        """Test complexity-specific instructions"""
        beginner_instructions = prompt_builder.get_complexity_specific_instructions("beginner")
        assert "basic word classes" in beginner_instructions
        assert "nouns (sustantivos)" in beginner_instructions

        intermediate_instructions = prompt_builder.get_complexity_specific_instructions("intermediate")
        assert "gender/number agreement" in intermediate_instructions
        assert "ser/estar distinction" in intermediate_instructions

        advanced_instructions = prompt_builder.get_complexity_specific_instructions("advanced")
        assert "clitic pronouns" in advanced_instructions
        assert "subjunctive mood" in advanced_instructions

    def test_spanish_text_validation(self, prompt_builder):
        """Test Spanish text validation"""
        assert prompt_builder.validate_spanish_text("Hola, ¿cómo estás?")
        assert not prompt_builder.validate_spanish_text("Hello world")

    def test_text_preparation(self, prompt_builder):
        """Test text preparation for analysis"""
        text = "  El gato come pescado  "
        prepared = prompt_builder.prepare_text_for_analysis(text)
        assert prepared == "El gato come pescado"