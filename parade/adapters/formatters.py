"""Formatters for converting project networks to various output formats."""

import json

from parade.application.format import ProjectFormatter
from parade.domain.project_network import ScheduledProjectNetwork


class JSONFormatter(ProjectFormatter):
    """Formatter that converts project networks to JSON."""

    def format(self, network: ScheduledProjectNetwork) -> str:
        """Convert project network to JSON string.

        Args:
            network: The scheduled project network to format.

        Returns:
            JSON string representation of the project network.
        """
        data = {
            "project_duration": str(network.project_duration.value),
            "activities": [
                {
                    "name": activity.name.value,
                    "duration": str(activity.duration.value),
                    "dependencies": sorted(dep.value for dep in activity.dependencies),
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
        return json.dumps(data, indent=2)
