"""Exporters for writing formatted content to various destinations."""

from pathlib import Path

from parade.application.export import ExportDestination, exporter


@exporter(ExportDestination.FILE)
class FileExporter:
    """Exporter that writes content to files."""

    def export(self, content: str, path: str | None = None) -> str:
        """Write content to a file.

        Args:
            content: The formatted content to write.
            path: Optional file path. If not provided, defaults to "project.json".

        Returns:
            The absolute path where the file was written.
        """
        if path is None:
            path = "project.json"

        file_path = Path(path)
        file_path.write_text(content, encoding="utf-8")

        return str(file_path.absolute())
