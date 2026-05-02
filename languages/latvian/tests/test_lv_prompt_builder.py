# languages/latvian/tests/test_lv_prompt_builder.py
"""Tests for LvPromptBuilder."""
import pytest
from languages.latvian.domain.lv_config import LvConfig
from languages.latvian.domain.lv_prompt_builder import LvPromptBuilder


@pytest.fixture
def builder():
    return LvPromptBuilder(LvConfig())


class TestLvPromptBuilder:
    def test_single_prompt_contains_sentence(self, builder):
        prompt = builder.build_single_prompt("Es runāju.", "runāju", "beginner")
        assert "Es runāju." in prompt

    def test_single_prompt_contains_language(self, builder):
        prompt = builder.build_single_prompt("Es runāju.", "runāju", "beginner")
        assert "Latvian" in prompt or "latviešu" in prompt.lower()

    def test_single_prompt_contains_target_word(self, builder):
        prompt = builder.build_single_prompt("Es runāju.", "runāju", "beginner")
        assert "runāju" in prompt

    def test_batch_prompt_contains_all_sentences(self, builder):
        sentences = ["Es runāju.", "Viņš iet.", "Māja ir skaista."]
        prompt = builder.build_batch_prompt(sentences, "runāju", "intermediate")
        for s in sentences:
            assert s in prompt

    def test_intermediate_prompt_mentions_debitive(self, builder):
        prompt = builder.build_single_prompt("Man jārunā.", "jārunā", "intermediate")
        assert "debitive" in prompt.lower() or "jā-" in prompt or "jā" in prompt.lower()

    def test_advanced_prompt_mentions_participles(self, builder):
        prompt = builder.build_single_prompt("Uzrakstītā vēstule.", "vēstule", "advanced")
        assert "participle" in prompt.lower() or "divdabis" in prompt.lower()

    def test_beginner_prompt_no_debitive(self, builder):
        prompt = builder.build_single_prompt("Es runāju.", "runāju", "beginner")
        # Beginner prompts should not overwhelm with advanced concepts
        assert "jā-" not in prompt

    def test_prompt_contains_json_schema(self, builder):
        prompt = builder.build_single_prompt("Māja ir skaista.", "māja", "beginner")
        assert "word_explanations" in prompt
        assert "JSON" in prompt

    def test_prompt_contains_color_mapping(self, builder):
        prompt = builder.build_single_prompt("Es runāju.", "runāju", "beginner")
        assert "#FFAA00" in prompt   # noun color
        assert "#4ECDC4" in prompt   # verb color

    def test_complexity_levels_produce_different_prompts(self, builder):
        p1 = builder.build_single_prompt("Es runāju.", "runāju", "beginner")
        p2 = builder.build_single_prompt("Es runāju.", "runāju", "advanced")
        assert p1 != p2
