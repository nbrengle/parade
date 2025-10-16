"""Application layer for formatting project networks into different output formats."""

from abc import ABC, abstractmethod
from enum import StrEnum, auto

from parade.domain.project_network import ScheduledProjectNetwork


class OutputFormat(StrEnum):
    """Supported output formats for project networks."""

    JSON = auto()


class ProjectFormatter(ABC):
    """Abstract base class for formatting project networks into specific output formats."""

    @abstractmethod
    def format(self, network: ScheduledProjectNetwork) -> str:
        """Format the project network into the target representation.

        Args:
            network: The scheduled project network to format.

        Returns:
            String representation in the target format.
        """


def format_as(formatter: ProjectFormatter, network: ScheduledProjectNetwork) -> str:
    """Format a project network using the provided formatter.

    Args:
        formatter: The formatter implementation to use.
        network: The scheduled project network to format.

    Returns:
        String representation in the specified format.
    """
    return formatter.format(network)
