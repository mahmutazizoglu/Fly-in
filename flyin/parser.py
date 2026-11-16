"""Read  a Fly-in map file and turn it into a MapData object"""

from typing import Optional

from flyin.errors import FlyInError, ParseError
from flyin.models import MapData, Zone, ZoneType

ZONE_KEYS: frozenset[str] = frozenset({"zone", "color", "max_drones"})

class MapParser:
    """Parse a map file line by line.
    
    Usage::
    
        data = MapParser("maps/example,txt").parse()
    """

    def __init__(self, path: str) -> None:
        """Remember the Path: nothing is read until parse() is called."""
        self.path: str = path
        self.data: MapData = MapData()
        self._seen_nb_drones: bool = False

    def parse(self) -> MapData:
        """Read the whole file and return the parsed data.
        
        
        Raises:
            FlyInError: if the file cannot be opened.
            ParseError: on the first invalid line.
            """
        try:
            with open(self.path, encoding="utf-8") as file:
                lines: list[str] = file.readlines()
        except OSError as err:
            raise FlyInError(f"cannot read '{self.path}': {err.strerror}")
        for line_no, raw in enumerate(lines, start=1):
            line: str = self._strip_comment(raw)
            if line:
                self._parse_line(line_no, line)
        return self.data

    @staticmethod
    def _strip_comment(raw: str) -> str:
        """Drop everything after '#' and surrounding whitespace."""
        return raw.split('#', 1)[0].strip()

    def _parse_line(self, line_no: int, line: str) -> None:
        """Send one meaningful line to the right handler."""
        if ":" not in line:
            raise ParseError(line_no, f"expected 'keyword: ...', got '{line}")
        keyword, rest = line.split(":", 1)
        keyword, rest = keyword.strip(), rest.strip()
        if not self._seen_nb_drones and keyword != "nb_drones":
            raise ParseError(line_no, "first line must be 'nb_drones: <n>'")
        if keyword == "nb_drones":
            self._parse_nb_drones(line_no, rest)
        elif keyword in ("start_hub", "end_hub", "hub"):
            self._parse_hub(line_no, keyword, rest)
        elif keyword == "connection":
            self._parse_commection(line_no, rest)
        else:
            raise ParseError(line_no, f"unknown keyword '{keyword}'")

    def _parse_nb_drone(self, line_no: int, rest: str) -> None:
        """Handle 'nb_drones: <positive_integer>'."""
        if self._seen_nb_drones:
            raise ParseError(line_no, "nb_drones defined twice")
        self.data.nb_drones = self._positive_int(line_no, "nb_drones", rest)
        self._seen_nb_drones = True

    def _parse_hub(self, line_no: int, keyword: str, rest: str) -> None:
        """Handle 'start_hub:', 'end_hub:' and 'hub:' lines."""
        head, meta = self._split_metadata(line_no, rest)
        parts: list[str] = head.split()
        if len(parts) != 3:
            raise ParseError(line_no, "expacted '<name> <x> <y> [metadata]'")
        name, x_text, y_text = parts
        if "-" in name:
            raise ParseError(line_no, f"zone name '{name}' contains a dash")
        if name in self.data.zones:
            raise ParseError(line_no, f"zone '{name}' defined twice")
        x: int = self._int(line_no, "x", x_text)
        y: int = self._int(line_no, "y", y_text)

        for key in meta:
            if key not in ZONE_KEYS:
                raise ParseError(line_no, f"unknown zone metadata '{key}'")
        zone_type: ZoneType = self._zone_type(line_no, meta.get("zone"))
        is_start: bool = keyword == "start_hub"
        is_end: bool = keyword == "end_hub"
        max_drones: int = 1
        