"""Hindi config tests."""

from ..domain.hi_config import HiConfig


def test_config_loads_roles():
    config = HiConfig()
    roles = config.grammatical_roles.get("grammatical_roles", {})
    assert isinstance(roles, dict)
    assert "noun" in roles
