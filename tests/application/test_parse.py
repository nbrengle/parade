"""Tests for parsing application services."""

import pytest

from parade.adapters.parsers import CSVParser
from parade.application.parse import ParseError, ProjectParser, ValidationError, parse_from


@pytest.fixture
def csv_parser() -> ProjectParser:
    """Create a CSV parser instance."""
    return CSVParser()


class TestCSVParser:
    """Tests for CSVParser."""

    def test_parse_simple_csv(self, csv_parser: ProjectParser) -> None:
        """Test parsing a simple valid CSV."""
        csv_content = """activity_name,duration,depends_on
A,5,
B,3,A
C,4,"A,B"
"""
        network = parse_from(csv_parser, csv_content)

        assert len(network.activities) == 3

        # Check activity A
        activity_a = next(a for a in network.activities if a.name.value == "A")
        assert activity_a.duration.value == 5
        assert len(activity_a.dependencies) == 0

        # Check activity B
        activity_b = next(a for a in network.activities if a.name.value == "B")
        assert activity_b.duration.value == 3
        assert len(activity_b.dependencies) == 1
        assert any(dep.value == "A" for dep in activity_b.dependencies)

        # Check activity C
        activity_c = next(a for a in network.activities if a.name.value == "C")
        assert activity_c.duration.value == 4
        assert len(activity_c.dependencies) == 2
        dep_values = {dep.value for dep in activity_c.dependencies}
        assert dep_values == {"A", "B"}

    def test_parse_csv_with_decimal_durations(self, csv_parser: ProjectParser) -> None:
        """Test parsing CSV with decimal durations."""
        csv_content = """activity_name,duration,depends_on
A,5.5,
B,3.25,A
"""
        network = parse_from(csv_parser, csv_content)

        activity_a = next(a for a in network.activities if a.name.value == "A")
        assert activity_a.duration.value == 5.5

        activity_b = next(a for a in network.activities if a.name.value == "B")
        assert activity_b.duration.value == 3.25

    def test_parse_csv_empty_file(self, csv_parser: ProjectParser) -> None:
        """Test that empty CSV raises ParseError."""
        with pytest.raises(ParseError, match="CSV file is empty"):
            csv_parser.parse("")

    def test_parse_csv_no_activities(self, csv_parser: ProjectParser) -> None:
        """Test that CSV with only headers raises ValidationError."""
        csv_content = """activity_name,duration,depends_on
"""
        with pytest.raises(ValidationError, match="No activities found"):
            csv_parser.parse(csv_content)

    def test_parse_csv_missing_headers(self, csv_parser: ProjectParser) -> None:
        """Test that CSV with missing headers raises ParseError."""
        csv_content = """activity_name,duration
A,5
"""
        with pytest.raises(ParseError, match="missing: depends_on"):
            csv_parser.parse(csv_content)

    def test_parse_csv_extra_headers(self, csv_parser: ProjectParser) -> None:
        """Test that CSV with extra headers raises ParseError."""
        csv_content = """activity_name,duration,depends_on,extra_column
A,5,,something
"""
        with pytest.raises(ParseError, match="extra: extra_column"):
            csv_parser.parse(csv_content)

    def test_parse_csv_empty_activity_name(self, csv_parser: ProjectParser) -> None:
        """Test that empty activity name raises ValidationError."""
        csv_content = """activity_name,duration,depends_on
,5,
"""
        with pytest.raises(ValidationError, match="Activity name cannot be empty"):
            csv_parser.parse(csv_content)

    def test_parse_csv_empty_duration(self, csv_parser: ProjectParser) -> None:
        """Test that empty duration raises ValidationError."""
        csv_content = """activity_name,duration,depends_on
A,,
"""
        with pytest.raises(ValidationError, match="Duration cannot be empty"):
            csv_parser.parse(csv_content)

    def test_parse_csv_invalid_duration(self, csv_parser: ProjectParser) -> None:
        """Test that invalid duration raises ValidationError."""
        csv_content = """activity_name,duration,depends_on
A,not_a_number,
"""
        with pytest.raises(ValidationError, match=r"Invalid duration.*must be a number"):
            csv_parser.parse(csv_content)

    def test_parse_csv_negative_duration(self, csv_parser: ProjectParser) -> None:
        """Test that negative duration raises ValueError."""
        csv_content = """activity_name,duration,depends_on
A,-5,
"""
        with pytest.raises(ValueError, match="Duration cannot be negative"):
            csv_parser.parse(csv_content)

    def test_parse_csv_circular_dependency(self, csv_parser: ProjectParser) -> None:
        """Test that circular dependencies raise ValueError."""
        csv_content = """activity_name,duration,depends_on
A,5,B
B,3,A
"""
        with pytest.raises(ValueError, match="circular"):
            csv_parser.parse(csv_content)

    def test_parse_csv_missing_dependency(self, csv_parser: ProjectParser) -> None:
        """Test that missing dependency raises ValueError."""
        csv_content = """activity_name,duration,depends_on
A,5,B
"""
        with pytest.raises(ValueError, match="non-existent"):
            csv_parser.parse(csv_content)

    def test_parse_csv_whitespace_handling(self, csv_parser: ProjectParser) -> None:
        """Test that whitespace is properly trimmed."""
        csv_content = """activity_name,duration,depends_on
  A  ,  5  ,
  B  ,  3  ,  A
"""
        network = parse_from(csv_parser, csv_content)

        assert len(network.activities) == 2
        activity_names = {a.name.value for a in network.activities}
        assert activity_names == {"A", "B"}
