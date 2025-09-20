import json
from typing import List
import plotly.graph_objects as go
from src.FundReturn import FundReturn


class GraphBuilder:
    @staticmethod
    def format_dates(data: List[FundReturn]):
        """Return tickvals and Danish month labels for the x-axis"""
        danish_months = [
            "",
            "jan",
            "feb",
            "mar",
            "apr",
            "maj",
            "jun",
            "jul",
            "aug",
            "sep",
            "okt",
            "nov",
            "dec",
        ]

        tickvals = []
        ticktext = []
        seen = set()

        for item in data:
            dt = item["date_obj"]
            ym = (dt.year, dt.month)
            if ym not in seen:
                seen.add(ym)
                tickvals.append(dt)
                ticktext.append(f"{danish_months[dt.month]} {dt.year}")

        return tickvals, ticktext

    @staticmethod
    def add_fund_trace(
        fig,
        data,
        label,
        color,
        show_dividends=False,
        visible=False,
        custom_hover_text=None,
    ):
        dates = [item["date_obj"] for item in data]
        values = [item["nav"] for item in data]
        dividends = [item["dividend"] for item in data]

        fill_color = None
        fill_mode = None
        line_color = color
        if label == "PMINDI.CO":
            line_color = "rgba(128, 0, 128, 1)"  # solid purple line
            fill_mode = "tozeroy"  # fill area to zero line
            fill_color = "rgba(128, 0, 128, 0.3)"  # translucent purple fill

        # Set up hover template based on custom text or default
        if custom_hover_text:
            hovertemplate = (
                f"<b>{label}</b><br>" + "Date: %{x}<br>Value: %{text}<extra></extra>"
            )
            text = custom_hover_text
        else:
            hovertemplate = (
                f"<b>{label}</b><br>" + "Date: %{x}<br>Value: %{y:.2f}<extra></extra>"
            )
            text = None

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines",
                name=label,
                opacity=0.9,
                line=dict(color=line_color),
                fill=fill_mode,
                fillcolor=fill_color,
                visible=visible,
                text=text,
                hovertemplate=hovertemplate,
            )
        )
        if show_dividends:
            div_x = [d for d, div in zip(dates, dividends) if div > 0]
            div_y = [pct for pct, div in zip(values, dividends) if div > 0]
            div_text = [
                f"Årligt udbytte\nDato: {item['date_obj'].strftime('%Y-%m-%d')}\nUdbytte: {item['dividend']:.2f} DKK"
                for item in data
                if item["dividend"] > 0
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
                name=f"{label} Udbytte",
                marker={"color": f"{line_color}", "size": 16, "symbol": "diamond"},
                visible=visible and show_dividends,
                hoverinfo="text",
            )
        )

    @staticmethod
    def build_graph_with_aligned_start(pmindi_data, ndx_data, show_dividends=False):
        """Build a graph where NDX values are scaled to start at the same point as PMINDI"""
        fig = go.Figure()
        # Add PMINDI trace first (with raw values)
        GraphBuilder.add_fund_trace(
            fig,
            pmindi_data,
            "PMINDI.CO",
            "purple",
            show_dividends=show_dividends,
            visible=True,
        )

        # Add NDX trace with aligned starting point
        GraphBuilder.add_fund_trace(
            fig, ndx_data, "NDX", "blue", show_dividends=show_dividends, visible=True
        )

        # Format dates for x-axis
        all_data = pmindi_data + ndx_data
        tickvals, ticktext = GraphBuilder.format_dates(all_data)

        # Update layout
        fig.update_layout(
            title="Fund Performance Comparison (Aligned Start)",
            xaxis=dict(tickvals=tickvals, ticktext=ticktext, title="Date"),
            yaxis=dict(title="Value"),
            hovermode="x unified",
        )

        return fig