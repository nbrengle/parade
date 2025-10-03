"""Project network domain models for Critical Path Method."""

from dataclasses import dataclass

from parade.domain.activity import (
    ActivityName,
    Duration,
    ScheduledActivity,
    UnscheduledActivity,
)


@dataclass(frozen=True)
class UnscheduledProjectNetwork:
    """Value object representing a validated network of unscheduled activities.

    Validates at construction that:
    - All activity names are unique
    - All dependency references exist
    - No circular dependencies exist
    """

    activities: frozenset[UnscheduledActivity]

    def __post_init__(self) -> None:
        """Validate the project network."""
        self._validate_not_empty()
        self._validate_unique_ids()
        self._validate_dependencies_exist()
        self._validate_no_cycles()

    def _validate_not_empty(self) -> None:
        """Ensure the network has at least one activity."""
        if not self.activities:
            msg = "Project network must contain at least one activity"
            raise ValueError(msg)

    def _validate_unique_ids(self) -> None:
        """Ensure all activity names are unique."""
        ids = [activity.name for activity in self.activities]
        if len(ids) != len(set(ids)):
            msg = "Activity names must be unique"
            raise ValueError(msg)

    def _validate_dependencies_exist(self) -> None:
        """Ensure all dependency references point to existing activities."""
        activity_ids = {activity.name for activity in self.activities}
        for activity in self.activities:
            for dependency_id in activity.dependencies:
                if dependency_id not in activity_ids:
                    msg = f"Activity {activity.name.value} depends on non-existent activity {dependency_id.value}"
                    raise ValueError(msg)

    def _validate_no_cycles(self) -> None:
        """Ensure the dependency graph has no cycles."""
        # Build adjacency list for DFS
        graph: dict[ActivityName, set[ActivityName]] = {
            activity.name: set(activity.dependencies) for activity in self.activities
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

        for activity_id in graph:
            if has_cycle(activity_id):
                msg = "Project network contains circular dependencies"
                raise ValueError(msg)


@dataclass(frozen=True)
class ScheduledProjectNetwork:
    """Value object representing a network of scheduled activities."""

    activities: frozenset[ScheduledActivity]

    @property
    def project_duration(self) -> Duration:
        """Calculate the total project duration.

        Project duration is the maximum earliest finish time across all activities.
        This represents the minimum time required to complete the entire project.
        """
        return max(activity.earliest_finish for activity in self.activities)
