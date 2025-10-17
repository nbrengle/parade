"""Application layer for formatting project networks into different output formats."""

from collections.abc import Callable
from enum import StrEnum
from functools import partial
from typing import Protocol

from parade.domain.project_network import ScheduledProjectNetwork


class OutputFormat(StrEnum):
    """Supported output formats for project networks."""

    JSON = "json"


class ProjectFormatter(Protocol):
    """Protocol for formatting project networks into specific output formats."""

    def format(self, network: ScheduledProjectNetwork) -> str:
        """Format the project network into the target representation.

        Args:
            network: The scheduled project network to format.

        Returns:
            String representation in the target format.
        """
        ...


# Registry for formatters
formatter_registry: dict[OutputFormat, ProjectFormatter] = {}


def formatter(format_type: OutputFormat) -> Callable[[type[ProjectFormatter]], type[ProjectFormatter]]:
    """Decorator to register a formatter for a specific output format.

    Args:
        format_type: The output format this formatter handles.

    Returns:
        Decorator function that registers the formatter class.

    Example:
        @formatter(OutputFormat.JSON)
        class JSONFormatter:
            def format(self, network: ScheduledProjectNetwork) -> str:
                ...
    """

    def decorator(cls: type[ProjectFormatter]) -> type[ProjectFormatter]:
        formatter_registry[format_type] = cls()
        return cls

    return decorator


def format_as_using(
    registry: dict[OutputFormat, ProjectFormatter],
    format_type: OutputFormat,
    network: ScheduledProjectNetwork,
) -> str:
    """Format a project network using a specific registry.

    This is the full interface that accepts a registry for dependency injection.
    Most code should use the `format_as` convenience function instead.

    Args:
        registry: The formatter registry to use.
        format_type: The desired output format.
        network: The scheduled project network to format.

    Returns:
        String representation in the specified format.

    Raises:
        KeyError: If the format type is not registered.
    """
    formatter_impl = registry[format_type]
    return formatter_impl.format(network)


# Convenience function with default global registry
format_as = partial(format_as_using, formatter_registry)
