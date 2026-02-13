"""French config tests."""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from languages.french.domain.fr_config import FrConfig


def test_config_loads_roles():
    config = FrConfig()
    roles = config.grammatical_roles.get("complexity_filters", {}).get("beginner", [])
    assert isinstance(roles, list)
    assert len(roles) > 0


def test_config_has_color_scheme():
    config = FrConfig()
    colors = config.get_color_scheme("beginner")
    assert isinstance(colors, dict)
    assert len(colors) > 0


def test_config_has_voice_config():
    config = FrConfig()
    assert hasattr(config, 'voice_config')
    assert 'language_code' in config.voice_config