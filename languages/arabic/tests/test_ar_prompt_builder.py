import pytest

class TestArabicPromptBuilder:
    """Test Arabic prompt builder component"""

    def test_initialization(self, arabic_prompt_builder, arabic_config):
        """Test prompt builder initializes correctly"""
        assert arabic_prompt_builder.config == arabic_config
        assert arabic_prompt_builder.single_template is not None
        assert arabic_prompt_builder.batch_template is not None

    def test_single_prompt_generation(self, arabic_prompt_builder, sample_arabic_sentences):
        """Test single sentence prompt generation"""
        sentence = sample_arabic_sentences['beginner']['simple'][0]
        target_word = "قطة"
        complexity = "beginner"

        prompt = arabic_prompt_builder.build_single_prompt(sentence, target_word, complexity)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert sentence in prompt
        assert target_word in prompt
        assert complexity in prompt
        assert "Arabic" in prompt
        assert "RIGHT TO LEFT" in prompt  # RTL instruction

    def test_batch_prompt_generation(self, arabic_prompt_builder, sample_arabic_sentences):
        """Test batch prompt generation"""
        sentences = sample_arabic_sentences['beginner']['simple'][:2]
        target_word = "test"
        complexity = "beginner"

        prompt = arabic_prompt_builder.build_batch_prompt(sentences, target_word, complexity)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        for sentence in sentences:
            assert sentence in prompt

    def test_arabic_text_validation(self, arabic_prompt_builder):
        """Test Arabic text validation in prompt builder"""
        assert arabic_prompt_builder.validate_arabic_text("مرحبا") == True
        assert arabic_prompt_builder.validate_arabic_text("Hello") == False

    @pytest.mark.parametrize("complexity", ["beginner", "intermediate", "advanced"])
    def test_complexity_specific_instructions(self, arabic_prompt_builder, complexity):
        """Test complexity-specific prompt instructions"""
        instructions = arabic_prompt_builder.get_complexity_specific_instructions(complexity)

        assert isinstance(instructions, str)
        assert len(instructions) > 0

        # Check complexity-specific content
        if complexity == "beginner":
            assert "basic word classes" in instructions.lower()
        elif complexity == "intermediate":
            assert "case markings" in instructions.lower()
        elif complexity == "advanced":
            assert "root-based morphology" in instructions.lower()

    def test_grammatical_roles_formatting(self, arabic_prompt_builder):
        """Test grammatical roles formatting for prompts"""
        roles = arabic_prompt_builder._format_grammatical_roles("beginner")

        assert isinstance(roles, str)
        assert len(roles) > 0
        assert "noun:" in roles
        assert "verb:" in roles
        # Should contain Arabic terms
        assert "اسم" in roles or "فعل" in roles