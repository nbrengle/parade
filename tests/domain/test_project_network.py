"""Tests for project network validation and queries."""

from decimal import Decimal

import pytest

from parade.domain.activity import ActivityName, Duration, ScheduledActivity, UnscheduledActivity
from parade.domain.project_network import UnscheduledProjectNetwork
from parade.domain.scheduling import schedule


class TestUnscheduledProjectNetwork:
    """Tests for UnscheduledProjectNetwork validation."""

    def test_empty_network_raises_error(self) -> None:
        """Test that empty network raises ValueError."""
        activities: frozenset[UnscheduledActivity] = frozenset()
        with pytest.raises(ValueError, match="must contain at least one activity"):
            UnscheduledProjectNetwork(activities=activities)

    def test_valid_network(self) -> None:
        """Test creating a valid project network."""
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal("1.0")),
                    depends_on=frozenset(),
                ),
                UnscheduledActivity(
                    name=ActivityName("B"),
                    duration=Duration(Decimal("2.0")),
                    depends_on=frozenset(["A"]),
                ),
            ],
        )
        network = UnscheduledProjectNetwork(activities=activities)
        assert len(network.activities) == 2

    def test_duplicate_activity_ids_raises_error(self) -> None:
        """Test that duplicate activity IDs raise ValueError."""
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal("1.0")),
                    depends_on=frozenset(),
                ),
                UnscheduledActivity(
                    name=ActivityName("A"),  # Duplicate!
                    duration=Duration(Decimal("2.0")),
                    depends_on=frozenset(),
                ),
            ],
        )
        with pytest.raises(ValueError, match="Activity names must be unique"):
            UnscheduledProjectNetwork(activities=activities)

    def test_missing_dependency_raises_error(self) -> None:
        """Test that referencing non-existent activity raises ValueError."""
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal("1.0")),
                    depends_on=frozenset(["B"]),  # B doesn't exist!
                ),
            ],
        )
        with pytest.raises(ValueError, match="depends on non-existent activity"):
            UnscheduledProjectNetwork(activities=activities)

    def test_circular_dependency_raises_error(self) -> None:
        """Test that circular dependencies raise ValueError."""
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal("1.0")),
                    depends_on=frozenset(["B"]),
                ),
                UnscheduledActivity(
                    name=ActivityName("B"),
                    duration=Duration(Decimal("2.0")),
                    depends_on=frozenset(["A"]),  # Cycle!
                ),
            ],
        )
        with pytest.raises(ValueError, match="circular dependencies"):
            UnscheduledProjectNetwork(activities=activities)

    def test_self_referential_dependency_raises_error(self) -> None:
        """Test that self-referential dependency raises ValueError."""
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal("1.0")),
                    depends_on=frozenset(["A"]),  # Self-cycle!
                ),
            ],
        )
        with pytest.raises(ValueError, match="circular dependencies"):
            UnscheduledProjectNetwork(activities=activities)

    def test_complex_cycle_raises_error(self) -> None:
        """Test that complex multi-node cycles are detected."""
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal("1.0")),
                    depends_on=frozenset(["B"]),
                ),
                UnscheduledActivity(
                    name=ActivityName("B"),
                    duration=Duration(Decimal("2.0")),
                    depends_on=frozenset(["C"]),
                ),
                UnscheduledActivity(
                    name=ActivityName("C"),
                    duration=Duration(Decimal("3.0")),
                    depends_on=frozenset(["A"]),  # Cycle: A->B->C->A
                ),
            ],
        )
        with pytest.raises(ValueError, match="circular dependencies"):
            UnscheduledProjectNetwork(activities=activities)


class TestScheduledProjectNetwork:
    """Tests for ScheduledProjectNetwork queries."""

    def test_project_duration_query(self) -> None:
        """Test that project_duration returns the total project duration."""
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal("5.0")),
                    depends_on=frozenset(),
                ),
                UnscheduledActivity(
                    name=ActivityName("B"),
                    duration=Duration(Decimal("3.0")),
                    depends_on=frozenset(["A"]),
                ),
            ],
        )
        network = UnscheduledProjectNetwork(activities=activities)
        result = schedule(network)

        # Project duration should be 8 (A=5 + B=3)
        assert result.project_duration == Duration(Decimal("8.0"))


class TestActivityDependencyChecking:
    """Tests for has_dependency method."""

    def test_unscheduled_activity_has_dependency(self) -> None:
        """Test has_dependency on UnscheduledActivity."""
        activity = UnscheduledActivity(
            name=ActivityName("A"),
            duration=Duration(Decimal("1.0")),
            depends_on=frozenset([ActivityName("B"), ActivityName("C")]),
        )
        assert activity.has_dependency(ActivityName("B"))
        assert activity.has_dependency(ActivityName("C"))
        assert not activity.has_dependency(ActivityName("D"))

    def test_unscheduled_activity_no_dependencies(self) -> None:
        """Test has_dependency when activity has no dependencies."""
        activity = UnscheduledActivity(
            name=ActivityName("A"),
            duration=Duration(Decimal("1.0")),
            depends_on=frozenset(),
        )
        assert not activity.has_dependency(ActivityName("B"))

    def test_scheduled_activity_has_dependency(self) -> None:
        """Test has_dependency on ScheduledActivity."""
        activity = ScheduledActivity(
            name=ActivityName("A"),
            duration=Duration(Decimal("1.0")),
            depends_on=frozenset([ActivityName("B"), ActivityName("C")]),
            earliest_start=Duration(Decimal(0)),
            earliest_finish=Duration(Decimal("1.0")),
            latest_start=Duration(Decimal("2.0")),
            latest_finish=Duration(Decimal("3.0")),
        )
        assert activity.has_dependency(ActivityName("B"))
        assert activity.has_dependency(ActivityName("C"))
        assert not activity.has_dependency(ActivityName("D"))
