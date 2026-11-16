"""Entry point: ''python3 fly_in.py <map_file>''."""

import sys

from flyin.errors import FlyInError
from flyin.parser import MapParser


def main(argv: list[str]) -> int:
    """Run the programm and return the process exit code."""
    if len(argv) != 2:
        print(f"usage: {argv[0]} <map_file>", file=sys.stderr)
        return 1
    try:
        data = MapParser(argv[1]).parse()
        print(f"{data.nb_drones} drones, {len(data.zones)} zones, "
              f"start={data.start}, end={data.end}")
        for zone in data.values():
            print(f" {zone.name:<12} {zone.zone_type.value:<10} "
                  f"max={zone.max_drones} color={zone.color}")
    except FlyInError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
