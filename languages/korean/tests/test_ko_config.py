"""Korean config tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.korean.domain.ko_config import KoConfig


def test_config_creation():
    config = KoConfig()
    assert config is not None


def test_config_loads_roles():
    config = KoConfig()
    roles = config.grammatical_roles.get("complexity_filters", {}).get("beginner", [])
    assert isinstance(roles, list)
    assert len(roles) > 0


def test_config_has_color_scheme():
    config = KoConfig()
    colors = config.get_color_scheme("beginner")
    assert isinstance(colors, dict)
    assert len(colors) > 0


def test_config_has_voice_config():
    config = KoConfig()
    assert hasattr(config, 'voice_config')
    assert 'language_code' in config.voice_config
    assert config.voice_config['language_code'] == 'ko-KR'


def test_config_loads_particle_patterns():
    config = KoConfig()
    assert isinstance(config.particle_patterns, dict)
    assert 'case_particles' in config.particle_patterns
    assert '은' in config.particle_patterns['case_particles']


def test_config_loads_verb_conjugations():
    config = KoConfig()
    assert isinstance(config.verb_conjugations, dict)
    assert 'verb_types' in config.verb_conjugations


def test_config_loads_honorific_patterns():
    config = KoConfig()
    assert isinstance(config.honorific_patterns, dict)
    assert 'honorific_levels' in config.honorific_patterns


def test_config_loads_word_meanings():
    config = KoConfig()
    assert isinstance(config.word_meanings, dict)
    assert 'common_words' in config.word_meanings
    assert '나' in config.word_meanings['common_words']


def test_config_loads_patterns():
    config = KoConfig()
    assert isinstance(config.patterns, dict)
    assert 'script_ranges' in config.patterns


def test_color_scheme_all_levels():
    config = KoConfig()
    for level in ['beginner', 'intermediate', 'advanced']:
        colors = config.get_color_scheme(level)
        assert isinstance(colors, dict)
        assert 'verb' in colors or 'noun' in colors


def test_config_has_prompt_templates():
    config = KoConfig()
    assert hasattr(config, 'prompt_templates')
    assert 'single' in config.prompt_templates
    assert 'batch' in config.prompt_templates


def test_korean_specific_colors_in_advanced():
    """Korean-specific roles should have unique colors in advanced scheme."""
    config = KoConfig()
    colors = config.get_color_scheme("advanced")
    assert 'topic_marker' in colors
    assert 'subject_marker' in colors
    assert 'object_marker' in colors
    assert 'honorific_particle' in colors
    assert 'honorific_verb' in colors
    assert 'connective_ending' in colors
    # Each must have a distinct color
    korean_roles = ['topic_marker', 'subject_marker', 'object_marker',
                    'honorific_particle', 'honorific_verb', 'connective_ending']
    korean_colors = [colors[r] for r in korean_roles]
    assert len(set(korean_colors)) == len(korean_colors), "Korean-specific roles must have unique colors"
