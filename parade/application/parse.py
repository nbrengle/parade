"""Application layer for parsing project data from different input formats."""

from abc import ABC, abstractmethod
from enum import StrEnum, auto

from parade.domain.project_network import UnscheduledProjectNetwork

__all__ = ["InputFormat", "ParseError", "ProjectParser", "ValidationError", "parse_from"]


class ParseError(ValueError):
    """Raised when content cannot be parsed into the expected format."""

    def __init__(self, message: str, line_number: int | None = None) -> None:
        """Initialize parse error.

        Args:
            message: Description of the parsing error.
            line_number: Optional line number where the error occurred.
        """
        self.line_number = line_number
        if line_number is not None:
            super().__init__(f"Line {line_number}: {message}")
        else:
            super().__init__(message)


class ValidationError(ValueError):
    """Raised when parsed data fails validation."""

    def __init__(self, message: str, field: str | None = None) -> None:
        """Initialize validation error.

        Args:
            message: Description of the validation error.
            field: Optional field name that failed validation.
        """
        self.field = field
        if field is not None:
            super().__init__(f"Field '{field}': {message}")
        else:
            super().__init__(message)


class InputFormat(StrEnum):
    """Supported input formats for project data."""

    CSV = auto()


class ProjectParser(ABC):
    """Abstract base class for parsing project data into domain objects."""

    @abstractmethod
    def parse(self, content: str) -> UnscheduledProjectNetwork:
        """Parse content into an unscheduled project network.

        Args:
            content: The raw content to parse.

        Returns:
            An unscheduled project network.

        Raises:
            ParseError: If the content cannot be parsed.
            ValidationError: If the parsed data fails validation.
        """


def parse_from(parser: ProjectParser, content: str) -> UnscheduledProjectNetwork:
    """Parse project data using the provided parser.

    Args:
        parser: The parser implementation to use.
        content: The raw content to parse.

    Returns:
        An unscheduled project network.
    """
    return parser.parse(content)
