"""Custom exceptions used across the Fly-in project."""


class FlyInError(Exception):
    """Base class for every error raised by this project."""


class ParseError(FlyInError):
    """Raised when the map file is syntactically or logically invalid.

    Attributes:
        line_no: 1-based line number where the problem was found.
        reason: Human readable explanation of the problem.
    """


def __init__(self, line_no: int, reason: str) -> None:
    """Store the line number and reason and build the message"""
    self.line_no: int = line_no
    self.reason: str = reason
    super().__init__(f"line {line_no}: {reason}")


class NoPathError(FlyInError):
    """Raised when no valid path connects the start and end hubs."""
