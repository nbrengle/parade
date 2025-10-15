"""Scheduling domain service for Critical Path Method."""

from dataclasses import dataclass
from decimal import Decimal

from parade.domain.activity import (
    ActivityName,
    Duration,
    ScheduledActivity,
    UnscheduledActivity,
)
from parade.domain.project_network import (
    ScheduledProjectNetwork,
    UnscheduledProjectNetwork,
)


@dataclass(frozen=True)
class ForwardPassResult:
    """Result of the forward pass calculation.

    Contains earliest start/finish times and the overall project end time.
    """

    earliest_starts: dict[ActivityName, Duration]
    earliest_finishes: dict[ActivityName, Duration]
    project_end: Duration


@dataclass(frozen=True)
class BackwardPassResult:
    """Result of the backward pass calculation.

    Contains latest start/finish times for all activities.
    """

    latest_starts: dict[ActivityName, Duration]
    latest_finishes: dict[ActivityName, Duration]


def schedule(network: UnscheduledProjectNetwork) -> ScheduledProjectNetwork:
    """Calculate the schedule using the Critical Path Method.

    Performs forward pass to calculate earliest start/finish times,
    then backward pass to calculate latest start/finish times.
    """
    # Create lookup for activities by ID (shared by both passes)
    activity_map = {activity.name: activity for activity in network.activities}

    # Forward pass: calculate earliest start and finish times
    forward_result = _forward_pass(network, activity_map)

    # Backward pass: calculate latest start and finish times
    backward_result = _backward_pass(network, activity_map, forward_result)

    # Create scheduled activities
    scheduled_activities = frozenset(
        ScheduledActivity(
            name=activity.name,
            duration=activity.duration,
            depends_on=activity.dependencies,
            earliest_start=forward_result.earliest_starts[activity.name],
            earliest_finish=forward_result.earliest_finishes[activity.name],
            latest_start=backward_result.latest_starts[activity.name],
            latest_finish=backward_result.latest_finishes[activity.name],
        )
        for activity in network.activities
    )

    return ScheduledProjectNetwork(activities=scheduled_activities)


def _forward_pass(
    network: UnscheduledProjectNetwork,
    activity_map: dict[ActivityName, UnscheduledActivity],
) -> ForwardPassResult:
    """Calculate earliest start and finish times for all activities.

    Returns:
        ForwardPassResult containing earliest times and project end.
    """
    earliest_starts: dict[ActivityName, Duration] = {}
    earliest_finishes: dict[ActivityName, Duration] = {}

    # Process activities in topological order
    def calculate_earliest(activity_name: ActivityName) -> None:
        """Recursively calculate earliest times."""
        if activity_name in earliest_starts:
            return

        activity = activity_map[activity_name]

        # Calculate earliest start based on dependencies
        if not activity.dependencies:
            # No dependencies - can start at time 0
            earliest_starts[activity_name] = Duration(Decimal(0))
        else:
            # Must wait for all dependencies to finish
            for dependency_name in activity.dependencies:
                calculate_earliest(dependency_name)

            max_finish = max(earliest_finishes[dependency_name] for dependency_name in activity.dependencies)
            earliest_starts[activity_name] = max_finish

        # Earliest finish = earliest start + duration
        earliest_finishes[activity_name] = earliest_starts[activity_name] + activity.duration

    # Calculate for all activities
    for activity in network.activities:
        calculate_earliest(activity.name)

    # Find project completion time
    project_end = max(earliest_finishes.values())

    return ForwardPassResult(
        earliest_starts=earliest_starts,
        earliest_finishes=earliest_finishes,
        project_end=project_end,
    )


def _backward_pass(
    network: UnscheduledProjectNetwork,
    activity_map: dict[ActivityName, UnscheduledActivity],
    forward_result: ForwardPassResult,
) -> BackwardPassResult:
    """Calculate latest start and finish times for all activities.

    Args:
        network: The project network.
        activity_map: Lookup dictionary for activities by name.
        forward_result: Results from the forward pass.

    Returns:
        BackwardPassResult containing latest start/finish times.
    """
    latest_starts: dict[ActivityName, Duration] = {}
    latest_finishes: dict[ActivityName, Duration] = {}

    # Build reverse dependency map (successors)
    successors: dict[ActivityName, set[ActivityName]] = {activity.name: set() for activity in network.activities}
    for activity in network.activities:
        for dependency_name in activity.dependencies:
            successors[dependency_name].add(activity.name)

    # Process activities in reverse topological order
    def calculate_latest(activity_name: ActivityName) -> None:
        """Recursively calculate latest times."""
        if activity_name in latest_finishes:
            return

        activity = activity_map[activity_name]

        # Calculate latest finish based on successors
        if not successors[activity_name]:
            # No successors - must finish by project end
            latest_finishes[activity_name] = forward_result.project_end
        else:
            # Must finish before any successor starts
            for successor_name in successors[activity_name]:
                calculate_latest(successor_name)

            min_start = min(latest_starts[successor_name] for successor_name in successors[activity_name])
            latest_finishes[activity_name] = min_start

        # Latest start = latest finish - duration
        latest_starts[activity_name] = latest_finishes[activity_name] - activity.duration

    # Calculate for all activities
    for activity in network.activities:
        calculate_latest(activity.name)

    return BackwardPassResult(
        latest_starts=latest_starts,
        latest_finishes=latest_finishes,
    )
