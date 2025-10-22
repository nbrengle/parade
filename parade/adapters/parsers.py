"""Parsers for converting various input formats to domain objects."""

import csv
import logging
from decimal import Decimal, InvalidOperation
from io import StringIO

from parade.application.parse import ParseError, ProjectParser, ValidationError
from parade.domain.activity import ActivityName, Duration, UnscheduledActivity
from parade.domain.project_network import UnscheduledProjectNetwork

__all__ = ["CSVParser"]

logger = logging.getLogger(__name__)


class CSVParser(ProjectParser):
    """Parser that converts CSV data to project networks."""

    def parse(self, content: str) -> UnscheduledProjectNetwork:
        """Parse CSV content into an unscheduled project network.

        Expected CSV format:
            activity_name,duration,depends_on
            A,5,
            B,3,A
            C,4,"A,B"

        Args:
            content: CSV string to parse.

        Returns:
            An unscheduled project network.

        Raises:
            ParseError: If the CSV cannot be parsed.
            ValidationError: If the data fails validation.
        """
        logger.debug("Starting CSV parsing")

        reader = self._create_csv_reader(content)
        self._validate_headers(reader)
        activities = self._parse_all_activities(reader)

        logger.info("Successfully parsed %d activities from CSV", len(activities))

        return self._create_network(activities)

    def _create_csv_reader(self, content: str) -> csv.DictReader[str]:
        """Create and return a CSV reader from content.

        Args:
            content: CSV string to parse.

        Returns:
            CSV DictReader instance.

        Raises:
            ParseError: If CSV format is invalid.
        """
        try:
            return csv.DictReader(StringIO(content))
        except csv.Error as e:
            msg = f"Invalid CSV format: {e}"
            raise ParseError(msg) from e

    def _validate_headers(self, reader: csv.DictReader[str]) -> None:
        """Validate that CSV has correct headers.

        Args:
            reader: CSV reader to validate.

        Raises:
            ParseError: If headers are missing or incorrect.
        """
        if reader.fieldnames is None:
            msg = "CSV file is empty or has no headers"
            raise ParseError(msg)

        expected_headers = {"activity_name", "duration", "depends_on"}
        actual_headers = set(reader.fieldnames)

        if actual_headers != expected_headers:
            missing = expected_headers - actual_headers
            extra = actual_headers - expected_headers
            msg_parts = []
            if missing:
                msg_parts.append(f"missing: {', '.join(missing)}")
            if extra:
                msg_parts.append(f"extra: {', '.join(extra)}")
            msg = f"Invalid CSV headers ({'; '.join(msg_parts)})"
            raise ParseError(msg)

    def _parse_all_activities(self, reader: csv.DictReader[str]) -> list[UnscheduledActivity]:
        """Parse all activities from CSV reader.

        Args:
            reader: CSV reader to parse.

        Returns:
            List of unscheduled activities.

        Raises:
            ParseError: If parsing fails.
            ValidationError: If no activities found.
        """
        activities: list[UnscheduledActivity] = []
        line_num = 2  # Account for header line

        for row in reader:
            try:
                activity = self._parse_activity(row)
                activities.append(activity)
            except (ParseError, ValidationError):
                raise
            except Exception as e:
                msg = f"Unexpected error: {e}"
                raise ParseError(msg, line_num) from e

            line_num += 1

        if not activities:
            msg = "No activities found in CSV"
            raise ValidationError(msg)

        return activities

    def _create_network(self, activities: list[UnscheduledActivity]) -> UnscheduledProjectNetwork:
        """Create an unscheduled project network from activities.

        Args:
            activities: List of activities.

        Returns:
            An unscheduled project network.

        Raises:
            ValidationError: If network creation fails validation.
        """
        try:
            return UnscheduledProjectNetwork(activities)
        except ValueError as e:
            # Domain-level validation errors
            raise ValidationError(str(e)) from e

    def _parse_activity(self, row: dict[str, str]) -> UnscheduledActivity:
        """Parse a single CSV row into an UnscheduledActivity.

        Args:
            row: Dictionary of CSV row data.

        Returns:
            An unscheduled activity.

        Raises:
            ParseError: If the row cannot be parsed.
            ValidationError: If the data fails validation.
        """
        name = self._parse_name(row)
        duration = self._parse_duration(row)
        depends_on = self._parse_dependencies(row)

        return UnscheduledActivity(
            name=name,
            duration=duration,
            depends_on=depends_on,
        )

    def _parse_name(self, row: dict[str, str]) -> ActivityName:
        """Parse activity name from row.

        Args:
            row: CSV row data.

        Returns:
            Activity name.

        Raises:
            ValidationError: If name is invalid.
        """
        name_str = row["activity_name"].strip()
        if not name_str:
            msg = "Activity name cannot be empty"
            raise ValidationError(msg, "activity_name")

        try:
            return ActivityName(name_str)
        except ValueError as e:
            raise ValidationError(str(e), "activity_name") from e

    def _parse_duration(self, row: dict[str, str]) -> Duration:
        """Parse duration from row.

        Args:
            row: CSV row data.

        Returns:
            Duration.

        Raises:
            ValidationError: If duration is invalid.
        """
        duration_str = row["duration"].strip()
        if not duration_str:
            msg = "Duration cannot be empty"
            raise ValidationError(msg, "duration")

        try:
            duration_decimal = Decimal(duration_str)
        except InvalidOperation as e:
            msg = f"Invalid duration '{duration_str}': must be a number"
            raise ValidationError(msg, "duration") from e

        try:
            return Duration(duration_decimal)
        except ValueError as e:
            raise ValidationError(str(e), "duration") from e

    def _parse_dependencies(self, row: dict[str, str]) -> frozenset[ActivityName]:
        """Parse dependencies from row.

        Args:
            row: CSV row data.

        Returns:
            Frozenset of activity names.

        Raises:
            ValidationError: If dependencies are invalid.
        """
        depends_on_str = row["depends_on"].strip()
        if not depends_on_str:
            return frozenset()

        # Split on comma and clean up each dependency
        dep_names = [d.strip() for d in depends_on_str.split(",") if d.strip()]
        try:
            return frozenset(ActivityName(dep) for dep in dep_names)
        except ValueError as e:
            raise ValidationError(str(e), "depends_on") from e
