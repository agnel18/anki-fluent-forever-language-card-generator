# languages/portuguese/tests/test_pt_prompt_builder.py
"""Tests for PtPromptBuilder — Portuguese prompt construction."""
import pytest
from languages.portuguese.domain.pt_config import PtConfig
from languages.portuguese.domain.pt_prompt_builder import PtPromptBuilder


@pytest.fixture
def builder():
    return PtPromptBuilder(PtConfig())


class TestPtPromptBuilderSingle:
    def test_single_prompt_contains_sentence(self, builder):
        prompt = builder.build_single_prompt("O gato bebe leite.", "gato", "beginner")
        assert "O gato bebe leite." in prompt

    def test_single_prompt_contains_target_word(self, builder):
        prompt = builder.build_single_prompt("O gato bebe leite.", "gato", "beginner")
        assert "gato" in prompt

    def test_single_prompt_mentions_portuguese(self, builder):
        prompt = builder.build_single_prompt("O gato bebe leite.", "gato", "beginner")
        assert "Portuguese" in prompt or "Português" in prompt

    def test_single_prompt_contains_json_schema(self, builder):
        prompt = builder.build_single_prompt("O gato bebe leite.", "gato", "beginner")
        assert "word_explanations" in prompt
        assert "JSON" in prompt

    def test_single_prompt_contains_color_mapping(self, builder):
        prompt = builder.build_single_prompt("O gato bebe leite.", "gato", "beginner")
        # Core color hex values must be present
        assert "#FFAA00" in prompt   # noun color
        assert "#44FF44" in prompt   # verb color

    def test_single_prompt_mentions_copula(self, builder):
        """Prompt should explain ser/estar distinction for all levels."""
        prompt = builder.build_single_prompt("Ela é estudante.", "é", "beginner")
        assert "copula" in prompt.lower() or "ser" in prompt.lower()

    def test_single_prompt_mentions_contractions(self, builder):
        """Prompt should explain obligatory contractions at all levels."""
        prompt = builder.build_single_prompt("Eu vou ao mercado.", "mercado", "beginner")
        assert "contraction" in prompt.lower() or "ao" in prompt

    def test_intermediate_prompt_mentions_clitics(self, builder):
        prompt = builder.build_single_prompt("Disse-me a verdade.", "verdade", "intermediate")
        assert "clitic" in prompt.lower() or "proclitic" in prompt.lower()

    def test_advanced_prompt_mentions_personal_infinitive(self, builder):
        prompt = builder.build_single_prompt(
            "Para fazermos isso, precisamos de treinar.", "fazermos", "advanced"
        )
        assert "personal infinitive" in prompt.lower() or "infinitivo pessoal" in prompt.lower()

    def test_advanced_prompt_mentions_subjunctive(self, builder):
        prompt = builder.build_single_prompt(
            "Quando eu falar contigo, entenderás.", "falar", "advanced"
        )
        assert "subjunctive" in prompt.lower() or "subjuntivo" in prompt.lower()

    def test_complexity_levels_produce_different_prompts(self, builder):
        p_begin = builder.build_single_prompt("O gato dorme.", "dorme", "beginner")
        p_adv = builder.build_single_prompt("O gato dorme.", "dorme", "advanced")
        assert p_begin != p_adv

    def test_prompt_contains_grammatical_role_key(self, builder):
        """The schema key must be 'grammatical_role', not 'role' or 'pos'."""
        prompt = builder.build_single_prompt("O gato dorme.", "dorme", "beginner")
        assert "grammatical_role" in prompt

    def test_beginner_prompt_lists_beginner_roles(self, builder):
        prompt = builder.build_single_prompt("O gato dorme.", "dorme", "beginner")
        # Beginner roles should appear but NOT advanced-only roles
        assert "noun" in prompt
        assert "verb" in prompt

    def test_advanced_prompt_lists_copula_role(self, builder):
        prompt = builder.build_single_prompt("Ela está cansada.", "está", "advanced")
        assert "copula" in prompt

    def test_prompt_returns_string(self, builder):
        prompt = builder.build_single_prompt("Eu falo.", "falo", "intermediate")
        assert isinstance(prompt, str)
        assert len(prompt) > 200


class TestPtPromptBuilderBatch:
    def test_batch_prompt_contains_all_sentences(self, builder):
        sentences = [
            "O gato dorme.",
            "Ela vai ao mercado.",
            "Não me disse nada.",
        ]
        prompt = builder.build_batch_prompt(sentences, "mercado", "intermediate")
        for s in sentences:
            assert s in prompt

    def test_batch_prompt_is_different_from_single(self, builder):
        single = builder.build_single_prompt("O gato dorme.", "gato", "beginner")
        batch = builder.build_batch_prompt(["O gato dorme."], "gato", "beginner")
        assert single != batch

    def test_batch_prompt_mentions_array(self, builder):
        sentences = ["Eu falo.", "Tu falas."]
        prompt = builder.build_batch_prompt(sentences, "falar", "beginner")
        assert "ARRAY" in prompt.upper() or "array" in prompt.lower()


class TestPtSentenceGenerationPrompt:
    def test_sentence_generation_prompt_contains_word(self, builder):
        prompt = builder.get_sentence_generation_prompt(
            word="casa",
            language="Portuguese",
            num_sentences=3,
            difficulty="beginner",
        )
        assert "casa" in prompt

    def test_sentence_generation_prompt_contains_sections(self, builder):
        prompt = builder.get_sentence_generation_prompt(
            word="falar",
            language="Portuguese",
            num_sentences=4,
            difficulty="intermediate",
        )
        assert "SENTENCES" in prompt
        assert "TRANSLATIONS" in prompt

    def test_sentence_generation_prompt_with_topics(self, builder):
        prompt = builder.get_sentence_generation_prompt(
            word="comer",
            language="Portuguese",
            num_sentences=2,
            topics=["food", "family"],
            difficulty="beginner",
        )
        assert "food" in prompt or "family" in prompt

    def test_sentence_generation_prompt_returns_string(self, builder):
        prompt = builder.get_sentence_generation_prompt(
            word="beber", language="Portuguese", num_sentences=3
        )
        assert isinstance(prompt, str)
        assert len(prompt) > 100
