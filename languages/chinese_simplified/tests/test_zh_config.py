"""Chinese Simplified config tests."""

from ..domain.zh_config import ZhConfig


def test_config_loads_roles():
    config = ZhConfig()
    roles = config.grammatical_roles.get("beginner", {})
    assert isinstance(roles, dict)
