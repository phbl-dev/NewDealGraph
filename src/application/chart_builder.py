from typing import List, Optional, Sequence

import plotly.graph_objects as go

from src.application.returns_calculator import ReturnsCalculator
from src.application.trace_config import TraceConfig
from src.domain.fund_return import FundReturn

_DANISH_MONTHS = (
    "", "jan", "feb", "mar", "apr", "maj", "jun",
    "jul", "aug", "sep", "okt", "nov", "dec",
)

_TIME_LABELS = ("6M", "YTD", "12M", "MAX")
_TRACES_PER_TIMESPAN = 4  # 2 series × (value trace + dividend trace)


class ChartBuilder:
    """
    Builds a Plotly Figure containing time-span toggle buttons and two series:
    a primary fund and a benchmark.

    Dependencies are injected; no concrete data source or calculator is
    instantiated here.
    """

    def __init__(self, calculator: ReturnsCalculator) -> None:
        self._calc = calculator

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(
        self,
        primary: List[FundReturn],
        benchmark: List[FundReturn],
        primary_cfg: TraceConfig,
        benchmark_cfg: TraceConfig,
    ) -> go.Figure:
        """
        Return a Figure with one button group per time-span label.

        *primary_cfg* and *benchmark_cfg* declare how each series should be
        styled and transformed — the builder never hard-codes series-specific
        behaviour.
        """
        ymin, ymax = self._calc.y_axis_range(
            primary, benchmark, use_adjusted=primary_cfg.use_adjusted
        )
        fig = go.Figure()
        buttons = []

        total_traces = len(_TIME_LABELS) * _TRACES_PER_TIMESPAN

        for i, label in enumerate(_TIME_LABELS):
            base = i * _TRACES_PER_TIMESPAN
            visibility = [base <= j < base + _TRACES_PER_TIMESPAN for j in range(total_traces)]

            pm_filtered = self._calc.filter_by_timespan(primary, label)
            bm_filtered = self._calc.filter_by_timespan(benchmark, label)

            pm_plot = self._apply_transform(pm_filtered, primary_cfg, anchor=None)
            anchor_value = pm_plot[0]["nav"] if pm_plot else None
            bm_plot = self._apply_transform(bm_filtered, benchmark_cfg, anchor=anchor_value)

            pm_hover = self._hover_text_primary(pm_plot)
            bm_hover = self._hover_text_benchmark(bm_plot, bm_filtered)

            self._add_trace(fig, pm_plot, primary_cfg, visible=(label == "MAX"), hover=pm_hover)
            self._add_trace(fig, bm_plot, benchmark_cfg, visible=(label == "MAX"), hover=bm_hover)

            rise_label = self._calc.total_return_label(pm_filtered)
            buttons.append(self._make_button(label, rise_label, visibility))

        tickvals, ticktext = self._format_date_axis(primary)

        fig.update_layout(
            updatemenus=[self._updatemenus_config(buttons)],
            xaxis=dict(
                tickmode="auto",
                tickvals=tickvals,
                ticktext=ticktext,
                nticks=6,
                tickangle=-45,
                showgrid=False,
            ),
            yaxis=dict(
                hoverformat=".2f",
                showgrid=False,
                side="right",
                rangemode="tozero",
                range=[ymin, ymax],
            ),
            plot_bgcolor="white",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                x=0.5, y=1.12,
                xanchor="center", yanchor="top",
                bgcolor="rgba(255,255,255,0.5)",
                bordercolor="#1B3C76",
                borderwidth=1,
            ),
            autosize=True,
            margin=dict(t=120, l=50, r=50, b=80),
        )

        return fig

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_transform(
        self,
        data: List[FundReturn],
        cfg: TraceConfig,
        anchor: Optional[float],
    ) -> List[FundReturn]:
        """Return a copy of *data* with nav replaced according to *cfg*.

        Transform order:
          1. Resolve the base value series (raw nav / YF adjusted / PMINDI adjusted).
          2. If use_percentage_offset, express as % change anchored to *anchor*.
        """
        # Step 1: resolve base values
        if cfg.use_adjusted:
            # PMINDI: dividend-corrected total-return NAV
            adj = self._calc.adjusted_nav(data)
            data = [{**item, "nav": v} for item, v in zip(data, adj)]
        elif cfg.use_yf_adjusted:
            # Benchmark: use the pre-computed "adjusted" column from Yahoo Finance
            data = [{**item, "nav": item["adjusted"]} for item in data]

        # Step 2: apply percentage offset so the benchmark aligns with PMINDI's scale
        if cfg.use_percentage_offset and anchor is not None:
            navs = [item["nav"] for item in data]
            pcts = self._calc.percentage_changes(navs)
            data = [{**item, "nav": pct + anchor} for item, pct in zip(data, pcts)]

        return data

    def _hover_text_primary(self, data: List[FundReturn]) -> List[str]:
        values = [item["nav"] for item in data]
        pcts = self._calc.percentage_changes(values)
        return [f"{v:.2f} kr ({p:+.1f}%)" for v, p in zip(values, pcts)]

    def _hover_text_benchmark(
        self,
        plotted: List[FundReturn],
        raw: List[FundReturn],
    ) -> List[str]:
        raw_navs = [item["nav"] for item in raw]
        pcts = self._calc.percentage_changes(raw_navs)
        return [f"{p:+.1f}%" for p in pcts]

    def _add_trace(
        self,
        fig: go.Figure,
        data: List[FundReturn],
        cfg: TraceConfig,
        visible: bool,
        hover: Optional[List[str]] = None,
    ) -> None:
        dates = [item["date_obj"] for item in data]
        values = [item["nav"] for item in data]
        dividends = [item.get("dividend", 0) for item in data]

        fill_mode = "tozeroy" if cfg.fill_to_zero else None
        line_color = cfg.color
        fill_color = self._translucent(cfg.color, 0.3) if cfg.fill_to_zero else None

        hovertemplate = (
            f"<b>{cfg.label}</b><br>Date: %{{x}}<br>Value: %{{text}}<extra></extra>"
            if hover
            else f"<b>{cfg.label}</b><br>Date: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>"
        )

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines",
                name=cfg.label,
                opacity=0.9,
                line=dict(color=line_color),
                fill=fill_mode,
                fillcolor=fill_color,
                visible=visible,
                text=hover,
                hovertemplate=hovertemplate,
            )
        )

        # Dividend markers
        if cfg.show_dividends:
            div_x = [d for d, div in zip(dates, dividends) if div > 0]
            div_y = [v for v, div in zip(values, dividends) if div > 0]
            div_text = [
                f"Årligt udbytte\nDato: {item['date_obj'].strftime('%Y-%m-%d')}\nUdbytte: {item['dividend']:.2f} DKK"
                for item in data
                if item.get("dividend", 0) > 0
            ]
        else:
            div_x, div_y, div_text = [], [], []

        fig.add_trace(
            go.Scatter(
                x=div_x,
                y=div_y,
                text=div_text,
                mode="markers",
                textposition="top center",
                name=f"{cfg.label} Udbytte",
                marker=dict(color=line_color, size=16, symbol="diamond"),
                visible=visible and cfg.show_dividends,
                hoverinfo="text",
            )
        )

    @staticmethod
    def _format_date_axis(data: List[FundReturn]):
        tickvals, ticktext = [], []
        seen: set = set()
        for item in data:
            dt = item.get("date_obj")
            if dt is None:
                from datetime import datetime
                dt = datetime.strptime(item["org_date"], "%Y-%m-%d").date()
            ym = (dt.year, dt.month)
            if ym not in seen:
                seen.add(ym)
                tickvals.append(dt)
                ticktext.append(f"{_DANISH_MONTHS[dt.month]} {dt.year}")
        return tickvals, ticktext

    @staticmethod
    def _make_button(label: str, rise: str, visibility: List[bool]) -> dict:
        return {
            "label": f"{'     '}{label}<br>{rise}",
            "method": "update",
            "args": [{"visible": visibility}],
        }

    @staticmethod
    def _updatemenus_config(buttons: list, active_index: int = 3) -> dict:
        # Default buttons are transparent with white text.
        # The active button is coloured #1B3C76 via styleActiveButton() in the JS.
        return {
            "type": "buttons",
            "direction": "right",
            "x": 0.5, "y": -0.3,
            "showactive": True,
            "active": active_index,
            "buttons": buttons,
            "pad": {"t": 5, "b": 5, "l": 3, "r": 3},
            "font": {"size": 10, "family": "verdana", "color": "#1B3C76"},
            "bgcolor": "rgba(255,255,255,0.85)",
            "bordercolor": "#1B3C76",
            "xanchor": "center",
            "yanchor": "top",
        }

    @staticmethod
    def _translucent(hex_color: str, alpha: float) -> str:
        """Convert a CSS hex colour to rgba(...) with the given alpha."""
        h = hex_color.lstrip("#")
        if len(h) == 6:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"
        # Fallback: return color as-is (e.g. already an rgba string)
        return hex_color