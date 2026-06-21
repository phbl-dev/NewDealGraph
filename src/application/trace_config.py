from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class TraceConfig:
    """Declarative configuration for a single chart series."""

    label: str
    color: str
    show_dividends: bool = False
    # If True, NAV is expressed as a % change anchored to the primary series.
    use_percentage_offset: bool = False
    # If True, the adjusted column (total return) is used instead of NAV.
    use_adjusted: bool = False
    fill_to_zero: bool = False
