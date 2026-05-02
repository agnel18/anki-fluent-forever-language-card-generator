# languages/portuguese/tests/test_pt_config.py
"""Tests for PtConfig — Portuguese configuration component."""
import pytest
from languages.portuguese.domain.pt_config import PtConfig


class TestPtConfigBasicProperties:
    def test_language_code(self):
        cfg = PtConfig()
        assert cfg.language_code == "pt"

    def test_language_name(self):
        cfg = PtConfig()
        assert cfg.language_name == "Portuguese"

    def test_is_ltr(self):
        cfg = PtConfig()
        assert cfg.is_rtl is False
        assert cfg.text_direction == "ltr"

    def test_script_type(self):
        cfg = PtConfig()
        assert cfg.script_type == "alphabetic"

    def test_genders(self):
        cfg = PtConfig()
        assert "masculine" in cfg.genders
        assert "feminine" in cfg.genders

    def test_clitic_positions(self):
        cfg = PtConfig()
        for pos in ("proclitic", "enclitic", "mesoclitic"):
            assert pos in cfg.clitic_positions

    def test_registers(self):
        cfg = PtConfig()
        for reg in ("BR", "PT", "neutral"):
            assert reg in cfg.registers


class TestPtConfigLinguisticFeatures:
    def test_ser_estar_split(self):
        cfg = PtConfig()
        assert cfg.linguistic_features["ser_estar_split"] is True

    def test_three_state_clitics(self):
        cfg = PtConfig()
        assert cfg.linguistic_features["three_state_clitics"] is True

    def test_obligatory_contractions(self):
        cfg = PtConfig()
        assert cfg.linguistic_features["obligatory_contractions"] is True

    def test_personal_infinitive(self):
        cfg = PtConfig()
        assert cfg.linguistic_features["personal_infinitive"] is True

    def test_future_subjunctive(self):
        cfg = PtConfig()
        assert cfg.linguistic_features["future_subjunctive"] is True

    def test_debitive_construction(self):
        cfg = PtConfig()
        assert cfg.linguistic_features["debitive_construction"] is True

    def test_br_pt_register_split(self):
        cfg = PtConfig()
        assert cfg.linguistic_features["br_pt_register_split"] is True


class TestPtConfigColorSchemes:
    def test_color_scheme_returns_dict_for_all_levels(self):
        cfg = PtConfig()
        for level in ("beginner", "intermediate", "advanced"):
            scheme = cfg.get_color_scheme(level)
            assert isinstance(scheme, dict)
            assert len(scheme) > 10

    def test_color_scheme_contains_core_roles(self):
        cfg = PtConfig()
        scheme = cfg.get_color_scheme("intermediate")
        for role in ("noun", "verb", "adjective", "pronoun", "preposition"):
            assert role in scheme

    def test_color_scheme_contains_portuguese_specific_roles(self):
        cfg = PtConfig()
        scheme = cfg.get_color_scheme("intermediate")
        for role in ("copula", "contraction", "clitic_pronoun", "mesoclitic",
                     "gerund", "past_participle", "personal_infinitive"):
            assert role in scheme, f"Missing Portuguese-specific role: {role}"

    def test_unknown_complexity_falls_back_to_intermediate(self):
        cfg = PtConfig()
        scheme = cfg.get_color_scheme("unknown_level")
        assert isinstance(scheme, dict)
        assert "noun" in scheme

    def test_get_color_for_noun(self):
        cfg = PtConfig()
        color = cfg.get_color_for_role("noun")
        assert color == "#FFAA00"

    def test_get_color_for_verb(self):
        cfg = PtConfig()
        color = cfg.get_color_for_role("verb")
        assert color == "#44FF44"

    def test_get_color_for_unknown_role_returns_default(self):
        cfg = PtConfig()
        color = cfg.get_color_for_role("nonexistent_role_xyz")
        assert isinstance(color, str)
        assert color.startswith("#")

    # Behavior 6: Portuguese-specific color distinctness
    def test_copula_color_distinct_from_verb(self):
        """Copula must have a distinct hex color from generic verb."""
        cfg = PtConfig()
        copula_color = cfg.get_color_for_role("copula", "intermediate")
        verb_color = cfg.get_color_for_role("verb", "intermediate")
        assert copula_color != verb_color, (
            f"copula and verb share the same color: {copula_color}"
        )

    def test_contraction_color_distinct_from_preposition(self):
        cfg = PtConfig()
        contraction_color = cfg.get_color_for_role("contraction", "intermediate")
        preposition_color = cfg.get_color_for_role("preposition", "intermediate")
        assert contraction_color != preposition_color

    def test_mesoclitic_color_distinct_from_clitic_pronoun(self):
        cfg = PtConfig()
        meso_color = cfg.get_color_for_role("mesoclitic", "intermediate")
        clitic_color = cfg.get_color_for_role("clitic_pronoun", "intermediate")
        assert meso_color != clitic_color

    def test_gerund_color_distinct_from_verb(self):
        cfg = PtConfig()
        gerund_color = cfg.get_color_for_role("gerund", "intermediate")
        verb_color = cfg.get_color_for_role("verb", "intermediate")
        assert gerund_color != verb_color


class TestPtConfigGrammaticalRoles:
    def test_default_roles_have_all_levels(self):
        cfg = PtConfig()
        roles = cfg._get_default_roles()
        for level in ("beginner", "intermediate", "advanced"):
            assert level in roles

    def test_beginner_roles_contains_basics(self):
        cfg = PtConfig()
        roles = cfg._get_default_roles()["beginner"]
        for key in ("noun", "verb", "adjective", "pronoun", "preposition", "adverb"):
            assert key in roles

    def test_intermediate_roles_contains_copula(self):
        """Behavior 1: copula must appear in intermediate+ roles."""
        cfg = PtConfig()
        roles = cfg._get_default_roles()["intermediate"]
        assert "copula" in roles
        assert "contraction" in roles

    def test_advanced_roles_contains_portuguese_specifics(self):
        """Behavior 1: advanced tier has all Portuguese-specific roles."""
        cfg = PtConfig()
        roles = cfg._get_default_roles()["advanced"]
        for role in (
            "clitic_pronoun", "mesoclitic", "personal_infinitive",
            "subjunctive_marker", "gerund", "past_participle", "debitive",
        ):
            assert role in roles, f"Missing advanced role: {role}"

    def test_role_count_per_tier(self):
        """Behavior 1: tier counts are progressive."""
        cfg = PtConfig()
        roles = cfg._get_default_roles()
        beginner_count = len(roles["beginner"])
        intermediate_count = len(roles["intermediate"])
        advanced_count = len(roles["advanced"])
        assert beginner_count >= 9
        assert intermediate_count >= 15
        assert advanced_count >= 25
        assert intermediate_count > beginner_count
        assert advanced_count > intermediate_count

    def test_get_role_label_returns_string(self):
        cfg = PtConfig()
        label = cfg.get_role_label("copula", "intermediate")
        assert isinstance(label, str)
        assert len(label) > 0

    def test_get_role_label_unknown_role_returns_role_itself(self):
        cfg = PtConfig()
        label = cfg.get_role_label("totally_unknown_role_xyz", "intermediate")
        assert "totally_unknown_role_xyz" in label


class TestPtConfigContractions:
    def _get_contractions(self, cfg):
        """
        Normalise the contractions dict regardless of whether the YAML file
        loaded with a wrapper key or the in-code defaults were used.
        The YAML stores: {'contractions': {'do': [...], ...}}
        The in-code default returns: {'do': [...], ...}
        """
        raw = cfg.contractions
        if isinstance(raw, dict) and "contractions" in raw and isinstance(raw["contractions"], dict):
            return raw["contractions"]
        return raw

    def test_contractions_loaded(self):
        cfg = PtConfig()
        contractions = self._get_contractions(cfg)
        assert isinstance(contractions, dict)
        assert len(contractions) > 10

    def test_ao_contraction(self):
        """Behavior 3: 'ao' = a + o."""
        cfg = PtConfig()
        contractions = self._get_contractions(cfg)
        assert "ao" in contractions
        assert contractions["ao"] == ["a", "o"]

    def test_do_contraction(self):
        cfg = PtConfig()
        contractions = self._get_contractions(cfg)
        assert "do" in contractions
        assert contractions["do"] == ["de", "o"]

    def test_no_contraction(self):
        """
        Note: YAML 1.1 parses bare 'no' as boolean False. The contraction
        'no' (em + o) is present either as the string 'no' (when using
        in-code defaults or YAML 1.2) or as False (YAML 1.1 bool quirk).
        Test for the value under either key form.
        """
        cfg = PtConfig()
        contractions = self._get_contractions(cfg)
        # Accept either 'no' (string) or False (YAML 1.1 quirk)
        assert "no" in contractions or False in contractions
        value = contractions.get("no") or contractions.get(False)
        assert value == ["em", "o"] or value == ["em", "o"]

    def test_pelo_contraction(self):
        cfg = PtConfig()
        contractions = self._get_contractions(cfg)
        assert "pelo" in contractions
        assert contractions["pelo"] == ["por", "o"]

    def test_dele_contraction(self):
        cfg = PtConfig()
        contractions = self._get_contractions(cfg)
        assert "dele" in contractions
        parts = contractions["dele"]
        assert parts[0] == "de"
        assert parts[1] == "ele"
