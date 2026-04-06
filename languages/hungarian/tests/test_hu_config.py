"""Hungarian config tests."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.hungarian.domain.hu_config import HuConfig, ComplexityLevel, GrammaticalRole


def test_config_creation():
    config = HuConfig()
    assert config is not None


def test_config_loads_grammatical_roles():
    config = HuConfig()
    assert isinstance(config.grammatical_roles, dict)
    assert 'role_hierarchy' in config.grammatical_roles
    assert 'complexity_filters' in config.grammatical_roles


def test_config_loads_word_meanings():
    config = HuConfig()
    assert isinstance(config.word_meanings, dict)
    assert 'common_words' in config.word_meanings
    common = config.word_meanings['common_words']
    assert 'ház' in common
    assert 'eszik' in common


def test_config_loads_patterns():
    config = HuConfig()
    assert isinstance(config.patterns, dict)
    assert 'vowel_harmony' in config.patterns
    assert 'case_suffixes' in config.patterns
    assert 'preverbs' in config.patterns


def test_color_scheme_beginner():
    config = HuConfig()
    scheme = config.get_color_scheme("beginner")
    assert isinstance(scheme, dict)
    assert "noun" in scheme
    assert "verb" in scheme
    assert "postposition" in scheme
    assert "preverb" in scheme


def test_color_scheme_intermediate():
    config = HuConfig()
    scheme = config.get_color_scheme("intermediate")
    assert "accusative" in scheme
    assert "dative" in scheme
    assert "possessive_suffix" in scheme
    assert "definite_conjugation" in scheme


def test_color_scheme_advanced():
    config = HuConfig()
    scheme = config.get_color_scheme("advanced")
    assert "terminative" in scheme
    assert "essive_formal" in scheme
    assert "distributive" in scheme
    assert "causative_verb" in scheme
    assert "potential_verb" in scheme


def test_color_scheme_unknown_returns_intermediate():
    config = HuConfig()
    scheme = config.get_color_scheme("unknown_level")
    intermediate = config.get_color_scheme("intermediate")
    assert scheme == intermediate


def test_prompt_templates_exist():
    config = HuConfig()
    assert 'single' in config.prompt_templates
    assert 'batch' in config.prompt_templates
    assert 'Hungarian' in config.prompt_templates['single'] or 'sentence' in config.prompt_templates['single']


def test_voice_config():
    config = HuConfig()
    assert config.voice_config['language_code'] == 'hu-HU'


def test_complexity_level_enum():
    assert ComplexityLevel.BEGINNER.value == "beginner"
    assert ComplexityLevel.INTERMEDIATE.value == "intermediate"
    assert ComplexityLevel.ADVANCED.value == "advanced"


def test_grammatical_role_enum():
    assert GrammaticalRole.NOUN.value == "noun"
    assert GrammaticalRole.ACCUSATIVE.value == "accusative"
    assert GrammaticalRole.PREVERB.value == "preverb"
    assert GrammaticalRole.POSTPOSITION.value == "postposition"
    assert GrammaticalRole.POSSESSIVE_SUFFIX.value == "possessive_suffix"
    assert GrammaticalRole.DEFINITE_CONJUGATION.value == "definite_conjugation"
    assert GrammaticalRole.INDEFINITE_CONJUGATION.value == "indefinite_conjugation"


def test_role_hierarchy_maps_verb_subtypes():
    config = HuConfig()
    hierarchy = config.grammatical_roles.get('role_hierarchy', {})
    assert hierarchy.get('definite_conjugation') == 'verb'
    assert hierarchy.get('indefinite_conjugation') == 'verb'
    assert hierarchy.get('auxiliary_verb') == 'verb'
    assert hierarchy.get('causative_verb') == 'verb'
    assert hierarchy.get('potential_verb') == 'verb'
