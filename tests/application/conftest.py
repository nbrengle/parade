"""Shared fixtures for application layer tests."""

from pathlib import Path

import pytest

from parade.adapters.exporters import FileExporter
from parade.adapters.formatters import JSONFormatter
from parade.application.export import Exporter
from parade.application.format import ProjectFormatter


@pytest.fixture
def json_formatter() -> ProjectFormatter:
    """Create a JSON formatter instance."""
    return JSONFormatter()


@pytest.fixture
def file_exporter(tmp_path: Path) -> Exporter:
    """Create a file exporter with tmp_path as allowed base dir."""
    return FileExporter(allowed_base_dir=tmp_path)
