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

    ymin, ymax = DP.calculate_yaxis_range(datasource_one, datasource_two, show_adjusted)

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
            # title="Afkast",
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
    """
    Adds PMINDI and NDX traces to a plotly figure.

    - PMINDI: optionally adjusted.
    - NDX: uses adjusted values only if show_adjusted=True.
    """
    # Filter by timespan
    pm_filtered = DP.filter_by_timespan(datasource_one, label)
    ndx_filtered = DP.filter_by_timespan(datasource_two, label)

    # PMINDI adjusted values if requested
    if show_adjusted:
        pm_adjusted = DP.calculate_adjusted(pm_filtered)
        pm_plot = [{**item, "nav": adj} for item, adj in zip(pm_filtered, pm_adjusted)]
        # NDX uses adjusted column
        ndx_plot = [{**item, "nav": item["adjusted"]} for item in ndx_filtered]
    else:
        pm_plot = pm_filtered
        # NDX uses raw nav
        ndx_plot = [{**item, "nav": item["nav"]} for item in ndx_filtered]

    # Calculate percentage changes for NDX
    ndx_navs = [item["nav"] for item in ndx_plot]
    ndx_pct = DP.calculate_percentage(ndx_navs)

    # Get PMINDI starting value for alignment
    pmindi_start_value, pm_hover_text = calculate_alignment(pm_plot)

    # Add PMINDI trace
    GB.add_fund_trace(
        fig,
        pm_plot,
        "PMINDI.CO",
        "purple",
        show_dividends=not show_adjusted,
        visible=(label == "MAX"),
        custom_hover_text=pm_hover_text,
    )

    # Offset NDX percentage values to start at PMINDI's starting point
    ndx_pct_offset = (
        [pct + pmindi_start_value for pct in ndx_pct] if pmindi_start_value else ndx_pct
    )

    ndx_pct_plot = [{**item, "nav": pct} for item, pct in zip(ndx_plot, ndx_pct_offset)]

    # Hover text showing only percentage changes for NDX
    ndx_hover_text = [f"{pct:+.1f}%" for pct in ndx_pct]

    GB.add_fund_trace(
        fig,
        ndx_pct_plot,
        "NASDAQ",
        "black",
        show_dividends=False,
        visible=(label == "MAX"),
        custom_hover_text=ndx_hover_text,
    )

    return pm_plot if show_adjusted else pm_filtered


@staticmethod
def create_box_html() -> str:
    return f"""
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
        }}
      .rectangle {{
            width: 600px;
            height: 75px;
            border: 1px solid #F4F4F4;
            background-color: #F4F4F4;
            border-radius: 10px;
            display: flex;
            align-items: center;
            padding: 15px;
            box-sizing: border-box;
            justify-content: space-between;
        }}
      .group {{
        display: flex;
        align-items: center;
        gap: 10px;
      }}
      .left_info {{
        display: flex;
        flex-direction: column;
      }}
      .right_info {{
        display: flex;
        flex-direction: column;
        text-align: right;
      }}
      .percentage {{
        font-size: 18px;
        font-weight: bold;
        margin: 0;
        color: #333;
      }}
      .image {{
        width: 40px !important;
        opacity: 70%;
      }}
      .amount {{
        font-size: 18px;
        font-weight: bold;
        margin: 0;
        color: #333;
      }}
      .date-info {{
        font-size: 12px;
        margin: 2px 0 0 0;
        color: #666;
      }}
      .return-info {{
        font-size: 12px;
        margin: 2px 0 0 0;
      }}

/* Tooltip container */
      .tooltip {{
        position: relative;
        display: inline-block;
        cursor: pointer;
      }}

      .tooltip .tooltiptext {{
        visibility: hidden;
        width: 250px;
        background-color: #555;
        color: #fff;
        text-align: left;
        padding: 5px 10px;
        border-radius: 5px;
        position: absolute;
        z-index: 1;
        top: 125%; /* below the button */
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
        white-space: normal;
        word-wrap: break-word;
      }}

      /* Arrow pointing up */
      .tooltip .tooltiptext::before {{
        content: "";
        position: absolute;
        top: -5px; /* above the tooltip box */
        left: 50%;
        transform: translateX(-50%);
        border-width: 5px;
        border-style: solid;
        border-color: transparent transparent #555 transparent; /* arrow pointing up */
      }}

      .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
      }}
    </style>
  </head>
  <body>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
      <div class="rectangle">
        <div class="group">
        <i class="fas fa-solid fa-calendar" style="font-size: 35px; opacity: 70%;;"></i>
          <div class="left_info">
            <h4 class="amount">38.9 DKK/andel</h4>
            <p class="date-info">X-dag 22. jan 2024</p>
          </div>
        </div>

        <div class="group">
          <div class="right_info">
            <h4 class="percentage">21%</h4>
            <p class="return-info">Udbytte</p>
          </div>
          <div class="tooltip">
        <i class="fas fa-solid fa-circle-info" style="font-size: 35px; opacity: 70%;;"></i>
            <span class="tooltiptext"> Udbyttet fragik kursen den 22. januar 2025. Udlodningen skete på baggrund af et samlet afkast i 2024 på 46 %, og er baseret på ligningslovens krav til minimumsudlodning. Udbyttet er opgjort til 38,90 kr./andel.</span>
          </div>
        </div>
      </div>
  </body>
</html>
    """


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

    with open("box.html", "w", encoding="utf-8") as f:
        f.write(create_box_html())
