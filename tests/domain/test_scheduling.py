"""Property-based tests for scheduling domain service."""

from hypothesis import given
from hypothesis import strategies as st

from parade.domain.activity import ActivityName, UnscheduledActivity
from parade.domain.project_network import UnscheduledProjectNetwork
from parade.domain.scheduling import schedule
from tests.strategies import durations


@st.composite
def acyclic_project_networks(draw: st.DrawFn) -> UnscheduledProjectNetwork:
    """Generate a valid acyclic project network.

    Generates networks with guaranteed acyclic dependencies by only allowing
    dependencies on earlier activities in the list.
    """
    num_activities = draw(st.integers(min_value=1, max_value=20))

    # Generate simple sequential activity IDs
    activity_ids_list = [ActivityName(f"activity_{i}") for i in range(num_activities)]

    # Generate activities with dependencies only on earlier activities (ensures acyclic)
    activities = []
    for i, activity_id in enumerate(activity_ids_list):
        duration = draw(durations())

        # Can only depend on activities that come before in the list
        possible_deps = activity_ids_list[:i]
        if possible_deps:
            # Let hypothesis pick any subset of previous activities
            deps = draw(st.sets(st.sampled_from(possible_deps)))
            dependencies = frozenset(deps)
        else:
            dependencies = frozenset()

        activities.append(
            UnscheduledActivity(
                name=activity_id,
                duration=duration,
                depends_on=dependencies,
            ),
        )

    return UnscheduledProjectNetwork(activities=frozenset(activities))


class TestSchedulingProperties:
    """Property-based tests for the CPM scheduling algorithm."""

    @given(acyclic_project_networks())
    def test_dependency_ordering(self, network: UnscheduledProjectNetwork) -> None:
        """For any activity A depending on B, earliest_start(A) >= earliest_finish(B)."""
        result = schedule(network)

        scheduled_by_id = {activity.name: activity for activity in result.activities}

        for activity in result.activities:
            for dep_id in activity.dependencies:
                dep = scheduled_by_id[dep_id]
                assert activity.earliest_start >= dep.earliest_finish, (
                    f"Activity {activity.name.value} starts at {activity.earliest_start} "
                    f"but depends on {dep_id.value} which finishes at {dep.earliest_finish}"
                )

    @given(acyclic_project_networks())
    def test_duration_consistency_earliest(self, network: UnscheduledProjectNetwork) -> None:
        """For all activities: earliest_finish = earliest_start + duration."""
        result = schedule(network)

        for activity in result.activities:
            expected_finish = activity.earliest_start + activity.duration
            assert activity.earliest_finish == expected_finish, (
                f"Activity {activity.name.value}: earliest_finish {activity.earliest_finish} "
                f"!= earliest_start {activity.earliest_start} + duration {activity.duration}"
            )

    @given(acyclic_project_networks())
    def test_duration_consistency_latest(self, network: UnscheduledProjectNetwork) -> None:
        """For all activities: latest_finish = latest_start + duration."""
        result = schedule(network)

        for activity in result.activities:
            expected_finish = activity.latest_start + activity.duration
            assert activity.latest_finish == expected_finish, (
                f"Activity {activity.name.value}: latest_finish {activity.latest_finish} "
                f"!= latest_start {activity.latest_start} + duration {activity.duration}"
            )

    @given(acyclic_project_networks())
    def test_float_calculation(self, network: UnscheduledProjectNetwork) -> None:
        """Total float should equal latest_start - earliest_start."""
        result = schedule(network)

        for activity in result.activities:
            expected_float = activity.latest_start - activity.earliest_start
            assert activity.total_float.value == expected_float.value, (
                f"Activity {activity.name.value}: total_float {activity.total_float} "
                f"!= latest_start {activity.latest_start} - earliest_start {activity.earliest_start}"
            )

    @given(acyclic_project_networks())
    def test_non_negative_float(self, network: UnscheduledProjectNetwork) -> None:
        """All activities should have non-negative total float."""
        result = schedule(network)

        for activity in result.activities:
            assert activity.total_float.value >= 0, (
                f"Activity {activity.name.value} has negative total_float: {activity.total_float}"
            )

    @given(acyclic_project_networks())
    def test_timing_order(self, network: UnscheduledProjectNetwork) -> None:
        """Earliest times should be <= latest times."""
        result = schedule(network)

        for activity in result.activities:
            assert activity.earliest_start <= activity.latest_start, (
                f"Activity {activity.name.value}: earliest_start {activity.earliest_start} "
                f"> latest_start {activity.latest_start}"
            )
            assert activity.earliest_finish <= activity.latest_finish, (
                f"Activity {activity.name.value}: earliest_finish {activity.earliest_finish} "
                f"> latest_finish {activity.latest_finish}"
            )

    @given(acyclic_project_networks())
    def test_critical_path_exists(self, network: UnscheduledProjectNetwork) -> None:
        """At least one activity should have zero float (be on critical path)."""
        result = schedule(network)

        critical_activities = [a for a in result.activities if a.is_critical]
        assert len(critical_activities) > 0, "No critical path found"
