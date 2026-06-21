from typing import Optional, TypedDict


class FundReturn(TypedDict):
    """Canonical data shape for a single NAV data point."""

    org_date: str
    nav: float
    dividend: float
    value: float
    adjusted: float
