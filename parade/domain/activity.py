"""Activity domain model for Critical Path Method."""

from dataclasses import InitVar, dataclass, field
from decimal import Decimal
from typing import Self

type DecimalConvertible = int | str | Decimal


@dataclass(frozen=True)
class ActivityName:
    """Value object representing an activity name."""

    value: str

    def __post_init__(self) -> None:
        """Validate activity name."""
        if not self.value.strip():
            msg = "Activity name cannot be empty"
            raise ValueError(msg)

    def __eq__(self, other: object) -> bool:
        """Compare ActivityName with another ActivityName or string."""
        if isinstance(other, ActivityName):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self) -> int:
        """Return hash based on value."""
        return hash(self.value)


@dataclass(frozen=True)
class Duration:
    """Value object representing the duration of an activity in abstract time units."""

    value: Decimal

    def __new__(cls, value: DecimalConvertible) -> Self:
        """Create and validate a Duration, converting the input to Decimal."""
        # Convert to Decimal if needed
        decimal_value = Decimal(value) if not isinstance(value, Decimal) else value

        if decimal_value.is_nan():
            msg = "Duration cannot be NaN"
            raise ValueError(msg)
        if decimal_value.is_infinite():
            msg = "Duration cannot be infinite"
            raise ValueError(msg)
        if decimal_value < 0:
            msg = "Duration cannot be negative"
            raise ValueError(msg)

        # Create instance with normalized Decimal value
        instance = object.__new__(cls)
        object.__setattr__(instance, "value", decimal_value)
        return instance

    def __add__(self, other: Self) -> Duration:
        """Add two durations together."""
        return Duration(self.value + other.value)

    def __sub__(self, other: Self) -> Duration:
        """Subtract one duration from another."""
        return Duration(self.value - other.value)

    def __lt__(self, other: Self) -> bool:
        """Check if this duration is less than another."""
        return self.value < other.value

    def __le__(self, other: Self) -> bool:
        """Check if this duration is less than or equal to another."""
        return self.value <= other.value

    def __gt__(self, other: Self) -> bool:
        """Check if this duration is greater than another."""
        return self.value > other.value

    def __ge__(self, other: Self) -> bool:
        """Check if this duration is greater than or equal to another."""
        return self.value >= other.value


@dataclass(frozen=True)
class Float(Duration):
    """Value object representing the slack time available for an activity.

    Float is the amount of time an activity can be delayed without
    delaying the project completion date.
    """

    @classmethod
    def from_duration(cls, duration: Duration) -> Self:
        """Create a Float from a Duration."""
        return cls(duration.value)


@dataclass(frozen=True, kw_only=True)
class Activity:
    """Base class for all activities with core attributes.

    All activities have:
    - A unique name for reference
    - A duration (time to complete)
    - Dependencies (other activities that must complete first)

    The depends_on parameter accepts strings or ActivityName objects for convenience,
    which are automatically converted to ActivityName objects and stored in dependencies.
    """

    name: ActivityName
    duration: Duration
    depends_on: InitVar[frozenset[str | ActivityName] | None] = None
    dependencies: frozenset[ActivityName] = field(init=False, default_factory=frozenset)

    def __post_init__(self, depends_on: frozenset[str | ActivityName] | None) -> None:
        """Convert string dependencies to ActivityName."""
        if depends_on is None:
            depends_on = frozenset()
        converted_deps = frozenset(ActivityName(dep) if isinstance(dep, str) else dep for dep in depends_on)
        object.__setattr__(self, "dependencies", converted_deps)

    def has_dependency(self, activity_name: ActivityName) -> bool:
        """Check if this activity depends on another activity."""
        return activity_name in self.dependencies


@dataclass(frozen=True, kw_only=True)
class UnscheduledActivity(Activity):
    """Value object representing a project activity before scheduling.

    Inherits all core activity attributes from Activity base class.
    """


@dataclass(frozen=True, kw_only=True)
class ScheduledActivity(Activity):
    """Value object representing a scheduled activity with calculated timings.

    Includes all core activity attributes plus:
    - Earliest start and finish times (from forward pass)
    - Latest start and finish times (from backward pass)
    - Calculated float
    """

    earliest_start: Duration
    earliest_finish: Duration
    latest_start: Duration
    latest_finish: Duration

    @property
    def total_float(self) -> Float:
        """Calculate the total float for this activity.

        Total Float = Latest Start - Earliest Start
        """
        return Float.from_duration(self.latest_start - self.earliest_start)

    @property
    def is_critical(self) -> bool:
        """Check if this activity is on the critical path (zero float)."""
        return self.total_float.value == 0
