"""Concrete correctness tests for CPM scheduling with hand-calculated expected values."""

from decimal import Decimal

from parade.domain.activity import ActivityName, DecimalConvertible, Duration, ScheduledActivity, UnscheduledActivity
from parade.domain.project_network import UnscheduledProjectNetwork
from parade.domain.scheduling import schedule


def assert_times(
    activity: ScheduledActivity,
    *,
    early: tuple[DecimalConvertible, DecimalConvertible],
    late: tuple[DecimalConvertible, DecimalConvertible],
    float_val: DecimalConvertible = 0,
    critical: bool = True,
) -> None:
    """Assert CPM timing values for an activity."""
    es, ef = early
    ls, lf = late
    assert activity.earliest_start == Duration(Decimal(es))
    assert activity.earliest_finish == Duration(Decimal(ef))
    assert activity.latest_start == Duration(Decimal(ls))
    assert activity.latest_finish == Duration(Decimal(lf))
    assert activity.total_float.value == Decimal(float_val)
    assert activity.is_critical == critical


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

        # Get activities by name
        activities_by_name = {a.name: a for a in result.activities}
        a = activities_by_name[ActivityName("A")]
        b = activities_by_name[ActivityName("B")]
        c = activities_by_name[ActivityName("C")]

        assert_times(a, early=(0, 5), late=(0, 5))
        assert_times(b, early=(5, 8), late=(5, 8))
        assert_times(c, early=(8, 10), late=(8, 10))
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

        # Get activities by name
        activities_by_name = {a.name: a for a in result.activities}
        a = activities_by_name[ActivityName("A")]
        b = activities_by_name[ActivityName("B")]
        c = activities_by_name[ActivityName("C")]
        d = activities_by_name[ActivityName("D")]

        assert_times(a, early=(0, 2), late=(0, 2))
        assert_times(b, early=(2, 7), late=(2, 7))
        assert_times(c, early=(2, 5), late=(4, 7), float_val=2, critical=False)
        assert_times(d, early=(7, 8), late=(7, 8))
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

        # Get activities by name
        activities_by_name = {a.name: a for a in result.activities}
        a = activities_by_name[ActivityName("A")]
        b = activities_by_name[ActivityName("B")]
        c = activities_by_name[ActivityName("C")]
        d = activities_by_name[ActivityName("D")]

        assert_times(a, early=(0, 2), late=(0, 2))
        assert_times(b, early=(2, 8), late=(2, 8))
        assert_times(c, early=(2, 8), late=(2, 8))
        assert_times(d, early=(8, 9), late=(8, 9))
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

        # Get activities by name
        activities_by_name = {a.name: a for a in result.activities}
        a = activities_by_name[ActivityName("A")]
        b = activities_by_name[ActivityName("B")]
        c = activities_by_name[ActivityName("C")]
        d = activities_by_name[ActivityName("D")]

        assert_times(a, early=(0, 5), late=(0, 5))
        assert_times(b, early=(5, 8), late=(5, 8))
        assert_times(c, early=(0, 2), late=(2, 4), float_val=2, critical=False)
        assert_times(d, early=(2, 6), late=(4, 8), float_val=2, critical=False)
        assert result.project_duration == Duration(Decimal(8))
