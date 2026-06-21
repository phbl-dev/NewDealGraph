"""
Entry point.

All dependencies are wired here — nothing inside src instantiates
concrete classes directly.  To swap a data source, change the binding here.
"""

import json
from pathlib import Path

from plotly.utils import PlotlyJSONEncoder

from src.application.chart_builder import ChartBuilder
from src.application.returns_calculator import ReturnsCalculator
from src.application.trace_config import TraceConfig
from src.infrastructure.fundmarket_source import FundMarketDataSource
from src.infrastructure.yahoo_finance_source import YahooFinanceDataSource
from src.presentation.html_renderer import HTMLRenderer

# ---------------------------------------------------------------------------
# Series configuration
# ---------------------------------------------------------------------------

BRAND_BLUE = "#1B3C76"

PMINDI_REGULAR = TraceConfig(
    label="PMINDI.CO",
    color=BRAND_BLUE,
    show_dividends=True,
    fill_to_zero=True,
)

PMINDI_ADJUSTED = TraceConfig(
    label="PMINDI.CO",
    color=BRAND_BLUE,
    use_adjusted=True,
    fill_to_zero=True,
)

PMINDIAKK = TraceConfig(
    label="PMINDIAKK.CO",
    color=BRAND_BLUE,
    fill_to_zero=True,
)

NASDAQ_REGULAR = TraceConfig(
    label="NASDAQ",
    color="#ffffff",
    use_percentage_offset=True,
)

NASDAQ_ADJUSTED = TraceConfig(
    label="NASDAQ",
    color="#ffffff",
    use_percentage_offset=True,
    use_yf_adjusted=True,   # read item["adjusted"] (YF pre-computed), then % offset
)

NASDAQ_AKK = TraceConfig(
    label="NASDAQ",
    color="#ffffff",
    use_percentage_offset=True,
)

# ---------------------------------------------------------------------------
# Dividend box content (keep presentation data out of the renderer itself)
# ---------------------------------------------------------------------------

DIVIDEND_BOX = dict(
    amount_per_share="38.9 DKK/andel",
    ex_date="22. jan 2024",
    return_percentage="21%",
    tooltip_text=(
        "Udbyttet fragik kursen den 22. januar 2025. "
        "Udlodningen skete på baggrund af et samlet afkast i 2024 på 46 %, "
        "og er baseret på ligningslovens krav til minimumsudlodning. "
        "Udbyttet er opgjort til 38,90 kr./andel."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_json(fig) -> str:
    return json.dumps(fig.to_plotly_json(), cls=PlotlyJSONEncoder)


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # --- Infrastructure
    pm_source  = FundMarketDataSource(timeout=30)
    yf_source  = YahooFinanceDataSource(start_date="2023-09-22")
    
    yf_source_akk  = YahooFinanceDataSource(start_date="2025-12-05")

    pm_data  = pm_source.fetch("1198")
    ndx_data = yf_source.fetch("QQQ")
    ndx_data_akk = yf_source_akk.fetch("QQQ")
    akk_data = pm_source.fetch("1251")

    # --- Application
    calculator = ReturnsCalculator()
    builder    = ChartBuilder(calculator)

    fig_regular  = builder.build(pm_data,  ndx_data, PMINDI_REGULAR,  NASDAQ_REGULAR)
    fig_adjusted = builder.build(pm_data,  ndx_data, PMINDI_ADJUSTED, NASDAQ_ADJUSTED)
    fig_akk      = builder.build(akk_data, ndx_data_akk, PMINDIAKK,       NASDAQ_AKK)

    regular_json  = _to_json(fig_regular)
    adjusted_json = _to_json(fig_adjusted)
    akk_json      = _to_json(fig_akk)

    # --- Presentation
    out = Path(".")
    _write(out / "regular.json",  regular_json)
    _write(out / "adjusted.json", adjusted_json)
    _write(out / "akk.json",      akk_json)
    _write(
        out / "fund_performance_toggle.html",
        HTMLRenderer.render_chart_page(regular_json, adjusted_json, akk_json),
    )
    _write(out / "box.html", HTMLRenderer.render_dividend_box(**DIVIDEND_BOX))

    print("Done.")


if __name__ == "__main__":
    main()