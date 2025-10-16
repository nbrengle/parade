"""Tests for export application services."""

from pathlib import Path

import pytest

from parade.adapters.exporters import FileExporter, FileSizeLimitExceededError, PathTraversalError
from parade.application.export import Exporter, export_to


@pytest.fixture
def sample_content() -> str:
    """Create sample content for export testing."""
    return '{"test": "data"}'


@pytest.fixture
def temp_file_path(tmp_path: Path) -> Path:
    """Create a temporary file path for testing."""
    return tmp_path / "test_output.json"


class TestExportTo:
    """Tests for export_to verb."""

    def test_export_to_file(
        self,
        sample_content: str,
        temp_file_path: Path,
        file_exporter: Exporter,
    ) -> None:
        """Test exporting content to a file."""
        result_path = export_to(
            file_exporter,
            sample_content,
            temp_file_path,
        )

        # Verify the file was created
        assert temp_file_path.exists()
        assert temp_file_path.read_text(encoding="utf-8") == sample_content

        # Verify the return value is the absolute path
        assert result_path == str(temp_file_path.absolute())

    def test_export_creates_parent_directories(
        self,
        sample_content: str,
        tmp_path: Path,
        file_exporter: Exporter,
    ) -> None:
        """Test that exporting creates missing parent directories."""
        nested_path = tmp_path / "subdir" / "nested" / "output.json"

        result_path = export_to(
            file_exporter,
            sample_content,
            nested_path,
        )

        # Verify the file and all parent directories were created
        assert nested_path.exists()
        assert nested_path.read_text(encoding="utf-8") == sample_content
        assert result_path == str(nested_path.absolute())


class TestFileExporterSecurity:
    """Tests for FileExporter security features."""

    def test_prevents_path_traversal_with_relative_paths(
        self,
        sample_content: str,
        tmp_path: Path,
    ) -> None:
        """Test that path traversal using .. is prevented."""
        exporter = FileExporter(allowed_base_dir=tmp_path / "safe")
        malicious_path = tmp_path / "safe" / ".." / ".." / "etc" / "passwd"

        with pytest.raises(PathTraversalError) as exc_info:
            exporter.export(sample_content, malicious_path)

        assert exc_info.value.allowed_base == tmp_path / "safe"

    def test_prevents_path_traversal_with_absolute_paths(
        self,
        sample_content: str,
        tmp_path: Path,
    ) -> None:
        """Test that absolute paths outside allowed directory are rejected."""
        exporter = FileExporter(allowed_base_dir=tmp_path / "safe")
        malicious_path = Path("/etc/passwd")

        with pytest.raises(PathTraversalError) as exc_info:
            exporter.export(sample_content, malicious_path)

        assert exc_info.value.allowed_base == tmp_path / "safe"

    def test_allows_paths_within_allowed_directory(
        self,
        sample_content: str,
        tmp_path: Path,
    ) -> None:
        """Test that valid paths within allowed directory work correctly."""
        safe_dir = tmp_path / "safe"
        exporter = FileExporter(allowed_base_dir=safe_dir)
        valid_path = safe_dir / "output.json"

        result = exporter.export(sample_content, valid_path)

        assert valid_path.exists()
        assert valid_path.read_text(encoding="utf-8") == sample_content
        assert result == str(valid_path.absolute())

    def test_defaults_to_current_working_directory(
        self,
        sample_content: str,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that FileExporter defaults to cwd as allowed base directory."""
        monkeypatch.chdir(tmp_path)
        exporter = FileExporter()  # No allowed_base_dir specified

        # Should work for files in cwd
        valid_path = tmp_path / "output.json"
        exporter.export(sample_content, valid_path)
        assert valid_path.exists()

        # Should reject paths outside cwd
        outside_path = tmp_path.parent / "outside.json"
        with pytest.raises(PathTraversalError):
            exporter.export(sample_content, outside_path)

    def test_prevents_large_files_with_default_limit(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that files exceeding the default 100MB limit are rejected."""
        exporter = FileExporter(allowed_base_dir=tmp_path)
        # Create content larger than 100MB
        large_content = "x" * (101 * 1024 * 1024)
        output_path = tmp_path / "large.txt"

        with pytest.raises(FileSizeLimitExceededError) as exc_info:
            exporter.export(large_content, output_path)

        assert exc_info.value.content_size > exc_info.value.max_size
        assert exc_info.value.max_size == FileExporter.DEFAULT_MAX_FILE_SIZE_BYTES

    def test_prevents_large_files_with_custom_limit(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that custom size limits are enforced."""
        max_size = 1024  # 1KB limit
        exporter = FileExporter(allowed_base_dir=tmp_path, max_file_size_bytes=max_size)
        # Create content larger than 1KB
        large_content = "x" * 2048
        output_path = tmp_path / "large.txt"

        with pytest.raises(FileSizeLimitExceededError) as exc_info:
            exporter.export(large_content, output_path)

        assert exc_info.value.content_size == 2048
        assert exc_info.value.max_size == max_size

    def test_allows_files_within_size_limit(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that files within the size limit are accepted."""
        max_size = 1024  # 1KB limit
        exporter = FileExporter(allowed_base_dir=tmp_path, max_file_size_bytes=max_size)
        small_content = "x" * 512  # 512 bytes
        output_path = tmp_path / "small.txt"

        result = exporter.export(small_content, output_path)

        assert output_path.exists()
        assert output_path.read_text(encoding="utf-8") == small_content
        assert result == str(output_path.absolute())

    def test_size_limit_can_be_disabled(
        self,
        tmp_path: Path,
    ) -> None:
        """Test that size limits can be disabled by setting to None."""
        exporter = FileExporter(allowed_base_dir=tmp_path, max_file_size_bytes=None)

        # Verify that the size limit is disabled
        assert exporter.max_file_size_bytes is None

        # Note: We don't actually test writing a 101MB file to keep tests fast,
        # but the None value means the size check in export() will be skipped
