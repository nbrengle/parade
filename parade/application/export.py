"""Application layer for exporting formatted content to different destinations."""

from abc import ABC, abstractmethod
from enum import StrEnum, auto
from pathlib import Path

__all__ = ["ExportDestination", "Exporter", "export_to"]


class ExportDestination(StrEnum):
    """Supported export destinations for formatted content."""

    FILE = auto()


class Exporter(ABC):
    """Abstract base class for exporting formatted content to specific destinations."""

    @abstractmethod
    def export(self, content: str, path: Path) -> Path:
        """Export the formatted content to the target destination.

        Args:
            content: The formatted content to export.
            path: Path/location for the export. Interpretation depends on destination.

        Returns:
            Path where the content was exported.
        """


def export_to(exporter: Exporter, path: Path, content: str) -> Path:
    """Export formatted content using the provided exporter.

    Args:
        exporter: The exporter implementation to use.
        path: Path/location for the export.
        content: The formatted content to export.

    Returns:
        Path where the content was exported.
    """
    return exporter.export(content, path)
