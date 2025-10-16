"""Integration tests for the complete format and export flow."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from parade.application.export import Exporter, export_to
from parade.application.format import ProjectFormatter, format_as
from parade.domain.activity import ActivityName, Duration, ScheduledActivity
from parade.domain.project_network import ScheduledProjectNetwork


@pytest.fixture
def complex_scheduled_network() -> ScheduledProjectNetwork:
    """Create a more complex scheduled network for integration testing."""
    activities = [
        ScheduledActivity(
            name=ActivityName("Start"),
            duration=Duration(Decimal(0)),
            earliest_start=Duration(Decimal(0)),
            earliest_finish=Duration(Decimal(0)),
            latest_start=Duration(Decimal(0)),
            latest_finish=Duration(Decimal(0)),
        ),
        ScheduledActivity(
            name=ActivityName("A"),
            duration=Duration(Decimal(5)),
            depends_on=frozenset([ActivityName("Start")]),
            earliest_start=Duration(Decimal(0)),
            earliest_finish=Duration(Decimal(5)),
            latest_start=Duration(Decimal(0)),
            latest_finish=Duration(Decimal(5)),
        ),
        ScheduledActivity(
            name=ActivityName("B"),
            duration=Duration(Decimal(3)),
            depends_on=frozenset([ActivityName("Start")]),
            earliest_start=Duration(Decimal(0)),
            earliest_finish=Duration(Decimal(3)),
            latest_start=Duration(Decimal(2)),
            latest_finish=Duration(Decimal(5)),
        ),
        ScheduledActivity(
            name=ActivityName("C"),
            duration=Duration(Decimal(4)),
            depends_on=frozenset([ActivityName("A"), ActivityName("B")]),
            earliest_start=Duration(Decimal(5)),
            earliest_finish=Duration(Decimal(9)),
            latest_start=Duration(Decimal(5)),
            latest_finish=Duration(Decimal(9)),
        ),
    ]
    return ScheduledProjectNetwork(activities)


class TestFormatAndExportIntegration:
    """Integration tests for the complete flow."""

    def test_format_json_and_export_to_file(
        self,
        complex_scheduled_network: ScheduledProjectNetwork,
        tmp_path: Path,
        json_formatter: ProjectFormatter,
        file_exporter: Exporter,
    ) -> None:
        """Test the complete flow: format as JSON and export to file."""
        # Format the network
        json_content = format_as(json_formatter, complex_scheduled_network)

        # Export to file
        output_path = tmp_path / "project.json"
        result_path = export_to(
            file_exporter,
            json_content,
            output_path,
        )

        # Verify the file exists and contains valid JSON
        assert output_path.exists()
        assert result_path == str(output_path.absolute())

        # Read and parse the JSON
        with output_path.open(encoding="utf-8") as f:
            data = json.load(f)

        # Verify the structure
        assert data["project_duration"] == "9"
        assert isinstance(data["project_duration"], str)
        assert len(data["activities"]) == 4

        # Verify critical path activities (A and C)
        activity_a = next(a for a in data["activities"] if a["name"] == "A")
        assert activity_a["is_critical"] is True
        assert activity_a["total_float"] == "0"
        assert isinstance(activity_a["total_float"], str)

        activity_c = next(a for a in data["activities"] if a["name"] == "C")
        assert activity_c["is_critical"] is True
        assert activity_c["total_float"] == "0"
        assert isinstance(activity_c["total_float"], str)

        # Verify non-critical activity (B has float)
        activity_b = next(a for a in data["activities"] if a["name"] == "B")
        assert activity_b["is_critical"] is False
        assert activity_b["total_float"] == "2"
        assert isinstance(activity_b["total_float"], str)

    def test_verb_composition(
        self,
        complex_scheduled_network: ScheduledProjectNetwork,
        tmp_path: Path,
        json_formatter: ProjectFormatter,
        file_exporter: Exporter,
    ) -> None:
        """Test composing the verbs in a natural workflow."""
        # This is the verb-oriented API in action:
        # 1. Format the network
        formatted = format_as(json_formatter, complex_scheduled_network)

        # 2. Export the formatted content
        output_file = tmp_path / "project.json"
        result = export_to(file_exporter, formatted, output_file)

        # Verify
        assert output_file.exists()
        assert result == str(output_file.absolute())

        # Verify content
        data = json.loads(output_file.read_text(encoding="utf-8"))
        assert data["project_duration"] == "9"
        assert isinstance(data["project_duration"], str)
        assert len(data["activities"]) == 4
