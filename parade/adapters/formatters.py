"""Formatters for converting project networks to various output formats."""

import json
import logging

from parade.application.format import ProjectFormatter
from parade.domain.project_network import ScheduledProjectNetwork

__all__ = ["JSONFormatter"]

logger = logging.getLogger(__name__)


class JSONFormatter(ProjectFormatter):
    """Formatter that converts project networks to JSON."""

    def format(self, network: ScheduledProjectNetwork) -> str:
        """Convert project network to JSON string.

        Args:
            network: The scheduled project network to format.

        Returns:
            JSON string representation of the project network.
        """
        logger.debug("Starting JSON formatting for network with %d activities", len(network.activities))

        data = {
            "project_duration": str(network.project_duration.value),
            "activities": [
                {
                    "name": activity.name.value,
                    "duration": str(activity.duration.value),
                    "dependencies": [dep.value for dep in activity.dependencies],
                    "earliest_start": str(activity.earliest_start.value),
                    "earliest_finish": str(activity.earliest_finish.value),
                    "latest_start": str(activity.latest_start.value),
                    "latest_finish": str(activity.latest_finish.value),
                    "total_float": str(activity.total_float.value),
                    "is_critical": activity.is_critical,
                }
                for activity in network.activities
            ],
        }
        result = json.dumps(data, indent=2)
        logger.info("Formatted network as JSON: %d characters", len(result))
        return result
