"""Entry point: ''python3 fly_in.py <map_file>''."""

import sys

from flyin.errors import FlyInError


def main(argv: list[str]) -> int:
    """Run the programm and return the process exit code."""
    if len(argv) != 2:
        print(f"usage: {argv[0]} <map_file>", file=sys.stderr)
        return 1
    try:
        # Parser, scheduler and simulation are added soon.
        print(f"Fly-in: map file '{argv[1]}' received (wip)")
    except FlyInError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
