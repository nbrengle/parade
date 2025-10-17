"""Tests for export application services."""

from pathlib import Path

import pytest

from parade.adapters.exporters import FileExporter
from parade.application.export import ExportDestination, Exporter, export_to_using


@pytest.fixture
def sample_content() -> str:
    """Create sample content for export testing."""
    return '{"test": "data"}'


@pytest.fixture
def temp_file_path(tmp_path: Path) -> Path:
    """Create a temporary file path for testing."""
    return tmp_path / "test_output.json"


@pytest.fixture
def test_exporter_registry() -> dict[ExportDestination, Exporter]:
    """Create a test-local exporter registry."""
    registry: dict[ExportDestination, Exporter] = {}
    registry[ExportDestination.FILE] = FileExporter()
    return registry


class TestExporterRegistry:
    """Tests for the exporter registry."""

    def test_file_exporter_is_registered(
        self,
        test_exporter_registry: dict[ExportDestination, Exporter],
    ) -> None:
        """Test that FileExporter is registered in the test registry."""
        assert ExportDestination.FILE in test_exporter_registry
        assert isinstance(test_exporter_registry[ExportDestination.FILE], FileExporter)


class TestExportTo:
    """Tests for export_to verb."""

    def test_export_to_file(
        self,
        sample_content: str,
        temp_file_path: Path,
        test_exporter_registry: dict[ExportDestination, Exporter],
    ) -> None:
        """Test exporting content to a file."""
        result_path = export_to_using(
            test_exporter_registry,
            ExportDestination.FILE,
            sample_content,
            temp_file_path,
        )

        # Verify the file was created
        assert temp_file_path.exists()
        assert temp_file_path.read_text(encoding="utf-8") == sample_content

        # Verify the return value is the absolute path
        assert result_path == str(temp_file_path.absolute())

    def test_export_to_unknown_destination_raises_error(
        self,
        sample_content: str,
        tmp_path: Path,
    ) -> None:
        """Test that exporting to an unregistered destination raises KeyError."""
        # Create an empty registry to test error handling
        empty_registry: dict[ExportDestination, Exporter] = {}

        with pytest.raises(KeyError):
            export_to_using(empty_registry, ExportDestination.FILE, sample_content, tmp_path / "test.json")
