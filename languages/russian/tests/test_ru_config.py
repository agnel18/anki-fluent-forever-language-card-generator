# languages/russian/tests/test_ru_config.py
"""
Tests for RuConfig (Russian configuration component).
"""
import pytest
from languages.russian.domain.ru_config import RuConfig


# ---------------------------------------------------------------------------
# Expected role counts per level (from ru_config._get_default_roles)
# ---------------------------------------------------------------------------
BEGINNER_ROLE_COUNT = 11    # noun, verb, adjective, pronoun, preposition,
                            # conjunction, adverb, particle, numeral,
                            # interjection, other
INTERMEDIATE_ROLE_COUNT = 24
ADVANCED_ROLE_COUNT = 43


class TestRuConfigInstantiation:
    def test_instantiation(self):
        config = RuConfig()
        assert config is not None

    def test_language_code(self):
        config = RuConfig()
        assert config.language_code == "ru"

    def test_language_name(self):
        config = RuConfig()
        assert config.language_name == "Russian"
        assert config.language_name_native == "Русский"

    def test_not_rtl(self):
        config = RuConfig()
        assert config.is_rtl is False
        assert config.text_direction == "ltr"

    def test_script_type(self):
        config = RuConfig()
        assert config.script_type == "alphabetic"

    def test_linguistic_features_present(self):
        config = RuConfig()
        features = config.linguistic_features
        assert features["case_system"] is True
        assert features["grammatical_gender"] is True
        assert features["verbal_aspect"] is True
        assert features["reflexive_verbs"] is True

    def test_cases_list(self):
        config = RuConfig()
        assert "nominative" in config.cases
        assert "genitive" in config.cases
        assert "dative" in config.cases
        assert "accusative" in config.cases
        assert "instrumental" in config.cases
        assert "prepositional" in config.cases
        assert len(config.cases) == 6

    def test_genders_list(self):
        config = RuConfig()
        assert "masculine" in config.genders
        assert "feminine" in config.genders
        assert "neuter" in config.genders


class TestRuConfigColorScheme:
    def test_color_scheme_all_levels_present(self):
        config = RuConfig()
        for level in ("beginner", "intermediate", "advanced"):
            scheme = config.get_color_scheme(level)
            assert isinstance(scheme, dict)
            assert len(scheme) > 5

    def test_color_for_role_returns_hex(self):
        config = RuConfig()
        for level in ("beginner", "intermediate", "advanced"):
            color = config.get_color_for_role("noun", level)
            assert color.startswith("#"), f"Expected hex color, got: {color!r}"
            assert len(color) in (4, 7), f"Invalid hex length: {color!r}"

    def test_color_for_noun(self):
        config = RuConfig()
        assert config.get_color_for_role("noun") == "#FFAA00"

    def test_color_for_verb(self):
        config = RuConfig()
        assert config.get_color_for_role("verb") == "#4ECDC4"

    def test_color_for_adjective(self):
        config = RuConfig()
        assert config.get_color_for_role("adjective") == "#FF44FF"

    def test_color_for_personal_pronoun(self):
        config = RuConfig()
        assert config.get_color_for_role("personal_pronoun") == "#9370DB"

    def test_color_for_preposition(self):
        config = RuConfig()
        assert config.get_color_for_role("preposition") == "#4444FF"

    def test_color_for_unknown_role_falls_back_to_other(self):
        config = RuConfig()
        other_color = config.get_color_for_role("other")
        unknown_color = config.get_color_for_role("totally_unknown_role_xyz")
        assert unknown_color == other_color

    def test_all_beginner_roles_have_valid_hex(self):
        config = RuConfig()
        roles = config._get_default_roles()
        scheme = config.get_color_scheme("beginner")
        for role in roles["beginner"]:
            color = scheme.get(role, scheme.get("other", "#808080"))
            assert color.startswith("#"), f"Role '{role}' has invalid color: {color!r}"

    def test_imperfective_and_perfective_verb_share_color(self):
        config = RuConfig()
        assert (
            config.get_color_for_role("imperfective_verb")
            == config.get_color_for_role("perfective_verb")
            == config.get_color_for_role("verb")
        )

    def test_participle_color(self):
        config = RuConfig()
        assert config.get_color_for_role("participle") == "#FF8C00"

    def test_gerund_color(self):
        config = RuConfig()
        assert config.get_color_for_role("gerund") == "#FFA500"

    def test_negation_particle_color(self):
        config = RuConfig()
        assert config.get_color_for_role("negation_particle") == "#FF6347"

    def test_aspectual_particle_color(self):
        config = RuConfig()
        assert config.get_color_for_role("aspectual_particle") == "#FF1493"


class TestRuConfigRoleLabels:
    def test_get_role_label_returns_non_empty(self):
        config = RuConfig()
        for level in ("beginner", "intermediate", "advanced"):
            roles = config._get_default_roles()[level]
            for role in roles:
                label = config.get_role_label(role, level)
                assert label, f"Empty label for role '{role}' at {level}"

    def test_get_role_label_unknown_role(self):
        config = RuConfig()
        label = config.get_role_label("totally_unknown_xyz", "intermediate")
        # Should return the role name itself as fallback
        assert label == "totally_unknown_xyz"

    def test_beginner_role_count(self):
        config = RuConfig()
        roles = config._get_default_roles()
        assert len(roles["beginner"]) == BEGINNER_ROLE_COUNT

    def test_intermediate_role_count(self):
        config = RuConfig()
        roles = config._get_default_roles()
        assert len(roles["intermediate"]) == INTERMEDIATE_ROLE_COUNT

    def test_advanced_role_count(self):
        config = RuConfig()
        roles = config._get_default_roles()
        assert len(roles["advanced"]) == ADVANCED_ROLE_COUNT

    def test_beginner_does_not_have_participle(self):
        """Participles are advanced/intermediate — should not be in beginner roles."""
        config = RuConfig()
        roles = config._get_default_roles()
        assert "participle" not in roles["beginner"]
        assert "present_active_participle" not in roles["beginner"]

    def test_advanced_has_all_participle_types(self):
        config = RuConfig()
        roles = config._get_default_roles()
        for role in (
            "participle",
            "present_active_participle",
            "past_active_participle",
            "present_passive_participle",
            "past_passive_participle",
        ):
            assert role in roles["advanced"], f"'{role}' missing from advanced roles"

    def test_advanced_has_gerund(self):
        config = RuConfig()
        roles = config._get_default_roles()
        assert "gerund" in roles["advanced"]

    def test_advanced_has_relative_pronoun(self):
        config = RuConfig()
        roles = config._get_default_roles()
        assert "relative_pronoun" in roles["advanced"]
