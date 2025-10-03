"""Concrete correctness tests for CPM scheduling with hand-calculated expected values."""

from decimal import Decimal

import pytest

from parade.domain.activity import ActivityName, Duration, UnscheduledActivity
from parade.domain.project_network import UnscheduledProjectNetwork
from parade.domain.scheduling import schedule


class TestLinearChain:
    """Test a simple linear chain: A(5) → B(3) → C(2)."""

    def test_linear_chain_correctness(self) -> None:
        """Test linear chain produces correct CPM values.

        Expected:
        - All activities critical (zero float)
        - Project duration = 10
        - A: ES=0, EF=5, LS=0, LF=5
        - B: ES=5, EF=8, LS=5, LF=8
        - C: ES=8, EF=10, LS=8, LF=10
        """
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal(5)),
                    depends_on=frozenset(),
                ),
                UnscheduledActivity(
                    name=ActivityName("B"),
                    duration=Duration(Decimal(3)),
                    depends_on=frozenset(["A"]),
                ),
                UnscheduledActivity(
                    name=ActivityName("C"),
                    duration=Duration(Decimal(2)),
                    depends_on=frozenset(["B"]),
                ),
            ],
        )
        network = UnscheduledProjectNetwork(activities=activities)
        result = schedule(network)

        # Get activities by ID
        activities_by_id = {a.name: a for a in result.activities}
        a = activities_by_id[ActivityName("A")]
        b = activities_by_id[ActivityName("B")]
        c = activities_by_id[ActivityName("C")]

        # Assert A
        assert a.earliest_start == Duration(Decimal(0))
        assert a.earliest_finish == Duration(Decimal(5))
        assert a.latest_start == Duration(Decimal(0))
        assert a.latest_finish == Duration(Decimal(5))
        assert a.total_float.value == Decimal(0)
        assert a.is_critical

        # Assert B
        assert b.earliest_start == Duration(Decimal(5))
        assert b.earliest_finish == Duration(Decimal(8))
        assert b.latest_start == Duration(Decimal(5))
        assert b.latest_finish == Duration(Decimal(8))
        assert b.total_float.value == Decimal(0)
        assert b.is_critical

        # Assert C
        assert c.earliest_start == Duration(Decimal(8))
        assert c.earliest_finish == Duration(Decimal(10))
        assert c.latest_start == Duration(Decimal(8))
        assert c.latest_finish == Duration(Decimal(10))
        assert c.total_float.value == Decimal(0)
        assert c.is_critical

        # Assert project duration
        assert result.project_duration == Duration(Decimal(10))


class TestDiamondUnequalPaths:
    """Test diamond with unequal paths.

         B(5)
        ↗    ↘
      A(2)    D(1)
        ↘    ↗
         C(3)

    Path A→B→D = 8 (critical)
    Path A→C→D = 6 (has float)
    """

    def test_diamond_unequal_paths_correctness(self) -> None:
        """Test diamond with unequal paths produces correct CPM values.

        Expected:
        - Critical path: A→B→D
        - Project duration = 8
        - A: ES=0, EF=2, LS=0, LF=2, float=0, critical
        - B: ES=2, EF=7, LS=2, LF=7, float=0, critical
        - C: ES=2, EF=5, LS=4, LF=7, float=2, NOT critical
        - D: ES=7, EF=8, LS=7, LF=8, float=0, critical
        """
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal(2)),
                    depends_on=frozenset(),
                ),
                UnscheduledActivity(
                    name=ActivityName("B"),
                    duration=Duration(Decimal(5)),
                    depends_on=frozenset(["A"]),
                ),
                UnscheduledActivity(
                    name=ActivityName("C"),
                    duration=Duration(Decimal(3)),
                    depends_on=frozenset(["A"]),
                ),
                UnscheduledActivity(
                    name=ActivityName("D"),
                    duration=Duration(Decimal(1)),
                    depends_on=frozenset(["B", "C"]),
                ),
            ],
        )
        network = UnscheduledProjectNetwork(activities=activities)
        result = schedule(network)

        # Get activities by ID
        activities_by_id = {a.name: a for a in result.activities}
        a = activities_by_id[ActivityName("A")]
        b = activities_by_id[ActivityName("B")]
        c = activities_by_id[ActivityName("C")]
        d = activities_by_id[ActivityName("D")]

        # Assert A (critical)
        assert a.earliest_start == Duration(Decimal(0))
        assert a.earliest_finish == Duration(Decimal(2))
        assert a.latest_start == Duration(Decimal(0))
        assert a.latest_finish == Duration(Decimal(2))
        assert a.total_float.value == Decimal(0)
        assert a.is_critical

        # Assert B (critical)
        assert b.earliest_start == Duration(Decimal(2))
        assert b.earliest_finish == Duration(Decimal(7))
        assert b.latest_start == Duration(Decimal(2))
        assert b.latest_finish == Duration(Decimal(7))
        assert b.total_float.value == Decimal(0)
        assert b.is_critical

        # Assert C (NOT critical - has float)
        assert c.earliest_start == Duration(Decimal(2))
        assert c.earliest_finish == Duration(Decimal(5))
        assert c.latest_start == Duration(Decimal(4))
        assert c.latest_finish == Duration(Decimal(7))
        assert c.total_float.value == Decimal(2)
        assert not c.is_critical

        # Assert D (critical)
        assert d.earliest_start == Duration(Decimal(7))
        assert d.earliest_finish == Duration(Decimal(8))
        assert d.latest_start == Duration(Decimal(7))
        assert d.latest_finish == Duration(Decimal(8))
        assert d.total_float.value == Decimal(0)
        assert d.is_critical

        # Assert project duration
        assert result.project_duration == Duration(Decimal(8))


class TestMultipleCriticalPaths:
    """Test diamond with equal-length paths.

         B(6)
        ↗    ↘
      A(2)    D(1)
        ↘    ↗
         C(6)

    Both paths = 9, so all activities should be critical.
    """

    def test_multiple_critical_paths_correctness(self) -> None:
        """Test that tied-longest paths are all marked critical.

        Expected:
        - Both paths critical: A→B→D = A→C→D = 9
        - Project duration = 9
        - All activities have zero float
        - A: ES=0, EF=2, LS=0, LF=2
        - B: ES=2, EF=8, LS=2, LF=8
        - C: ES=2, EF=8, LS=2, LF=8
        - D: ES=8, EF=9, LS=8, LF=9
        """
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal(2)),
                    depends_on=frozenset(),
                ),
                UnscheduledActivity(
                    name=ActivityName("B"),
                    duration=Duration(Decimal(6)),
                    depends_on=frozenset(["A"]),
                ),
                UnscheduledActivity(
                    name=ActivityName("C"),
                    duration=Duration(Decimal(6)),
                    depends_on=frozenset(["A"]),
                ),
                UnscheduledActivity(
                    name=ActivityName("D"),
                    duration=Duration(Decimal(1)),
                    depends_on=frozenset(["B", "C"]),
                ),
            ],
        )
        network = UnscheduledProjectNetwork(activities=activities)
        result = schedule(network)

        # Get activities by ID
        activities_by_id = {a.name: a for a in result.activities}
        a = activities_by_id[ActivityName("A")]
        b = activities_by_id[ActivityName("B")]
        c = activities_by_id[ActivityName("C")]
        d = activities_by_id[ActivityName("D")]

        # Assert all activities are critical
        assert a.earliest_start == Duration(Decimal(0))
        assert a.earliest_finish == Duration(Decimal(2))
        assert a.latest_start == Duration(Decimal(0))
        assert a.latest_finish == Duration(Decimal(2))
        assert a.total_float.value == Decimal(0)
        assert a.is_critical

        assert b.earliest_start == Duration(Decimal(2))
        assert b.earliest_finish == Duration(Decimal(8))
        assert b.latest_start == Duration(Decimal(2))
        assert b.latest_finish == Duration(Decimal(8))
        assert b.total_float.value == Decimal(0)
        assert b.is_critical

        assert c.earliest_start == Duration(Decimal(2))
        assert c.earliest_finish == Duration(Decimal(8))
        assert c.latest_start == Duration(Decimal(2))
        assert c.latest_finish == Duration(Decimal(8))
        assert c.total_float.value == Decimal(0)
        assert c.is_critical

        assert d.earliest_start == Duration(Decimal(8))
        assert d.earliest_finish == Duration(Decimal(9))
        assert d.latest_start == Duration(Decimal(8))
        assert d.latest_finish == Duration(Decimal(9))
        assert d.total_float.value == Decimal(0)
        assert d.is_critical

        # Assert project duration
        assert result.project_duration == Duration(Decimal(9))


class TestDisconnectedSubgraphs:
    """Test multiple independent chains.

    A(5) → B(3)

    C(2) → D(4)

    Chain A→B = 8 (critical)
    Chain C→D = 6 (has float)
    """

    def test_disconnected_chains_correctness(self) -> None:
        """Test disconnected subgraphs produce correct CPM values.

        Expected:
        - Project duration = 8 (max of both chains)
        - A→B chain is critical
        - C→D chain has float = 2
        - A: ES=0, EF=5, LS=0, LF=5, float=0, critical
        - B: ES=5, EF=8, LS=5, LF=8, float=0, critical
        - C: ES=0, EF=2, LS=2, LF=4, float=2, NOT critical
        - D: ES=2, EF=6, LS=4, LF=8, float=2, NOT critical
        """
        activities = frozenset(
            [
                UnscheduledActivity(
                    name=ActivityName("A"),
                    duration=Duration(Decimal(5)),
                    depends_on=frozenset(),
                ),
                UnscheduledActivity(
                    name=ActivityName("B"),
                    duration=Duration(Decimal(3)),
                    depends_on=frozenset(["A"]),
                ),
                UnscheduledActivity(
                    name=ActivityName("C"),
                    duration=Duration(Decimal(2)),
                    depends_on=frozenset(),
                ),
                UnscheduledActivity(
                    name=ActivityName("D"),
                    duration=Duration(Decimal(4)),
                    depends_on=frozenset(["C"]),
                ),
            ],
        )
        network = UnscheduledProjectNetwork(activities=activities)
        result = schedule(network)

        # Get activities by ID
        activities_by_id = {a.name: a for a in result.activities}
        a = activities_by_id[ActivityName("A")]
        b = activities_by_id[ActivityName("B")]
        c = activities_by_id[ActivityName("C")]
        d = activities_by_id[ActivityName("D")]

        # Assert A (critical)
        assert a.earliest_start == Duration(Decimal(0))
        assert a.earliest_finish == Duration(Decimal(5))
        assert a.latest_start == Duration(Decimal(0))
        assert a.latest_finish == Duration(Decimal(5))
        assert a.total_float.value == Decimal(0)
        assert a.is_critical

        # Assert B (critical)
        assert b.earliest_start == Duration(Decimal(5))
        assert b.earliest_finish == Duration(Decimal(8))
        assert b.latest_start == Duration(Decimal(5))
        assert b.latest_finish == Duration(Decimal(8))
        assert b.total_float.value == Decimal(0)
        assert b.is_critical

        # Assert C (NOT critical)
        assert c.earliest_start == Duration(Decimal(0))
        assert c.earliest_finish == Duration(Decimal(2))
        assert c.latest_start == Duration(Decimal(2))
        assert c.latest_finish == Duration(Decimal(4))
        assert c.total_float.value == Decimal(2)
        assert not c.is_critical

        # Assert D (NOT critical)
        assert d.earliest_start == Duration(Decimal(2))
        assert d.earliest_finish == Duration(Decimal(6))
        assert d.latest_start == Duration(Decimal(4))
        assert d.latest_finish == Duration(Decimal(8))
        assert d.total_float.value == Decimal(2)
        assert not d.is_critical

        # Assert project duration (max of both chains)
        assert result.project_duration == Duration(Decimal(8))


class TestEmptyNetwork:
    """Test edge case of zero activities."""

    def test_empty_network(self) -> None:
        """Test that empty network raises ValueError."""
        activities: frozenset[UnscheduledActivity] = frozenset()
        with pytest.raises(ValueError, match="must contain at least one activity"):
            UnscheduledProjectNetwork(activities=activities)
