"""Application layer for reading input from different sources."""

from abc import ABC, abstractmethod
from enum import StrEnum, auto
from pathlib import Path

__all__ = ["InputReader", "InputSource", "read_from"]


class InputSource(StrEnum):
    """Supported input sources for project data."""

    FILE = auto()
    STDIN = auto()


class InputReader(ABC):
    """Abstract base class for reading input from specific sources."""

    @abstractmethod
    def read(self, source: Path | None = None) -> str:
        """Read input from the source.

        Args:
            source: The source location (interpretation depends on the reader).
                   For FILE: Path to the file
                   For STDIN: None (ignored)

        Returns:
            The raw content as a string.

        Raises:
            OSError: If reading fails.
        """


def read_from(reader: InputReader, source: Path | None = None) -> str:
    """Read input using the provided reader.

    Args:
        reader: The reader implementation to use.
        source: The source location (optional, depends on reader type).

    Returns:
        The raw content as a string.
    """
    return reader.read(source)
