"""Tests for domain value objects."""

from decimal import Decimal

import pytest

from parade.domain.activity import ActivityName, Duration, Float


class TestActivityName:
    """Tests for ActivityName value object."""

    def test_valid_activity_name(self) -> None:
        """Test creating a valid ActivityName."""
        activity_name = ActivityName("task_1")
        assert activity_name.value == "task_1"

    def test_empty_activity_name_raises_error(self) -> None:
        """Test that empty ActivityName raises ValueError."""
        with pytest.raises(ValueError, match="Activity name cannot be empty"):
            ActivityName("")

    def test_whitespace_activity_name_raises_error(self) -> None:
        """Test that whitespace-only ActivityName raises ValueError."""
        with pytest.raises(ValueError, match="Activity name cannot be empty"):
            ActivityName("   ")


class TestDuration:
    """Tests for Duration value object."""

    def test_valid_duration(self) -> None:
        """Test creating a valid Duration."""
        duration = Duration(Decimal("5.0"))
        assert duration.value == Decimal("5.0")

    def test_zero_duration(self) -> None:
        """Test that zero duration is valid."""
        duration = Duration(Decimal(0))
        assert duration.value == Decimal(0)

    def test_negative_duration_raises_error(self) -> None:
        """Test that negative duration raises ValueError."""
        with pytest.raises(ValueError, match="Duration cannot be negative"):
            Duration(Decimal("-1.0"))

    def test_nan_duration_raises_error(self) -> None:
        """Test that NaN duration raises ValueError."""
        with pytest.raises(ValueError, match="Duration cannot be NaN"):
            Duration(Decimal("NaN"))

    def test_positive_infinity_duration_raises_error(self) -> None:
        """Test that positive infinity duration raises ValueError."""
        with pytest.raises(ValueError, match="Duration cannot be infinite"):
            Duration(Decimal("Infinity"))

    def test_negative_infinity_duration_raises_error(self) -> None:
        """Test that negative infinity duration raises ValueError."""
        with pytest.raises(ValueError, match="Duration cannot be infinite"):
            Duration(Decimal("-Infinity"))

    def test_duration_addition(self) -> None:
        """Test adding two durations."""
        d1 = Duration(Decimal("5.0"))
        d2 = Duration(Decimal("3.0"))
        result = d1 + d2
        assert result == Duration(Decimal("8.0"))

    def test_duration_subtraction(self) -> None:
        """Test subtracting two durations."""
        d1 = Duration(Decimal("5.0"))
        d2 = Duration(Decimal("3.0"))
        result = d1 - d2
        assert result == Duration(Decimal("2.0"))

    def test_duration_comparison(self) -> None:
        """Test comparing durations."""
        d1 = Duration(Decimal("5.0"))
        d2 = Duration(Decimal("3.0"))
        d3 = Duration(Decimal("5.0"))

        assert d1 > d2
        assert d2 < d1
        assert d1 >= d3
        assert d1 <= d3
        assert d1 == d3


class TestFloat:
    """Tests for Float value object."""

    def test_valid_float(self) -> None:
        """Test creating a valid Float."""
        slack = Float(Decimal("2.0"))
        assert slack.value == Decimal("2.0")

    def test_negative_float_raises_error(self) -> None:
        """Test that negative float raises ValueError."""
        with pytest.raises(ValueError, match="Duration cannot be negative"):
            Float(Decimal("-1.0"))

    def test_nan_float_raises_error(self) -> None:
        """Test that NaN float raises ValueError."""
        with pytest.raises(ValueError, match="Duration cannot be NaN"):
            Float(Decimal("NaN"))

    def test_positive_infinity_float_raises_error(self) -> None:
        """Test that positive infinity float raises ValueError."""
        with pytest.raises(ValueError, match="Duration cannot be infinite"):
            Float(Decimal("Infinity"))

    def test_negative_infinity_float_raises_error(self) -> None:
        """Test that negative infinity float raises ValueError."""
        with pytest.raises(ValueError, match="Duration cannot be infinite"):
            Float(Decimal("-Infinity"))

    def test_float_from_duration(self) -> None:
        """Test creating Float from Duration."""
        duration = Duration(Decimal("5.0"))
        slack = Float.from_duration(duration)
        assert slack.value == Decimal("5.0")

    def test_float_comparison(self) -> None:
        """Test comparing floats."""
        f1 = Float(Decimal("5.0"))
        f2 = Float(Decimal("3.0"))
        f3 = Float(Decimal("5.0"))

        assert f1 > f2
        assert f2 < f1
        assert f1 >= f3
        assert f1 <= f3
        assert f1 == f3
