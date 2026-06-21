import math
from datetime import date, datetime
from typing import List, Sequence

from dateutil.relativedelta import relativedelta

from src.domain.fund_return import FundReturn

# Each entry represents the retention factor applied at each successive dividend
# event.  A factor of 0.786 means the NAV dropped to 78.6 % of its pre-dividend
# value after the payout, so adjusted values are divided by the cumulative
# product of all prior factors.
_DIVIDEND_RETENTION_FACTORS: tuple[float, ...] = (0.786, 0.782)


class ReturnsCalculator:
    """Pure-function helpers for transforming fund return data."""

    # ------------------------------------------------------------------
    # Percentage helpers
    # ------------------------------------------------------------------

    @staticmethod
    def percentage_changes(values: Sequence[float]) -> List[float]:
        """Return cumulative % change vs. the first value in *values*."""
        if not values:
            return []
        start = values[0]
        return [(v - start) / start * 100 for v in values]

    # ------------------------------------------------------------------
    # Dividend-adjusted NAV
    # ------------------------------------------------------------------

    @staticmethod
    def adjusted_nav(data: List[FundReturn]) -> List[float]:
        """
        Reconstruct a total-return NAV series by un-doing each dividend drop.

        Whenever a dividend > 0 is encountered the running factor is multiplied
        by the next retention factor from *_DIVIDEND_RETENTION_FACTORS*.
        Dividing NAV by the cumulative factor restores what the price *would*
        have been had dividends been reinvested.
        """
        if not data:
            return []

        cumulative_factor = 1.0
        dividend_index = 0
        adjusted: List[float] = []

        for point in data:
            dividend = point.get("dividend") or 0.0
            nav = point.get("nav") or 0.0

            if dividend > 0 and dividend_index < len(_DIVIDEND_RETENTION_FACTORS):
                cumulative_factor *= _DIVIDEND_RETENTION_FACTORS[dividend_index]
                dividend_index += 1

            adjusted.append(nav / cumulative_factor)

        return adjusted

    # ------------------------------------------------------------------
    # Timespan filtering
    # ------------------------------------------------------------------

    @staticmethod
    def filter_by_timespan(data: List[FundReturn], timespan: str) -> List[FundReturn]:
        """
        Return records on or after the cutoff implied by *timespan*.

        Supported formats:
          - ``"<N>M"``  – last N calendar months  (e.g. ``"6M"``)
          - ``"YTD"``   – from 31 Dec of the prior year
          - anything else – entire history (no filtering)
        """
        today = date.today()
        t = timespan.upper()

        if t.endswith("M"):
            cutoff = today - relativedelta(months=int(t[:-1]))
        elif t == "YTD":
            cutoff = date(today.year, 1, 1) - relativedelta(days=1)
        else:
            cutoff = date.min

        result = []
        for item in data:
            item_date = datetime.strptime(item["org_date"], "%Y-%m-%d").date()
            if item_date >= cutoff:
                # Attach parsed date so callers don't have to re-parse
                result.append({**item, "date_obj": item_date})

        return result

    # ------------------------------------------------------------------
    # Summary statistics
    # ------------------------------------------------------------------

    @staticmethod
    def total_return_label(data: List[FundReturn]) -> str:
        """Return an emoji-prefixed percentage string for *data*'s full range."""
        if not data:
            return ""
        start, end = data[0]["nav"], data[-1]["nav"]
        pct = (end - start) / start * 100
        sign = "🟢" if pct >= 0 else "🔴"
        return f"{sign} {pct:+.1f}%"

    # ------------------------------------------------------------------
    # Y-axis range
    # ------------------------------------------------------------------

    @staticmethod
    def y_axis_range(
        primary: List[FundReturn],
        benchmark: List[FundReturn],
        use_adjusted: bool,
    ) -> tuple[float, float]:
        """
        Compute a y-axis range that accommodates both series as they will be
        plotted by ``ChartBuilder.build``.

        The benchmark is expressed as a percentage offset anchored to the
        primary series' starting NAV — this mirrors the chart's own alignment
        logic so the range is always accurate.
        """
        if not primary or not benchmark:
            return 0, 0

        if use_adjusted:
            primary_values = ReturnsCalculator.adjusted_nav(primary)
            benchmark_values = [p["adjusted"] for p in benchmark]
        else:
            primary_values = [p["nav"] for p in primary]
            benchmark_values = [p["nav"] for p in benchmark]

        anchor = primary_values[0]
        benchmark_pct = ReturnsCalculator.percentage_changes(benchmark_values)
        benchmark_offset = [pct + anchor for pct in benchmark_pct]

        all_values = primary_values + benchmark_offset
        return math.floor(min(all_values) * 0.9), math.ceil(max(all_values) * 1.1)
