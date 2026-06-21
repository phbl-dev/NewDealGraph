from dataclasses import dataclass


@dataclass(frozen=True)
class TraceConfig:
    """Declarative configuration for a single chart series."""

    label: str
    color: str
    show_dividends: bool = False
    # Express values as % change anchored to the primary series' starting NAV.
    use_percentage_offset: bool = False
    # Use the dividend-corrected adjusted_nav() calculation (PMINDI only).
    use_adjusted: bool = False
    # Use the pre-computed "adjusted" column from Yahoo Finance (benchmark only).
    use_yf_adjusted: bool = False
    fill_to_zero: bool = False