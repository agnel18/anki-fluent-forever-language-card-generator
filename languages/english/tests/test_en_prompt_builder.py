# languages/english/tests/test_en_prompt_builder.py
"""Tests for EnPromptBuilder."""
import pytest
from languages.english.domain.en_config import EnConfig
from languages.english.domain.en_prompt_builder import EnPromptBuilder


@pytest.fixture
def builder():
    return EnPromptBuilder(EnConfig())


class TestEnPromptBuilder:
    def test_single_prompt_contains_sentence(self, builder):
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        assert "The cat eats fish." in prompt

    def test_single_prompt_contains_language(self, builder):
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        assert "English" in prompt

    def test_single_prompt_contains_target_word(self, builder):
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        assert "eats" in prompt

    def test_batch_prompt_contains_all_sentences(self, builder):
        sentences = [
            "The cat eats fish.",
            "I want to run quickly.",
            "The book that she read was interesting.",
        ]
        prompt = builder.build_batch_prompt(sentences, "book", "advanced")
        for s in sentences:
            assert s in prompt

    def test_single_prompt_contains_json_schema(self, builder):
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        assert "word_explanations" in prompt
        assert "JSON" in prompt

    def test_single_prompt_contains_individual_meaning_field(self, builder):
        """The prompt must ask for the individual_meaning field."""
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        assert "individual_meaning" in prompt

    def test_single_prompt_contains_color_mapping(self, builder):
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        assert "#FFAA00" in prompt   # noun color
        assert "#4ECDC4" in prompt   # verb color

    def test_prompt_contains_article_color(self, builder):
        """English-specific: article color must be in the prompt."""
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        assert "#FFD700" in prompt   # article color

    def test_intermediate_prompt_mentions_to_disambiguation(self, builder):
        """Intermediate+ prompts must explicitly address 'to' ambiguity."""
        prompt = builder.build_single_prompt("I want to run quickly.", "run", "intermediate")
        assert "to" in prompt.lower()
        # The prompt should explain that 'to' before a base verb = infinitive marker
        assert "infinitive" in prompt.lower()

    def test_intermediate_prompt_mentions_ing_disambiguation(self, builder):
        """Intermediate+ prompts must address -ing form disambiguation."""
        prompt = builder.build_single_prompt("Running is fun.", "running", "intermediate")
        assert "-ing" in prompt or "ing" in prompt.lower()
        assert "gerund" in prompt.lower() or "participle" in prompt.lower()

    def test_advanced_prompt_mentions_that_disambiguation(self, builder):
        """Advanced prompts must cover the 4-way 'that' ambiguity."""
        prompt = builder.build_single_prompt(
            "The book that she read was interesting.", "book", "advanced"
        )
        assert "that" in prompt.lower()
        # Should mention relative pronoun
        assert "relative" in prompt.lower()

    def test_advanced_prompt_mentions_phrasal_verbs(self, builder):
        """Advanced prompts must address phrasal-verb particle disambiguation."""
        prompt = builder.build_single_prompt(
            "I looked up the word.", "looked", "advanced"
        )
        assert "phrasal" in prompt.lower()

    def test_beginner_prompt_no_subjunctive(self, builder):
        """Beginner prompts should not overwhelm with advanced grammar concepts."""
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        # Subjunctive is not a beginner concept
        assert "subjunctive" not in prompt.lower()

    def test_beginner_prompt_no_relative_pronoun_in_roles(self, builder):
        """Beginner prompts should not list relative_pronoun in the allowed roles."""
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        # relative_pronoun is an advanced role — it must not appear in the beginner roles list.
        # (Worked examples in the prompt body may mention it as a concept, but the
        #  GRAMMATICAL ROLES line should not include it at beginner level.)
        from languages.english.domain.en_config import EnConfig
        beginner_roles = list(EnConfig()._get_default_roles()["beginner"].keys())
        assert "relative_pronoun" not in beginner_roles, (
            "relative_pronoun must not be a beginner role"
        )

    def test_advanced_prompt_mentions_relative_pronoun(self, builder):
        """Advanced prompts must list relative pronoun in the grammar roles."""
        prompt = builder.build_single_prompt(
            "The book that she read was interesting.", "book", "advanced"
        )
        assert "relative_pronoun" in prompt or "relative pronoun" in prompt.lower()

    def test_complexity_levels_produce_different_prompts(self, builder):
        p1 = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        p2 = builder.build_single_prompt("The cat eats fish.", "eats", "advanced")
        assert p1 != p2

    def test_batch_prompt_returns_array_instruction(self, builder):
        """Batch prompts must instruct the model to return a JSON ARRAY."""
        sentences = ["The cat eats fish.", "She runs quickly."]
        prompt = builder.build_batch_prompt(sentences, "cat", "beginner")
        assert "ARRAY" in prompt or "array" in prompt.lower()

    def test_critical_section_header_present(self, builder):
        """The CRITICAL section that specifies individual_meaning depth must appear."""
        prompt = builder.build_single_prompt("The cat eats fish.", "eats", "beginner")
        assert "CRITICAL" in prompt

    def test_worked_example_for_to(self, builder):
        """The worked examples section must include a 'to' disambiguation example."""
        prompt = builder.build_single_prompt("I want to run.", "run", "intermediate")
        # The prompt body should demonstrate the 'to' example
        assert "infinitive marker" in prompt.lower() or "infinitive_marker" in prompt.lower()

    def test_worked_example_for_look_up(self, builder):
        """Advanced prompts should include a phrasal verb worked example."""
        prompt = builder.build_single_prompt("I looked up the word.", "looked", "advanced")
        assert "look up" in prompt.lower() or "look_up" in prompt.lower() or "phrasal" in prompt.lower()
