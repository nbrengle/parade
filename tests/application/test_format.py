"""Tests for formatting application services."""

import json
from decimal import Decimal

import pytest

from parade.adapters.formatters import JSONFormatter
from parade.application.format import OutputFormat, ProjectFormatter, format_as_using
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


@pytest.fixture
def test_formatter_registry() -> dict[OutputFormat, ProjectFormatter]:
    """Create a test-local formatter registry."""
    registry: dict[OutputFormat, ProjectFormatter] = {}
    registry[OutputFormat.JSON] = JSONFormatter()
    return registry


class TestFormatterRegistry:
    """Tests for the formatter registry."""

    def test_json_formatter_is_registered(
        self,
        test_formatter_registry: dict[OutputFormat, ProjectFormatter],
    ) -> None:
        """Test that JSONFormatter is registered in the test registry."""
        assert OutputFormat.JSON in test_formatter_registry
        assert isinstance(test_formatter_registry[OutputFormat.JSON], JSONFormatter)


class TestFormatAs:
    """Tests for format_as verb."""

    def test_format_as_json(
        self,
        simple_scheduled_network: ScheduledProjectNetwork,
        test_formatter_registry: dict[OutputFormat, ProjectFormatter],
    ) -> None:
        """Test formatting a network as JSON."""
        result = format_as_using(test_formatter_registry, OutputFormat.JSON, simple_scheduled_network)

        # Verify it's valid JSON
        data = json.loads(result)

        # Verify structure
        assert "project_duration" in data
        assert "activities" in data
        assert data["project_duration"] == "8"
        assert isinstance(data["project_duration"], str)
        assert len(data["activities"]) == 2

        # Verify activity A
        activity_a = next(a for a in data["activities"] if a["name"] == "A")
        assert activity_a["duration"] == "5"
        assert isinstance(activity_a["duration"], str)
        assert activity_a["dependencies"] == []
        assert activity_a["earliest_start"] == "0"
        assert isinstance(activity_a["earliest_start"], str)
        assert activity_a["earliest_finish"] == "5"
        assert isinstance(activity_a["earliest_finish"], str)
        assert activity_a["is_critical"] is True

        # Verify activity B
        activity_b = next(a for a in data["activities"] if a["name"] == "B")
        assert activity_b["duration"] == "3"
        assert isinstance(activity_b["duration"], str)
        assert activity_b["dependencies"] == ["A"]
        assert activity_b["earliest_start"] == "5"
        assert isinstance(activity_b["earliest_start"], str)
        assert activity_b["earliest_finish"] == "8"
        assert isinstance(activity_b["earliest_finish"], str)
        assert activity_b["is_critical"] is True

    def test_format_as_unknown_format_raises_error(
        self,
        simple_scheduled_network: ScheduledProjectNetwork,
    ) -> None:
        """Test that formatting with an unregistered format raises KeyError."""
        # Create an empty registry to test error handling
        empty_registry: dict[OutputFormat, ProjectFormatter] = {}

        with pytest.raises(KeyError):
            format_as_using(empty_registry, OutputFormat.JSON, simple_scheduled_network)
