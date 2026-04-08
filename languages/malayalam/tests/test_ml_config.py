"""Malayalam config tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.malayalam.domain.ml_config import MlConfig


def test_config_creation():
    config = MlConfig()
    assert config is not None


def test_config_loads_roles():
    config = MlConfig()
    roles = config.grammatical_roles.get("complexity_filters", {}).get("beginner", [])
    assert isinstance(roles, list)
    assert len(roles) > 0


def test_config_has_color_scheme():
    config = MlConfig()
    colors = config.get_color_scheme("beginner")
    assert isinstance(colors, dict)
    assert len(colors) > 0


def test_config_has_voice_config():
    config = MlConfig()
    assert hasattr(config, 'voice_config')
    assert 'language_code' in config.voice_config
    assert config.voice_config['language_code'] == 'ml-IN'


def test_config_loads_case_patterns():
    config = MlConfig()
    assert isinstance(config.case_patterns, dict)
    assert 'cases' in config.case_patterns
    assert 'nominative' in config.case_patterns['cases']
    assert 'accusative' in config.case_patterns['cases']
    assert 'dative' in config.case_patterns['cases']
    assert 'locative' in config.case_patterns['cases']


def test_config_loads_verb_conjugations():
    config = MlConfig()
    assert isinstance(config.verb_conjugations, dict)
    assert 'tenses' in config.verb_conjugations
    assert 'present' in config.verb_conjugations['tenses']
    assert 'past' in config.verb_conjugations['tenses']
    assert 'future' in config.verb_conjugations['tenses']


def test_config_loads_postposition_patterns():
    config = MlConfig()
    assert isinstance(config.postposition_patterns, dict)
    assert 'spatial' in config.postposition_patterns
    assert 'temporal' in config.postposition_patterns


def test_config_loads_honorific_patterns():
    config = MlConfig()
    assert isinstance(config.honorific_patterns, dict)
    assert 'levels' in config.honorific_patterns


def test_config_loads_word_meanings():
    config = MlConfig()
    assert isinstance(config.word_meanings, dict)
    assert 'common_words' in config.word_meanings
    assert 'ഞാൻ' in config.word_meanings['common_words']


def test_config_color_scheme_has_malayalam_roles():
    config = MlConfig()
    colors = config.get_color_scheme("intermediate")
    assert 'postposition' in colors
    assert 'case_marker' in colors
    assert 'verbal_participle' in colors


def test_config_all_complexity_levels():
    config = MlConfig()
    for level in ['beginner', 'intermediate', 'advanced']:
        colors = config.get_color_scheme(level)
        assert isinstance(colors, dict)
        assert 'noun' in colors
        assert 'verb' in colors
