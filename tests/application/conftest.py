"""Shared fixtures for application layer tests."""

import pytest

from parade.adapters.exporters import FileExporter
from parade.adapters.formatters import JSONFormatter
from parade.application.export import ExportDestination, Exporter
from parade.application.format import OutputFormat, ProjectFormatter


@pytest.fixture
def test_formatter_registry() -> dict[OutputFormat, ProjectFormatter]:
    """Create a test-local formatter registry."""
    registry: dict[OutputFormat, ProjectFormatter] = {}
    registry[OutputFormat.JSON] = JSONFormatter()
    return registry


@pytest.fixture
def test_exporter_registry() -> dict[ExportDestination, Exporter]:
    """Create a test-local exporter registry."""
    registry: dict[ExportDestination, Exporter] = {}
    registry[ExportDestination.FILE] = FileExporter()
    return registry
