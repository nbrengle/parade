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

    earliest_start: dict[ActivityName, Duration]
    earliest_finish: dict[ActivityName, Duration]
    project_end: Duration


@dataclass(frozen=True)
class BackwardPassResult:
    """Result of the backward pass calculation.

    Contains latest start/finish times for all activities.
    """

    latest_start: dict[ActivityName, Duration]
    latest_finish: dict[ActivityName, Duration]


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
            earliest_start=forward_result.earliest_start[activity.name],
            earliest_finish=forward_result.earliest_finish[activity.name],
            latest_start=backward_result.latest_start[activity.name],
            latest_finish=backward_result.latest_finish[activity.name],
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
    earliest_start: dict[ActivityName, Duration] = {}
    earliest_finish: dict[ActivityName, Duration] = {}

    # Process activities in topological order
    def calculate_earliest(activity_id: ActivityName) -> None:
        """Recursively calculate earliest times."""
        if activity_id in earliest_start:
            return

        activity = activity_map[activity_id]

        # Calculate earliest start based on dependencies
        if not activity.dependencies:
            # No dependencies - can start at time 0
            earliest_start[activity_id] = Duration(Decimal(0))
        else:
            # Must wait for all dependencies to finish
            for dep_id in activity.dependencies:
                calculate_earliest(dep_id)

            max_finish = max(earliest_finish[dep_id] for dep_id in activity.dependencies)
            earliest_start[activity_id] = max_finish

        # Earliest finish = earliest start + duration
        earliest_finish[activity_id] = earliest_start[activity_id] + activity.duration

    # Calculate for all activities
    for activity in network.activities:
        calculate_earliest(activity.name)

    # Find project completion time
    project_end = max(earliest_finish.values())

    return ForwardPassResult(
        earliest_start=earliest_start,
        earliest_finish=earliest_finish,
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
        activity_map: Lookup dictionary for activities by ID.
        forward_result: Results from the forward pass.

    Returns:
        BackwardPassResult containing latest start/finish times.
    """
    latest_start: dict[ActivityName, Duration] = {}
    latest_finish: dict[ActivityName, Duration] = {}

    # Build reverse dependency map (successors)
    successors: dict[ActivityName, set[ActivityName]] = {activity.name: set() for activity in network.activities}
    for activity in network.activities:
        for dep_id in activity.dependencies:
            successors[dep_id].add(activity.name)

    # Process activities in reverse topological order
    def calculate_latest(activity_id: ActivityName) -> None:
        """Recursively calculate latest times."""
        if activity_id in latest_finish:
            return

        activity = activity_map[activity_id]

        # Calculate latest finish based on successors
        if not successors[activity_id]:
            # No successors - must finish by project end
            latest_finish[activity_id] = forward_result.project_end
        else:
            # Must finish before any successor starts
            for succ_id in successors[activity_id]:
                calculate_latest(succ_id)

            min_start = min(latest_start[succ_id] for succ_id in successors[activity_id])
            latest_finish[activity_id] = min_start

        # Latest start = latest finish - duration
        latest_start[activity_id] = latest_finish[activity_id] - activity.duration

    # Calculate for all activities
    for activity in network.activities:
        calculate_latest(activity.name)

    return BackwardPassResult(
        latest_start=latest_start,
        latest_finish=latest_finish,
    )
