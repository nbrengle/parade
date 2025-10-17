"""Exporters for writing formatted content to various destinations."""

from pathlib import Path

from parade.application.export import ExportDestination, exporter


@exporter(ExportDestination.FILE)
class FileExporter:
    """Exporter that writes content to files.

    Note: Currently only supports string content. In the future, we may need to
    support other content types (bytes, structured data, etc.) for different
    export formats.
    """

    def export(self, content: str, path: Path) -> str:
        """Write content to a file.

        Args:
            content: The formatted content to write.
            path: File path where content should be written.

        Returns:
            The absolute path where the file was written.
        """
        path.write_text(content, encoding="utf-8")
        return str(path.absolute())
