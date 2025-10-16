"""Entry point for the Parade CLI application.

This module serves as the composition root where dependency injection is configured.
All service wiring happens here, inline and visible.
"""

import argparse
import sys
from pathlib import Path

import punq

from parade.adapters.exporters import FileExporter
from parade.adapters.formatters import JSONFormatter
from parade.application.export import ExportDestination, Exporter
from parade.application.format import OutputFormat, ProjectFormatter


def main() -> int:
    """Main entry point for the Parade CLI.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = argparse.ArgumentParser(description="Parade - Domain-driven project planning tool")
    parser.add_argument(
        "--format",
        type=str,
        default=OutputFormat.JSON.value,
        choices=[f.value for f in OutputFormat],
        help="Output format for the project network",
    )
    parser.add_argument(
        "--destination",
        type=str,
        default=ExportDestination.FILE.value,
        choices=[d.value for d in ExportDestination],
        help="Export destination for the formatted output",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("project.json"),
        help="Output file path",
    )

    args = parser.parse_args()

    # Wire up container INLINE - all visible here
    container = punq.Container()

    # Register formatters by tag
    container.register(
        ProjectFormatter,
        instance=JSONFormatter(),
        tag=OutputFormat.JSON.value,
    )

    # Register exporters by tag
    container.register(
        Exporter,
        instance=FileExporter(
            allowed_base_dir=Path.cwd(),
            max_file_size_bytes=None,  # No size limit for CLI use
        ),
        tag=ExportDestination.FILE.value,
    )

    # Resolve services at boundary
    _ = container.resolve(ProjectFormatter, tag=args.format)
    _ = container.resolve(Exporter, tag=args.destination)

    # Placeholder for future implementation:
    # When we have actual project input, we'll:
    # 1. Read/parse project data
    # 2. Schedule the network
    # 3. Format using resolved formatter
    # 4. Export using resolved exporter

    # For now, just verify the wiring works
    sys.stdout.write(
        f"Parade CLI - Format: {args.format}, Destination: {args.destination}, Output: {args.output}\n"
        "Note: Full project input/scheduling not yet implemented\n"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
