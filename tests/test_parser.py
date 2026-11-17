"""Unit tests for flyin.parser (Day 2: drones, hubs, metadata)."""

from pathlib import Path

import pytest

from flyin.errors import FlyInError, ParseError
from flyin.models import ZoneType
from flyin.parser import MapParser


HUBS = "nb_drones: 2\nstart_hub: s 0 0\nend_hub: e 9 9\n"


def parse_text(tmp_path: Path, text: str) -> MapParser:
    """Write text to a temp file and return a parser on it."""
    file = tmp_path / "map.txt"
    file.write_text(text, encoding="utf-8")
    return MapParser(str(file))


def test_example_map() -> None:
    """The subject's example map parses with the right values."""
    data = MapParser("maps/example.txt").parse()
    assert data.nb_drones == 5
    assert data.start == "hub" and data.end == "goal"
    assert len(data.zones) == 7
    assert data.zones["roof1"].zone_type is ZoneType.RESTRICTED
    assert data.zones["corridorA"].max_drones == 2
    assert data.zones["roof2"].color == "blue"
    assert len(data.connections) == 6
    assert data.connections[4].name == "corridorA-tunnelB"
    assert data.connections[4].max_link_capacity == 2
    assert data.connections[0].max_link_capacity == 1


def test_comments_and_blank_lines(tmp_path: Path) -> None:
    """Comments and empty lines are ignored, even inline."""
    p = parse_text(tmp_path, HUBS.replace("start_hub", "# hi\n\nstart_hub")
                   + "hub: a 1 2 # inline\n")
    data = p.parse()
    assert data.nb_drones == 2 and "a" in data.zones


def test_start_ignores_max_drones(tmp_path: Path) -> None:
    """max_drones on start/end is ignored, not an error."""
    p = parse_text(tmp_path, HUBS.replace("s 0 0", "s 0 0 [max_drones=0]"))
    assert p.parse().zones["s"].unlimited


@pytest.mark.parametrize("text, line", [
    ("hub: a 0 0\n", 1),                           # nb_drones not first
    ("nb_drones: 0\n", 1),                         # not positive
    ("nb_drones: two\n", 1),                       # not an integer
    ("nb_drones: 1\nnb_drones: 2\n", 2),           # twice
    ("nb_drones: 1\nfoo: x\n", 2),                 # unknown keyword
    ("nb_drones: 1\nhub a 0 0\n", 2),              # missing colon
    ("nb_drones: 1\nhub: a-b 0 0\n", 2),           # dash in name
    ("nb_drones: 1\nhub: a 0\n", 2),               # missing y
    ("nb_drones: 1\nhub: a 0 1.5\n", 2),           # float coordinate
    ("nb_drones: 1\nhub: a 0 0\nhub: a 1 1\n", 3),  # duplicate name
    ("nb_drones: 1\nhub: a 0 0 [zone=lava]\n", 2),  # bad zone type
    ("nb_drones: 1\nhub: a 0 0 [max_drones=0]\n", 2),
    ("nb_drones: 1\nhub: a 0 0 [speed=3]\n", 2),   # unknown key
    ("nb_drones: 1\nhub: a 0 0 [color]\n", 2),     # no '='
    ("nb_drones: 1\nhub: a 0 0 [color=red\n", 2),  # unclosed bracket
    ("nb_drones: 1\nstart_hub: a 0 0\nstart_hub: b 0 0\n", 3),
])
def test_errors_report_line(tmp_path: Path, text: str, line: int) -> None:
    """Every invalid line raises ParseError with the right line number."""
    with pytest.raises(ParseError) as info:
        parse_text(tmp_path, text).parse()
    assert info.value.line_no == line


# HUBS is 3 lines, so a bad 4th line must be reported as line 4.
@pytest.mark.parametrize("link", [
    "connection: s-x",                           # unknown zone
    "connection: s-s",                           # self loop
    "connection: s-e-x",                         # three names
    "connection: s-",                            # empty name
    "connection: s e",                           # no dash
    "connection: s-e [max_link_capacity=0]",     # not positive
    "connection: s-e [max_link_capacity=two]",   # not an integer
    "connection: s-e [max_drones=2]",            # zone key on a link
])
def test_connection_errors(tmp_path: Path, link: str) -> None:
    """Every invalid connection line is reported on its own line."""
    with pytest.raises(ParseError) as info:
        parse_text(tmp_path, HUBS + link + "\n").parse()
    assert info.value.line_no == 4


@pytest.mark.parametrize("second", ["s-e", "e-s"])
def test_duplicate_connection(tmp_path: Path, second: str) -> None:
    """a-b and b-a are the same link: the second one is line 5."""
    text = HUBS + "connection: s-e\nconnection: " + second + "\n"
    with pytest.raises(ParseError) as info:
        parse_text(tmp_path, text).parse()
    assert info.value.line_no == 5


@pytest.mark.parametrize("text, reason", [
    ("", "nb_drones"),
    ("# only a comment\n", "nb_drones"),
    ("nb_drones: 1\nend_hub: e 0 0\n", "start_hub"),
    ("nb_drones: 1\nstart_hub: s 0 0\n", "end_hub"),
])
def test_incomplete_file(tmp_path: Path, text: str, reason: str) -> None:
    """Missing nb_drones / start / end is detected after the last line."""
    with pytest.raises(ParseError) as info:
        parse_text(tmp_path, text).parse()
    assert reason in info.value.reason


def test_missing_file() -> None:
    """A missing file is a clean FlyInError, not a crash."""
    with pytest.raises(FlyInError):
        MapParser("does/not/exist.txt").parse()
