"""Tests for reading input from various sources."""

from pathlib import Path
from unittest.mock import patch

import pytest

from parade.adapters.readers import FileReader, StdinReader
from parade.application.read import InputReader, read_from


@pytest.fixture
def file_reader() -> InputReader:
    """Create a file reader instance."""
    return FileReader()


@pytest.fixture
def stdin_reader() -> InputReader:
    """Create a stdin reader instance."""
    return StdinReader()


class TestFileReader:
    """Tests for FileReader."""

    def test_read_file(self, file_reader: InputReader, tmp_path: Path) -> None:
        """Test reading content from a file."""
        test_file = tmp_path / "test.csv"
        test_content = "activity_name,duration,depends_on\nA,5,"
        test_file.write_text(test_content, encoding="utf-8")

        result = read_from(file_reader, test_file)

        assert result == test_content

    def test_read_file_no_source_raises_error(self, file_reader: InputReader) -> None:
        """Test that reading without a source raises ValueError."""
        with pytest.raises(ValueError, match="requires a source path"):
            file_reader.read(None)

    def test_read_file_not_found_raises_error(self, file_reader: InputReader, tmp_path: Path) -> None:
        """Test that reading non-existent file raises OSError."""
        non_existent = tmp_path / "does_not_exist.csv"

        with pytest.raises(FileNotFoundError):
            file_reader.read(non_existent)

    def test_read_file_with_utf8(self, file_reader: InputReader, tmp_path: Path) -> None:
        """Test reading file with UTF-8 characters."""
        test_file = tmp_path / "utf8.csv"
        test_content = "activity_name,duration,depends_on\nÜber,5,\nCafé,3,Über"
        test_file.write_text(test_content, encoding="utf-8")

        result = file_reader.read(test_file)

        assert result == test_content
        assert "Über" in result
        assert "Café" in result


class TestStdinReader:
    """Tests for StdinReader."""

    def test_read_stdin(self, stdin_reader: InputReader) -> None:
        """Test reading content from stdin."""
        test_content = "activity_name,duration,depends_on\nA,5,"

        with patch("sys.stdin.read", return_value=test_content):
            result = stdin_reader.read()

        assert result == test_content

    def test_read_stdin_ignores_source(self, stdin_reader: InputReader) -> None:
        """Test that stdin reader ignores the source parameter."""
        test_content = "activity_name,duration,depends_on\nA,5,"

        with patch("sys.stdin.read", return_value=test_content):
            result = stdin_reader.read(source=Path("/ignored/path"))

        assert result == test_content

    def test_read_stdin_error_raises_oserror(self, stdin_reader: InputReader) -> None:
        """Test that stdin read errors are propagated."""
        with (
            patch("sys.stdin.read", side_effect=OSError("Read error")),
            pytest.raises(OSError, match="Read error"),
        ):
            stdin_reader.read()
