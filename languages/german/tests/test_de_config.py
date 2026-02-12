"""German config tests."""

from ..domain.de_config import DeConfig


def test_config_loads_roles():
    config = DeConfig()
    roles = config.grammatical_roles.get("grammatical_roles", {})
    assert isinstance(roles, dict)
