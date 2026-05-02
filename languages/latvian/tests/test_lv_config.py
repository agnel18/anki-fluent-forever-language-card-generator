# languages/latvian/tests/test_lv_config.py
"""Tests for LvConfig."""
import pytest
from languages.latvian.domain.lv_config import LvConfig


class TestLvConfig:
    def test_basic_properties(self):
        cfg = LvConfig()
        assert cfg.language_code == "lv"
        assert cfg.language_name == "Latvian"
        assert cfg.is_rtl is False
        assert cfg.text_direction == "ltr"
        assert cfg.script_type == "alphabetic"

    def test_color_scheme_returns_dict(self):
        cfg = LvConfig()
        for level in ("beginner", "intermediate", "advanced"):
            scheme = cfg.get_color_scheme(level)
            assert isinstance(scheme, dict)
            assert "noun" in scheme
            assert "verb" in scheme

    def test_color_for_noun(self):
        cfg = LvConfig()
        color = cfg.get_color_for_role("noun")
        assert color == "#FFAA00"

    def test_color_for_verb(self):
        cfg = LvConfig()
        color = cfg.get_color_for_role("verb")
        assert color == "#4ECDC4"

    def test_color_for_debitive(self):
        cfg = LvConfig()
        color = cfg.get_color_for_role("debitive")
        assert color == "#FF1493"

    def test_color_unknown_role_returns_gray(self):
        cfg = LvConfig()
        color = cfg.get_color_for_role("nonexistent_role")
        assert color == "#808080"

    def test_default_roles_have_all_levels(self):
        cfg = LvConfig()
        roles = cfg._get_default_roles()
        for level in ("beginner", "intermediate", "advanced"):
            assert level in roles

    def test_beginner_roles_contains_basics(self):
        cfg = LvConfig()
        roles = cfg._get_default_roles()["beginner"]
        for key in ("noun", "verb", "adjective", "pronoun", "adverb"):
            assert key in roles

    def test_advanced_roles_contains_latvian_specific(self):
        cfg = LvConfig()
        roles = cfg._get_default_roles()["advanced"]
        assert "debitive" in roles
        assert "participle" in roles
        assert "reflexive_verb" in roles
        assert "verbal_noun" in roles

    def test_linguistic_features(self):
        cfg = LvConfig()
        assert cfg.linguistic_features["case_system"] is True
        assert cfg.linguistic_features["debitive_mood"] is True
        assert cfg.linguistic_features["definite_adjective"] is True

    def test_cases_list(self):
        cfg = LvConfig()
        assert len(cfg.cases) == 7
        assert "nominative" in cfg.cases
        assert "vocative" in cfg.cases
