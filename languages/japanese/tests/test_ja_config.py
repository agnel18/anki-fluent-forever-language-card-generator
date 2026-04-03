"""Japanese config tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.japanese.domain.ja_config import JaConfig


def test_config_creation():
    config = JaConfig()
    assert config is not None


def test_config_loads_roles():
    config = JaConfig()
    roles = config.grammatical_roles.get("complexity_filters", {}).get("beginner", [])
    assert isinstance(roles, list)
    assert len(roles) > 0


def test_config_has_color_scheme():
    config = JaConfig()
    colors = config.get_color_scheme("beginner")
    assert isinstance(colors, dict)
    assert len(colors) > 0


def test_config_has_voice_config():
    config = JaConfig()
    assert hasattr(config, 'voice_config')
    assert 'language_code' in config.voice_config
    assert config.voice_config['language_code'] == 'ja-JP'


def test_config_loads_particle_patterns():
    config = JaConfig()
    assert isinstance(config.particle_patterns, dict)
    assert 'case_particles' in config.particle_patterns
    assert 'は' in config.particle_patterns['case_particles']


def test_config_loads_verb_conjugations():
    config = JaConfig()
    assert isinstance(config.verb_conjugations, dict)
    assert 'verb_groups' in config.verb_conjugations
    assert 'godan' in config.verb_conjugations['verb_groups']


def test_config_loads_adjective_patterns():
    config = JaConfig()
    assert isinstance(config.adjective_patterns, dict)
    assert 'i_adjectives' in config.adjective_patterns
    assert 'na_adjectives' in config.adjective_patterns


def test_config_loads_honorific_patterns():
    config = JaConfig()
    assert isinstance(config.honorific_patterns, dict)
    assert 'honorific_levels' in config.honorific_patterns


def test_config_loads_counter_patterns():
    config = JaConfig()
    assert isinstance(config.counter_patterns, dict)
    assert 'general_counters' in config.counter_patterns


def test_config_loads_word_meanings():
    config = JaConfig()
    assert isinstance(config.word_meanings, dict)
    assert 'common_words' in config.word_meanings
    assert '私' in config.word_meanings['common_words']


def test_config_loads_patterns():
    config = JaConfig()
    assert isinstance(config.patterns, dict)
    assert 'script_ranges' in config.patterns


def test_color_scheme_all_levels():
    config = JaConfig()
    for level in ['beginner', 'intermediate', 'advanced']:
        colors = config.get_color_scheme(level)
        assert isinstance(colors, dict)
        assert 'verb' in colors or 'noun' in colors


def test_config_has_prompt_templates():
    config = JaConfig()
    assert hasattr(config, 'prompt_templates')
    assert 'single' in config.prompt_templates
    assert 'batch' in config.prompt_templates


def test_config_supported_complexity_levels():
    config = JaConfig()
    # Complexity levels are defined in grammatical_roles complexity_filters
    filters = config.grammatical_roles.get('complexity_filters', {})
    assert 'beginner' in filters
    assert 'intermediate' in filters
    assert 'advanced' in filters
