"""Tests for formatting application services."""

import json
from decimal import Decimal

import pytest

from parade.application.format import ProjectFormatter, format_as
from parade.domain.activity import ActivityName, Duration, ScheduledActivity
from parade.domain.project_network import ScheduledProjectNetwork


@pytest.fixture
def simple_scheduled_network() -> ScheduledProjectNetwork:
    """Create a simple scheduled network for testing."""
    activities = [
        ScheduledActivity(
            name=ActivityName("A"),
            duration=Duration(Decimal(5)),
            earliest_start=Duration(Decimal(0)),
            earliest_finish=Duration(Decimal(5)),
            latest_start=Duration(Decimal(0)),
            latest_finish=Duration(Decimal(5)),
        ),
        ScheduledActivity(
            name=ActivityName("B"),
            duration=Duration(Decimal(3)),
            depends_on=frozenset([ActivityName("A")]),
            earliest_start=Duration(Decimal(5)),
            earliest_finish=Duration(Decimal(8)),
            latest_start=Duration(Decimal(5)),
            latest_finish=Duration(Decimal(8)),
        ),
    ]
    return ScheduledProjectNetwork(activities)


class TestFormatAsJson:
    """Tests for formatting as JSON."""

    def test_format_as_json(
        self,
        simple_scheduled_network: ScheduledProjectNetwork,
        json_formatter: ProjectFormatter,
    ) -> None:
        """Test formatting a network as JSON."""
        result = format_as(json_formatter, simple_scheduled_network)

        # Verify it's valid JSON
        data = json.loads(result)

        # Verify structure
        assert "project_duration" in data
        assert "activities" in data
        assert data["project_duration"] == "8"
        assert len(data["activities"]) == 2

        # Verify activity A
        activity_a = next(a for a in data["activities"] if a["name"] == "A")
        assert activity_a["duration"] == "5"
        assert activity_a["dependencies"] == []
        assert activity_a["earliest_start"] == "0"
        assert activity_a["earliest_finish"] == "5"
        assert activity_a["is_critical"] is True

        # Verify activity B
        activity_b = next(a for a in data["activities"] if a["name"] == "B")
        assert activity_b["duration"] == "3"
        assert activity_b["dependencies"] == ["A"]
        assert activity_b["earliest_start"] == "5"
        assert activity_b["earliest_finish"] == "8"
        assert activity_b["is_critical"] is True
