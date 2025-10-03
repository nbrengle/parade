"""Simple tests for scheduling to debug issues."""

from decimal import Decimal

from parade.domain.activity import ActivityName, Duration, UnscheduledActivity
from parade.domain.project_network import UnscheduledProjectNetwork
from parade.domain.scheduling import schedule


def test_single_activity() -> None:
    """Test scheduling a single activity with no dependencies."""
    activity = UnscheduledActivity(
        name=ActivityName("A"),
        duration=Duration(Decimal("5.0")),
        depends_on=frozenset(),
    )
    network = UnscheduledProjectNetwork(activities=frozenset([activity]))

    result = schedule(network)

    assert len(result.activities) == 1
    scheduled = next(iter(result.activities))
    assert scheduled.name == "A"
    assert scheduled.earliest_start == Duration(Decimal(0))
    assert scheduled.earliest_finish == Duration(Decimal("5.0"))
    assert scheduled.is_critical
