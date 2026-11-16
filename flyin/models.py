"""Plain data models describing the zone network."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ZoneType(Enum):
    """The four kinds of zones a hub can be."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def cost(self) -> int:
        """Return how many turns it takes to ENTER a zone of this type.

        Blocked zones can never be entered, so asking for their cost is a
        programming error.
        """
        if self is ZoneType.BLOCKED:
            raise ValueError("blocked zones cannot be entered")
        if self is ZoneType.RESTRICTED:
            return 2
        return 1


@dataclass
class Zone:
    """A hub (node) of the network.

    Attributes:
        name: Unique zone name (no dashes, no spaces).
        x: Integer x coordinate (used only for display).
        y: Integer y coordinate (used only for display).
        zone_type: Type of the zone, decides movement cost.
        color: Optional display color.
        max_drones: How many drones may be inside at the same time.
        is_start: True for the unique start hub.
        is_end: True for the unique end hub.
    """

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: Optional[str] = None
    max_drones: int = 1
    is_start: bool = False
    is_end: bool = False

    @property
    def unlimited(self) -> bool:
        """Start and end hubs have no capacity limit."""
        return self.is_start or self.is_end

    @property
    def enterable(self) -> bool:
        """A zone can be entered unless it is blocked."""
        return self.zone_type is not ZoneType.BLOCKED


@dataclass
class Connection:
    """A bidirectional edge between two zones.

    Attributes:
        a: Name of the first zone.
        b: Name of the second zone.
        max_link_capacity: Drones allowed on the link at the same time.
    """

    a: str
    b: str
    max_link_capacity: int = 1

    @property
    def name(self) -> str:
        """Name used in the output, e.g. ``roof1-roof2``."""
        return f"{self.a}-{self.b}"

    @property
    def key(self) -> frozenset[str]:
        """Order independent key, so ``a-b`` and ``b-a`` are equal."""
        return frozenset((self.a, self.b))

    def other(self, zone_name: str) -> str:
        """Return the zone on the other side of ``zone_name``."""
        if zone_name == self.a:
            return self.b
        if zone_name == self.b:
            return self.a
        raise ValueError(f"{zone_name} is not part of {self.name}")


@dataclass
class MapData:
    """Everything read from a map file, before building the graph.

    Attributes:
        nb_drones: Number of drones to route (positive).
        zones: Zone name -> Zone, in file order.
        connections: Every connection, in file order.
        start: Name of the start hub (None until it is read).
        end: Name of the end hub (None until it is read).
        """

    nb_drones: int = 0
    zones: dict[str, Zone] = field(default_factory=dict)
    connections: list[Connection] = field(default_factory=list)
    start: Optional[str] = None
    end: Optional[str] = None
