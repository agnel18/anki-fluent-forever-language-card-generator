"""Chinese Traditional config tests."""

from ..domain.zh_tw_config import ZhTwConfig


def test_config_loads_roles():
    config = ZhTwConfig()
    roles = config.grammatical_roles.get("beginner", {})
    assert isinstance(roles, dict)
