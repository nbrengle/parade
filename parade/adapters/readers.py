"""Readers for getting input from various sources."""

import logging
import sys
from pathlib import Path

from parade.application.read import InputReader

__all__ = ["FileReader", "StdinReader"]

logger = logging.getLogger(__name__)


class FileReader(InputReader):
    """Reader that reads content from files."""

    def read(self, source: Path | None = None) -> str:
        """Read content from a file.

        Args:
            source: Path to the file to read. Must be provided.

        Returns:
            The file content as a string.

        Raises:
            ValueError: If source is None.
            OSError: If file cannot be read (doesn't exist, permission denied, etc).
        """
        if source is None:
            msg = "FileReader requires a source path"
            raise ValueError(msg)

        logger.debug("Reading file from %s", source)

        try:
            content = source.read_text(encoding="utf-8")
        except OSError:
            logger.exception("Failed to read file %s", source)
            raise
        else:
            logger.info("Successfully read %d characters from %s", len(content), source)
            return content


class StdinReader(InputReader):
    """Reader that reads content from standard input."""

    def read(self, source: Path | None = None) -> str:
        """Read content from standard input.

        Args:
            source: Ignored (stdin doesn't use a path). Required by InputReader protocol.

        Returns:
            The stdin content as a string.

        Raises:
            OSError: If stdin cannot be read.
        """
        # source parameter required by InputReader protocol but unused for stdin
        _ = source
        logger.debug("Reading from stdin")

        try:
            content = sys.stdin.read()
        except OSError:
            logger.exception("Failed to read from stdin")
            raise
        else:
            logger.info("Successfully read %d characters from stdin", len(content))
            return content
