# languages/english/tests/test_en_config.py
"""Tests for EnConfig."""
import pytest
from languages.english.domain.en_config import EnConfig


class TestEnConfig:
    def test_basic_properties(self):
        cfg = EnConfig()
        assert cfg.language_code == "en"
        assert cfg.language_name == "English"
        assert cfg.is_rtl is False
        assert cfg.text_direction == "ltr"
        assert cfg.script_type == "alphabetic"

    def test_color_scheme_returns_dict(self):
        cfg = EnConfig()
        for level in ("beginner", "intermediate", "advanced"):
            scheme = cfg.get_color_scheme(level)
            assert isinstance(scheme, dict)
            assert "noun" in scheme
            assert "verb" in scheme

    def test_color_for_noun(self):
        cfg = EnConfig()
        color = cfg.get_color_for_role("noun")
        assert color == "#FFAA00"

    def test_color_for_verb(self):
        cfg = EnConfig()
        color = cfg.get_color_for_role("verb")
        assert color == "#4ECDC4"

    def test_color_for_article(self):
        """English-specific: article gets gold color."""
        cfg = EnConfig()
        color = cfg.get_color_for_role("article")
        assert color == "#FFD700"

    def test_color_for_infinitive_marker(self):
        """English-specific: infinitive marker gets its own color."""
        cfg = EnConfig()
        color = cfg.get_color_for_role("infinitive_marker")
        assert color == "#FF8C00"

    def test_color_for_modal_verb(self):
        """English-specific: modal verb gets its own color."""
        cfg = EnConfig()
        color = cfg.get_color_for_role("modal_verb")
        assert color is not None
        assert color.startswith("#")

    def test_color_unknown_role_returns_gray(self):
        cfg = EnConfig()
        color = cfg.get_color_for_role("nonexistent_role")
        assert color == "#808080"

    def test_default_roles_have_all_levels(self):
        cfg = EnConfig()
        roles = cfg._get_default_roles()
        for level in ("beginner", "intermediate", "advanced"):
            assert level in roles

    def test_beginner_roles_contains_basics(self):
        cfg = EnConfig()
        roles = cfg._get_default_roles()["beginner"]
        for key in ("noun", "verb", "adjective", "pronoun", "adverb", "article", "auxiliary"):
            assert key in roles, f"Expected '{key}' in beginner roles"

    def test_beginner_role_count(self):
        """Beginner should have 10 roles (as specified)."""
        cfg = EnConfig()
        roles = cfg._get_default_roles()["beginner"]
        assert len(roles) == 10, (
            f"Expected 10 beginner roles, got {len(roles)}: {list(roles.keys())}"
        )

    def test_intermediate_role_count(self):
        """Intermediate should have 22 roles (as specified)."""
        cfg = EnConfig()
        roles = cfg._get_default_roles()["intermediate"]
        assert len(roles) == 22, (
            f"Expected 22 intermediate roles, got {len(roles)}: {list(roles.keys())}"
        )

    def test_advanced_role_count(self):
        """Advanced should have 31 roles (as specified)."""
        cfg = EnConfig()
        roles = cfg._get_default_roles()["advanced"]
        assert len(roles) == 31, (
            f"Expected 31 advanced roles, got {len(roles)}: {list(roles.keys())}"
        )

    def test_advanced_roles_contains_english_specific(self):
        cfg = EnConfig()
        roles = cfg._get_default_roles()["advanced"]
        assert "relative_pronoun" in roles
        assert "phrasal_verb" in roles
        assert "subordinating_conjunction" in roles
        assert "reflexive_pronoun" in roles

    def test_intermediate_roles_contains_english_specific(self):
        cfg = EnConfig()
        roles = cfg._get_default_roles()["intermediate"]
        assert "modal_verb" in roles
        assert "particle" in roles
        assert "infinitive_marker" in roles
        assert "gerund" in roles

    def test_linguistic_features(self):
        cfg = EnConfig()
        assert cfg.linguistic_features["case_system"] is False  # English lost noun case
        assert cfg.linguistic_features["pronoun_case"] is True  # I/me, he/him survives
        assert cfg.linguistic_features["phrasal_verbs"] is True
        assert cfg.linguistic_features["do_support"] is True
        assert cfg.linguistic_features["strict_svo"] is True

    def test_color_scheme_all_levels_return_hex(self):
        """All color values must be valid hex codes."""
        cfg = EnConfig()
        for level in ("beginner", "intermediate", "advanced"):
            scheme = cfg.get_color_scheme(level)
            for role, color in scheme.items():
                assert color.startswith("#"), (
                    f"Color for role '{role}' at {level} is not a hex code: {color!r}"
                )
                assert len(color) in (4, 7), (
                    f"Color for role '{role}' at {level} has unexpected length: {color!r}"
                )

    def test_get_role_label_returns_nonempty(self):
        cfg = EnConfig()
        for level in ("beginner", "intermediate", "advanced"):
            for role in cfg.get_roles_for_complexity(level):
                label = cfg.get_role_label(role, level)
                assert label, f"Empty label for role '{role}' at {level}"

    def test_color_for_role_with_level_fallback(self):
        """color_for_role with unknown level falls back to intermediate."""
        cfg = EnConfig()
        color = cfg.get_color_for_role("noun", "unknown_level")
        assert color == "#FFAA00"

    def test_articles_list(self):
        cfg = EnConfig()
        assert "a" in cfg.articles
        assert "an" in cfg.articles
        assert "the" in cfg.articles

    def test_modal_verbs_list(self):
        cfg = EnConfig()
        for modal in ("can", "could", "will", "would", "shall", "should", "may", "might", "must"):
            assert modal in cfg.modal_verbs
