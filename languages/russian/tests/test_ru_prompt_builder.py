# languages/russian/tests/test_ru_prompt_builder.py
"""
Tests for RuPromptBuilder (Russian prompt construction).
"""
import pytest
from languages.russian.domain.ru_config import RuConfig
from languages.russian.domain.ru_prompt_builder import RuPromptBuilder


@pytest.fixture
def builder():
    return RuPromptBuilder(RuConfig())


class TestRuPromptBuilderSingle:
    def test_single_prompt_contains_sentence(self, builder):
        sentence = "Я читаю книгу."
        prompt = builder.build_single_prompt(sentence, "читаю", "beginner")
        assert sentence in prompt

    def test_single_prompt_cyrillic_sentence(self, builder):
        sentence = "Мне нужно написать письмо."
        prompt = builder.build_single_prompt(sentence, "написать", "intermediate")
        assert sentence in prompt

    def test_single_prompt_advanced_cyrillic(self, builder):
        sentence = "Книга, которую она читала, была интересной."
        prompt = builder.build_single_prompt(sentence, "которую", "advanced")
        assert sentence in prompt

    def test_single_prompt_non_empty(self, builder):
        prompt = builder.build_single_prompt("Я читаю.", "читаю", "beginner")
        assert len(prompt) > 100

    def test_single_prompt_contains_individual_meaning_schema(self, builder):
        """Prompt must request the individual_meaning field."""
        prompt = builder.build_single_prompt("Я читаю книгу.", "читаю", "beginner")
        assert "individual_meaning" in prompt

    def test_single_prompt_contains_json_schema(self, builder):
        """Prompt must include a JSON schema block."""
        prompt = builder.build_single_prompt("Я читаю книгу.", "читаю", "beginner")
        assert "word_explanations" in prompt

    def test_single_prompt_contains_color_mapping(self, builder):
        """Prompt must contain the color mapping for Russian roles."""
        prompt = builder.build_single_prompt("Я читаю книгу.", "читаю", "beginner")
        # Check for a few canonical Russian colors
        assert "#FFAA00" in prompt  # noun
        assert "#4ECDC4" in prompt  # verb

    def test_single_prompt_contains_critical_section(self, builder):
        """Prompt must contain a CRITICAL instruction section."""
        prompt = builder.build_single_prompt("Я читаю книгу.", "читаю", "beginner")
        assert "CRITICAL" in prompt

    def test_single_prompt_contains_cyrillic_examples(self, builder):
        """Prompt body should contain the canonical Cyrillic worked examples."""
        prompt = builder.build_single_prompt("Я читаю книгу.", "читаю", "intermediate")
        # These examples are hardcoded in the prompt builder
        assert "читаю" in prompt  # Example sentence: Я читаю интересную книгу
        assert "написал" in prompt  # Example sentence: Я написал письмо
        assert "открылась" in prompt  # Example sentence: Дверь открылась
        assert "идём" in prompt  # Example sentence: Мы идём в школу

    def test_beginner_prompt_does_not_mention_participle_roles(self, builder):
        """At beginner level, advanced roles like participle should not appear in role list."""
        prompt = builder.build_single_prompt("Я читаю.", "читаю", "beginner")
        # The beginner role list should not contain participle sub-types
        # (it collapses them to verb)
        assert "present_active_participle" not in prompt
        assert "past_passive_participle" not in prompt

    def test_advanced_prompt_mentions_participles(self, builder):
        """At advanced level, participle sub-types must appear in role list."""
        prompt = builder.build_single_prompt("Книга написана.", "написана", "advanced")
        assert "participle" in prompt.lower()

    def test_advanced_prompt_mentions_reflexive_verbs_of_motion(self, builder):
        """At advanced level, the prompt should mention reflexive -ся and verbs of motion."""
        prompt = builder.build_single_prompt("Мы идём в школу.", "идём", "advanced")
        assert "рефлекс" in prompt.lower() or "reflexive" in prompt.lower() or "-ся" in prompt
        assert "motion" in prompt.lower() or "движен" in prompt.lower()

    def test_russian_specific_notes_present(self, builder):
        """The Russian-specific mandatory rules must be in every prompt."""
        for level in ("beginner", "intermediate", "advanced"):
            prompt = builder.build_single_prompt("Я читаю.", "читаю", level)
            assert "6" in prompt or "nominative" in prompt.lower()
            assert "aspect" in prompt.lower()


class TestRuPromptBuilderBatch:
    def test_batch_prompt_contains_all_sentences(self, builder):
        sentences = ["Я читаю.", "Она пишет.", "Мы говорим."]
        prompt = builder.build_batch_prompt(sentences, "читаю", "beginner")
        for s in sentences:
            assert s in prompt

    def test_batch_prompt_cyrillic_sentences(self, builder):
        sentences = [
            "Мне нужно написать письмо.",
            "Книга, которую она читала, была интересной.",
        ]
        prompt = builder.build_batch_prompt(sentences, "книга", "advanced")
        for s in sentences:
            assert s in prompt

    def test_batch_prompt_non_empty(self, builder):
        prompt = builder.build_batch_prompt(["Я читаю."], "читаю", "beginner")
        assert len(prompt) > 100

    def test_batch_prompt_contains_individual_meaning(self, builder):
        prompt = builder.build_batch_prompt(["Я читаю.", "Она пишет."], "читаю", "intermediate")
        assert "individual_meaning" in prompt

    def test_batch_prompt_batch_mode_instruction(self, builder):
        """Batch prompt must instruct the model to return an array."""
        sentences = ["Я читаю.", "Она пишет."]
        prompt = builder.build_batch_prompt(sentences, "читаю", "intermediate")
        # The batch prompt should mention array / multiple sentences
        assert "ARRAY" in prompt or "array" in prompt or str(len(sentences)) in prompt

    def test_batch_prompt_with_list_target_words(self, builder):
        """build_batch_prompt accepts both string and list target_words."""
        sentences = ["Я читаю.", "Она пишет."]
        prompt_str = builder.build_batch_prompt(sentences, "читаю", "beginner")
        prompt_list = builder.build_batch_prompt(sentences, ["читаю", "пишет"], "beginner")
        # Both should produce valid prompts containing the sentences
        for s in sentences:
            assert s in prompt_str
            assert s in prompt_list
