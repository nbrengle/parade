"""Project network domain models for Critical Path Method."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypeVar

from parade.domain.activity import (
    Activity,
    ActivityName,
    Duration,
    ScheduledActivity,
    UnscheduledActivity,
)

ActivityT = TypeVar("ActivityT", bound=Activity)


def _validate_not_empty(activities: Iterable[Activity]) -> None:
    """Ensure the network has at least one activity."""
    # Convert to list to check if empty (iterables might be consumed)
    activities_list = list(activities)
    if not activities_list:
        msg = "Project network must contain at least one activity"
        raise ValueError(msg)


def _validate_unique_names(activities: Iterable[Activity]) -> None:
    """Ensure all activity names are unique."""
    names = [activity.name for activity in activities]
    if len(names) != len(set(names)):
        msg = "Activity names must be unique"
        raise ValueError(msg)


def _validate_dependencies_exist(activities: Iterable[Activity]) -> None:
    """Ensure all dependency references point to existing activities."""
    activities_list = list(activities)
    activity_names = {activity.name for activity in activities_list}
    for activity in activities_list:
        for dependency_name in activity.dependencies:
            if dependency_name not in activity_names:
                msg = f"Activity {activity.name.value} depends on non-existent activity {dependency_name.value}"
                raise ValueError(msg)


def _validate_no_cycles(activities: Iterable[Activity]) -> None:
    """Ensure the dependency graph has no cycles."""
    # Build adjacency list for DFS
    graph: dict[ActivityName, set[ActivityName]] = {
        activity.name: set(activity.dependencies) for activity in activities
    }

    # Track visited nodes and nodes in current path
    visited: set[ActivityName] = set()
    in_path: set[ActivityName] = set()

    def has_cycle(node: ActivityName) -> bool:
        """Perform DFS to detect cycles."""
        if node in in_path:
            return True
        if node in visited:
            return False

        visited.add(node)
        in_path.add(node)

        for dependency in graph.get(node, set()):
            if has_cycle(dependency):
                return True

        in_path.remove(node)
        return False

    for activity_name in graph:
        if has_cycle(activity_name):
            msg = "Project network contains circular dependencies"
            raise ValueError(msg)


@dataclass(frozen=True)
class ProjectNetwork[ActivityT]:
    """Generic base class for validated project networks.

    Validates at construction that:
    - Network is not empty
    - All activity names are unique
    - All dependency references exist
    - No circular dependencies exist

    Type parameter ActivityT ensures type safety for the specific activity type.
    """

    activities: frozenset[ActivityT]

    def __init__(self, activities: Iterable[Activity]) -> None:
        """Create and validate a project network.

        Args:
            activities: Any iterable of Activity objects (UnscheduledActivity or ScheduledActivity).
                       Will be validated and stored as a frozenset.
        """
        _validate_not_empty(activities)
        _validate_unique_names(activities)
        _validate_dependencies_exist(activities)
        _validate_no_cycles(activities)

        # Store validated activities as frozenset
        object.__setattr__(self, "activities", frozenset(activities))


class UnscheduledProjectNetwork(ProjectNetwork[UnscheduledActivity]):
    """Value object representing a validated network of unscheduled activities."""


class ScheduledProjectNetwork(ProjectNetwork[ScheduledActivity]):
    """Value object representing a validated network of scheduled activities."""

    @property
    def project_duration(self) -> Duration:
        """Calculate the total project duration.

        Project duration is the maximum earliest finish time across all activities.
        This represents the minimum time required to complete the entire project.
        """
        return max(activity.earliest_finish for activity in self.activities)
