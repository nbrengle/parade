"""Exporters for writing formatted content to various destinations."""

import logging
from pathlib import Path

from parade.application.export import Exporter

__all__ = ["FileExporter", "FileSizeLimitExceededError", "PathTraversalError"]

logger = logging.getLogger(__name__)


class PathTraversalError(ValueError):
    """Raised when a path attempts to escape the allowed base directory."""

    def __init__(self, attempted_path: Path, allowed_base: Path) -> None:
        """Initialize the error with path details.

        Args:
            attempted_path: The path that was rejected.
            allowed_base: The base directory that paths must be within.
        """
        super().__init__(
            f"Path '{attempted_path}' is outside allowed base directory '{allowed_base}'. "
            "Path traversal attempts are not permitted."
        )
        self.attempted_path = attempted_path
        self.allowed_base = allowed_base


class FileSizeLimitExceededError(ValueError):
    """Raised when attempting to write content that exceeds the maximum allowed file size."""

    def __init__(self, content_size: int, max_size: int) -> None:
        """Initialize the error with size details.

        Args:
            content_size: The size of the content attempting to be written (in bytes).
            max_size: The maximum allowed file size (in bytes).
        """
        super().__init__(
            f"Content size ({content_size:,} bytes) exceeds maximum allowed file size ({max_size:,} bytes). "
            "This limit prevents disk exhaustion attacks."
        )
        self.content_size = content_size
        self.max_size = max_size


class FileExporter(Exporter):
    """Exporter that writes content to files with security constraints.

    Security features:
    - Path traversal protection: All paths must be within allowed_base_dir
    - File size limits: Prevents disk exhaustion by limiting max file size
    - Atomic writes: Uses temp file + rename to prevent corruption
    - Parent directory creation: Automatically creates missing parent directories

    Note: Currently only supports string content. In the future, we may need to
    support other content types (bytes, structured data, etc.) for different
    export formats.
    """

    # Default maximum file size: 100MB
    # This is generous for JSON/text exports but prevents abuse
    DEFAULT_MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024

    def __init__(
        self,
        allowed_base_dir: Path,
        max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    ) -> None:
        """Initialize the file exporter with security constraints.

        Args:
            allowed_base_dir: Base directory that all exported files must be within.
                            This prevents path traversal attacks.
            max_file_size_bytes: Maximum allowed file size in bytes. Defaults to 100MB.
        """
        self.allowed_base_dir = allowed_base_dir.resolve()
        self.max_file_size_bytes = max_file_size_bytes

    def export(self, content: str, path: Path) -> Path:
        """Write content to a file with security and reliability safeguards.

        Args:
            content: The formatted content to write.
            path: File path where content should be written. Must be within
                 the allowed base directory.

        Returns:
            The absolute path where the file was written.

        Raises:
            PathTraversalError: If the path attempts to escape allowed_base_dir.
            FileSizeLimitExceededError: If content exceeds max_file_size_bytes.
            OSError: If file operations fail (permission denied, disk full, etc).
        """
        logger.debug("Starting file export to %s", path)

        # Check file size limit before attempting to write
        content_bytes = content.encode("utf-8")
        content_size = len(content_bytes)

        if content_size > self.max_file_size_bytes:
            logger.warning(
                "File size limit exceeded: %d bytes > %d bytes max",
                content_size,
                self.max_file_size_bytes,
            )
            raise FileSizeLimitExceededError(content_size, self.max_file_size_bytes)

        # Resolve to absolute path and validate it's within allowed directory
        absolute_path = path.resolve()

        if not absolute_path.is_relative_to(self.allowed_base_dir):
            logger.warning(
                "Path traversal attempt blocked: %s outside %s",
                absolute_path,
                self.allowed_base_dir,
            )
            raise PathTraversalError(absolute_path, self.allowed_base_dir)

        # Ensure parent directory exists
        absolute_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Created parent directories for %s", absolute_path)

        # Atomic write: write to temp file, then rename
        # This prevents corruption if the process crashes during write
        temp_path = absolute_path.with_suffix(absolute_path.suffix + ".tmp")

        try:
            logger.debug("Writing %d bytes to temporary file %s", content_size, temp_path)
            temp_path.write_bytes(content_bytes)  # Use write_bytes since we already encoded
            temp_path.replace(absolute_path)  # Atomic on POSIX systems
            logger.info("Successfully exported %d bytes to %s", content_size, absolute_path)
        except OSError:
            logger.exception("Failed to write file %s", absolute_path)
            # Clean up temp file on any error
            temp_path.unlink(missing_ok=True)
            raise

        return absolute_path
