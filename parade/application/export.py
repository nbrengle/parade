"""Application layer for exporting formatted content to different destinations."""

from collections.abc import Callable
from enum import StrEnum
from functools import partial
from pathlib import Path
from typing import Protocol


class ExportDestination(StrEnum):
    """Supported export destinations for formatted content."""

    FILE = "file"


class Exporter(Protocol):
    """Protocol for exporting formatted content to specific destinations."""

    def export(self, content: str, path: Path) -> str:
        """Export the formatted content to the target destination.

        Args:
            content: The formatted content to export.
            path: Path/location for the export. Interpretation depends on destination.

        Returns:
            String describing where the content was exported (e.g., file path).
        """
        ...


# Registry for exporters
exporter_registry: dict[ExportDestination, Exporter] = {}


def exporter(destination: ExportDestination) -> Callable[[type[Exporter]], type[Exporter]]:
    """Decorator to register an exporter for a specific destination.

    Args:
        destination: The export destination this exporter handles.

    Returns:
        Decorator function that registers the exporter class.

    Example:
        @exporter(ExportDestination.FILE)
        class FileExporter:
            def export(self, content: str, path: Path) -> str:
                ...
    """

    def decorator(cls: type[Exporter]) -> type[Exporter]:
        exporter_registry[destination] = cls()
        return cls

    return decorator


def export_to_using(
    registry: dict[ExportDestination, Exporter],
    destination: ExportDestination,
    content: str,
    path: Path,
) -> str:
    """Export formatted content using a specific registry.

    This is the full interface that accepts a registry for dependency injection.
    Most code should use the `export_to` convenience function instead.

    Args:
        registry: The exporter registry to use.
        destination: The target export destination.
        content: The formatted content to export.
        path: Path/location for the export.

    Returns:
        String describing where the content was exported.

    Raises:
        KeyError: If the destination is not registered.
    """
    exporter_impl = registry[destination]
    return exporter_impl.export(content, path)


# Convenience function with default global registry
export_to = partial(export_to_using, exporter_registry)
