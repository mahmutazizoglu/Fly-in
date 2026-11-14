"""Unit tests for flyin.models (not graded, for our own safety)."""

import pytest

from flyin.models import Connection, Zone, ZoneType


def test_zone_costs() -> None:
    """Restricted costs 2 turns, normal and priority cost 1."""
    assert ZoneType.NORMAL.cost == 1
    assert ZoneType.PRIORITY.cost == 1
    assert ZoneType.RESTRICTED.cost == 2
    with pytest.raises(ValueError):
        _ = ZoneType.BLOCKED.cost


def test_zone_defaults() -> None:
    """A bare zone is normal, capacity 1, not start/end."""
    z = Zone("a", 0, 0)
    assert z.zone_type is ZoneType.NORMAL
    assert z.max_drones == 1
    assert z.enterable and not z.unlimited


def test_connection_key_is_order_independent() -> None:
    """a-b and b-a must be detected as the same connection."""
    assert Connection("a", "b").key == Connection("b", "a").key
    assert Connection("a", "b").other("a") == "b"
