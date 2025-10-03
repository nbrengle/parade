"""Hypothesis strategies for domain types."""

from decimal import Decimal

from hypothesis import strategies as st

from parade.domain.activity import Duration


@st.composite
def durations(draw: st.DrawFn) -> Duration:
    """Generate a valid Duration.

    Generates positive finite Decimals that match domain constraints.
    Limits to reasonable range and precision for performance and avoid rounding errors.
    """
    value = draw(
        st.decimals(
            min_value=Decimal("0.001"),
            max_value=Decimal(10000),
            allow_nan=False,
            allow_infinity=False,
            places=3,  # Limit to 3 decimal places to avoid precision issues
        ),
    )
    return Duration(value)
