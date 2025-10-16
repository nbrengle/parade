"""Application layer for exporting formatted content to different destinations."""

from abc import ABC, abstractmethod
from enum import StrEnum, auto
from pathlib import Path


class ExportDestination(StrEnum):
    """Supported export destinations for formatted content."""

    FILE = auto()


class Exporter(ABC):
    """Abstract base class for exporting formatted content to specific destinations."""

    @abstractmethod
    def export(self, content: str, path: Path) -> str:
        """Export the formatted content to the target destination.

        Args:
            content: The formatted content to export.
            path: Path/location for the export. Interpretation depends on destination.

        Returns:
            String describing where the content was exported (e.g., file path).
        """


def export_to(exporter: Exporter, content: str, path: Path) -> str:
    """Export formatted content using the provided exporter.

    Args:
        exporter: The exporter implementation to use.
        content: The formatted content to export.
        path: Path/location for the export.

    Returns:
        String describing where the content was exported.
    """
    return exporter.export(content, path)
