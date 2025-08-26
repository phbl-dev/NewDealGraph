import json
import math
from typing import List, Optional
import plotly.graph_objects as go

from plotly.utils import PlotlyJSONEncoder

from src import (
    DataCollector as DC,
    DataProcessing as DP,
    FundReturn,
    GraphBuilder as GB,
)


@staticmethod
def generate_graph(
    datasource_one: Optional[List[FundReturn]] = None,
    datasource_two: Optional[List[FundReturn]] = None,
    show_adjusted: bool = False,
):
    """
    Genererer en graf over fondsafkast for to datasæt.

    Args:
        datasource_one: Fondsdata fra FundMarket (PMINDI).
        datasource_two: Fondsdata fra Yahoo Finance (QQQ).
        show_adjusted: Hvis True, anvendes NAV + udbytter.

    Returns:
        Plotly-figur.
    """

    ymin = math.floor(min([p["value"] for p in datasource_one]) * 0.9) or 0
    ymax = math.floor(max([p["value"] for p in datasource_one]) * 1.1) or 0

    time_labels = ["6M", "YTD", "12M", "MAX"]
    fig = go.Figure()
    buttons = []
    for i, label in enumerate(time_labels):
        TRACES_PER_LABEL = 4
        TOTAL_TRACES = len(time_labels) * TRACES_PER_LABEL
        base = i * TRACES_PER_LABEL
        visibility = [
            base <= idx < base + TRACES_PER_LABEL for idx in range(TOTAL_TRACES)
        ]
        pct_str = DP.calculate_rise(
            add_graph(datasource_one, datasource_two, show_adjusted, fig, label)
        )

        buttons.append(
            {
                "label": f"{5*' '} {label}<br>{pct_str}",
                "method": "update",
                "args": [{"visible": visibility}],
                
            }
        )

    tickvals, ticktext = GB.format_dates(datasource_one)
    fig.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "direction": "right",
                "x": 0.5,
                "y": -0.3,
                "showactive": True,
                "active": 3,
                "buttons": buttons,
                "pad": {
                    "t": 5,
                    "b": 5,
                    "l": 3,
                    "r": 3,
                },
                "font": {"size": 10, "family": "verdana"},
                "xanchor": "center",
                "yanchor": "top",
            },
        ],
        xaxis=dict(
            tickmode="auto",
            tickvals=tickvals,
            ticktext=ticktext,
            nticks=6,
            tickangle=-45,
            showgrid=False,
        ),
        yaxis=dict(
            title="Kurs",
            hoverformat=".2f",
            showgrid=False,
            side="right",
            rangemode="tozero",  # optional safeguard
            range=[ymin, ymax],
        ),
        plot_bgcolor="white",
        hovermode="x unified",
        legend={
            "orientation": "h",
            "x": 0.5,
            "y": 1.12,
            "xanchor": "center",
            "yanchor": "top",
            "bgcolor": "rgba(255,255,255,0.5)",
            "bordercolor": "rgba(128, 0, 128, 1)",
            "borderwidth": 1,
        },
        autosize=True,
        margin={"t": 120, "l": 50, "r": 50, "b": 80},
    )

    return fig


@staticmethod
def add_graph(datasource_one, datasource_two, show_adjusted, fig, label):
    pm_filtered = DP.filter_by_timespan(datasource_one, label)
    ndx_filtered = DP.filter_by_timespan(datasource_two, label)

    if show_adjusted:
        pm_adjusted = DP.calculate_adjusted(pm_filtered)
        pm_plot = [{**item, "nav": adj} for item, adj in zip(pm_filtered, pm_adjusted)]
        ndx_adjusted = DP.calculate_adjusted(ndx_filtered)

        ndx_plot = [
            {**item, "nav": adj} for item, adj in zip(ndx_filtered, ndx_adjusted)
        ]

        # Get PMINDI starting value for alignment
        pmindi_start_value, pm_hover_text = calculate_alignment(pm_plot)

        GB.add_fund_trace(
            fig,
            pm_plot,
            "PMINDI.CO",
            "purple",
            show_dividends=False,
            visible=(label == "12M"),
            custom_hover_text=pm_hover_text,
        )

        # For NDX: calculate percentage changes and offset by PMINDI starting value
        ndx_navs = [item["nav"] for item in ndx_plot]
        ndx_pct = DP.calculate_percentage(ndx_navs)

        # Offset percentage values to start at PMINDI's starting point
        if pmindi_start_value:
            ndx_pct_offset = [pct + pmindi_start_value for pct in ndx_pct]
        else:
            ndx_pct_offset = ndx_pct

        ndx_pct_plot = [
            {**item, "nav": pct} for item, pct in zip(ndx_plot, ndx_pct_offset)
        ]

        # Create hover text showing only percentage changes for NDX
        ndx_hover_text = [f"{pct:+.1f}%" for pct in ndx_pct]

        GB.add_fund_trace(
            fig,
            ndx_pct_plot,
            "NASDAQ",
            "black",
            show_dividends=False,
            visible=(label == "12M"),
            custom_hover_text=ndx_hover_text,
        )
        return pm_plot

        # Get PMINDI starting value for alignment
    pmindi_start_value, pm_hover_text = calculate_alignment(pm_filtered)

    GB.add_fund_trace(
        fig,
        pm_filtered,
        "PMINDI.CO",
        "purple",
        show_dividends=True,
        visible=(label == "12M"),
        custom_hover_text=pm_hover_text,
    )

    # For NDX: calculate percentage changes and offset by PMINDI starting value
    ndx_navs = [item["nav"] for item in ndx_filtered]
    ndx_pct = DP.calculate_percentage(ndx_navs)

    # Offset percentage values to start at PMINDI's starting point
    if pmindi_start_value:
        ndx_pct_offset = [pct + pmindi_start_value for pct in ndx_pct]
    else:
        ndx_pct_offset = ndx_pct

    ndx_pct_plot = [
        {**item, "nav": pct} for item, pct in zip(ndx_filtered, ndx_pct_offset)
    ]

    # Create hover text showing only percentage changes for NDX
    ndx_hover_text = [f"{pct:+.1f}%" for pct in ndx_pct]

    GB.add_fund_trace(
        fig,
        ndx_pct_plot,
        "NASDAQ",
        "black",
        show_dividends=False,
        visible=(label == "12M"),
        custom_hover_text=ndx_hover_text,
    )
    return pm_filtered


@staticmethod
def calculate_alignment(pm_plot):
    pmindi_start_value = pm_plot[0]["nav"] if pm_plot else None

    # Calculate PMINDI percentage changes for hover text
    pm_values = [item["nav"] for item in pm_plot]
    pm_pct_changes = DP.calculate_percentage(pm_values)
    pm_hover_text = [
        f"{val:.2f} kr ({pct:+.1f}%)" for val, pct in zip(pm_values, pm_pct_changes)
    ]

    return pmindi_start_value, pm_hover_text


if __name__ == "__main__":
    fig_regular = generate_graph(DC.get_data_mf("1198"), DC.get_data_yf("QQQ"), False)
    fig_adjusted = generate_graph(DC.get_data_mf("1198"), DC.get_data_yf("QQQ"), True)

    with open("regular.json", "w", encoding="UTF-8") as f:
        json.dump(fig_regular.to_plotly_json(), f, cls=PlotlyJSONEncoder)

    with open("adjusted.json", "w", encoding="UTF-8") as f:
        json.dump(fig_adjusted.to_plotly_json(), f, cls=PlotlyJSONEncoder)

    fig_regular_json = json.dumps(fig_regular.to_plotly_json(), cls=PlotlyJSONEncoder)
    fig_adjusted_json = json.dumps(fig_adjusted.to_plotly_json(), cls=PlotlyJSONEncoder)

    with open("fund_performance_toggle.html", "w", encoding="UTF-8") as f:
        f.write(GB.build_html(fig_regular_json, fig_adjusted_json))
