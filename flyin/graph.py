"""The zone network as a graph that the algorithms can walk on """

from flyin.errors import NoPathError
from flyin.models import Connection, MapData, Zone


class Network:
    """Graph view of parsed map: zones are nodes, connections are edges.
    
    Attributes:
        nb_drones: Number of drones to route.
        start: Name of the start hub.
        end: Name of the end hub.
        zones: Zone name -> Zone.
    """

    def __init__(self, data: MapData) -> None:
        """Build the adjacency lists and the link lookup table.

        Raises:
            NoPathError: if the start or the end hub is blocked.
        """
        if data.start is None or data.end is None:
            raise ValueError("MapData has no start or end hub")
        self.nb_drones: int = data.nb_drones
        self.start: str = data.start
        self.end: str = data.end
        self.zones: dict[str, Zone] = data.zones
        self._neighbours: dict[str, list[str]] = {
            name: [] for name in self.zones}
        self._links: dict[frozenset[str], Connection] = {}
        for link in data.connections:
            self._neighbours[link.a].append(link.b)
            self._neighbours[link.b].append(link.a)
            self._links[link.key] = link
        for name in (self.start, self.end):
            if not self.zones[name].enterable:
                raise NoPathError(f"hub '{name}' is blocked")

        def neighbours(self, name: str) -> list[str]:
            """Zones one connection away from ''name'', in file order."""
            return self._neighbours[name]

        def link(self, a: str, b: str) -> Connection:
            """Return the connection between ''a'' and ''b''.
            
            Raises:
                KeyError: if the two zones are not connected.
                """
            return self._links[frozenset((a, b))]

        def move_cost(self, name: str) -> int:
            """Turns needed to fly INTO zone ''name'' (2 for restricted)."""
            return self.zones[name].zone_type.cost
