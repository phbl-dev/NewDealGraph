from typing import List, TypedDict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from plotly.io import to_html
import json
from plotly.utils import PlotlyJSONEncoder
import requests
import yfinance as yf
import pandas as pd


class FundReturn(TypedDict):
    """Interface klasse, så det er lettere at arbejde med data"""

    org_date: str
    nav: float
    dividend: float
    value: float


def get_data_mf(fund_id: str) -> List[FundReturn]:
    """Hent data omkring fonde understøttet af FundMarket"""
    url = f"https://node-api.fundmarket.dk/funds/ninfo/{fund_id}"
    response = requests.get(url, timeout=1000)
    data = response.json()["returns"]

    return data


def get_data_yf(fund_id) -> List[FundReturn]:
    """Hent data omkring fonde understøttet af yfinance API"""
    data = yf.Ticker(fund_id).history(
        start="2023-09-22", end=str(date.today()), actions=True
    )

    data = data.reset_index()

    nasdaq_cleaned = [
        {
            "org_date": row["Date"].date().isoformat(),
            "nav": row["Close"],
            "dividend": row["Dividends"],
            "value": row["Close"],
        }
        for _, row in data.iterrows()
    ]
    return nasdaq_cleaned


def generate_graph(show_adjusted=False):
    pmindi_data = get_data_mf(1198)
    nasdaq_data = get_data_yf("QQQ")

    print(pmindi_data)

    def filter_by_timespan(data, timespan: str) -> list[FundReturn]:
        """Filtrering af data med måneder. Måneder angives i hele tal og afsluttes med "M". F.eks. vil man skrive "6M", hvis man skal bruges 6 måneder."""
        today = date.today()
        for item in data:
            item["date_obj"] = datetime.strptime(item["org_date"], "%Y-%m-%d").date()

        t = timespan.upper()
        if t.endswith("M"):
            month = int(t[:-1])
            cutoff = today - relativedelta(months=month)
        elif t == "YTD":
            cutoff = date(today.year, 1, 1)
        else:
            cutoff = date.min

        return [item for item in data if item["date_obj"] >= cutoff]

    def calculate_adjusted(data):
        """Udregn adjusted close inkl. udbytte"""
        if not data:
            return []

        adjusted = [data[0]["nav"]]
        for k in range(1, len(data)):
            prev_adj = adjusted[-1]
            nav_today = data[k]["nav"]
            nav_yesterday = data[k - 1]["nav"]
            dividend_today = data[k]["dividend"]
            new_adj = prev_adj * ((nav_today + dividend_today) / nav_yesterday)
            adjusted.append(new_adj)

        return adjusted

    def calculate_rise(label):
        pm_filtered = filter_by_timespan(pmindi_data, label)
        if pm_filtered:
            start_val = pm_filtered[0]["nav"]
            end_val = pm_filtered[-1]["nav"]
            pct_change = (end_val - start_val) / start_val * 100
            sign = "🟢" if pct_change >= 0 else "🔴"
            pct_str = f"{sign} {pct_change:+.1f}%"
        else:
            pct_str = ""
        return pct_str

    def calculate_percentage(values):
        """Udregn percentvis ændring siden start af periode"""
        start_value = values[0]
        return [(v - start_value) / start_value * 100 for v in values]

    def add_fund_trace(fig, data, label, color, show_dividends=False, visible=False):
        dates = [item["date_obj"] for item in data]
        values = [item["nav"] for item in data]
        dividends = [item["dividend"] for item in data]
        values_pct = calculate_percentage(values)

        fill_color = None
        fill_mode = None
        if label == "PMINDI.CO":
            fill_mode = "tozeroy"
            fill_color = f"rgba(128, 0, 128, 0.3)"  # purple with 30% opacity

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values_pct,
                mode="lines",
                name=label,
                opacity=0.9,
                line=dict(color=color),
                fill=fill_mode,
                fillcolor=fill_color,
                visible=visible,
            )
        )
        if show_dividends:
            div_x = [d for d, div in zip(dates, dividends) if div > 0]
            div_y = [pct for pct, div in zip(values_pct, dividends) if div > 0]
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
                marker={"color": f"{color}", "size": 16, "symbol": "diamond"},
                visible=visible and show_dividends,
                hoverinfo="text",
            )
        )

    def setup_graph(pmindi_data, nasdaq_data, show_adjusted):
        time_labels = ["3M", "6M", "YTD", "12M", "24M", "MAX"]
        fig = go.Figure()

        for i, label in enumerate(time_labels):
            pm_filtered = filter_by_timespan(pmindi_data, label)
            ndx_filtered = filter_by_timespan(nasdaq_data, label)

            if show_adjusted:
                pm_adjusted = calculate_adjusted(pm_filtered)
                for j, adj in enumerate(pm_adjusted):
                    pm_filtered[j]["nav"] = adj

                add_fund_trace(
                    fig,
                    pm_filtered,
                    "PMINDI.CO",
                    "purple",
                    show_dividends=False,
                    visible=(label == "12M"),
                )
            else:
                add_fund_trace(
                    fig,
                    pm_filtered,
                    "PMINDI.CO",
                    "purple",
                    show_dividends=True,
                    visible=(label == "12M"),
                )
            add_fund_trace(
                fig,
                ndx_filtered,
                "NASDAQ",
                "green",
                show_dividends=False,
                visible=(label == "12M"),
            )

        return time_labels, fig

    time_labels, fig = setup_graph(pmindi_data, nasdaq_data, show_adjusted)

    buttons = []
    for i, label in enumerate(time_labels):
        TRACES_PER_LABEL = 4
        TOTAL_TRACES = len(time_labels) * TRACES_PER_LABEL
        visibility = [False] * TOTAL_TRACES
        base = i * TRACES_PER_LABEL
        visibility[base] = True
        visibility[base + 1] = True
        visibility[base + 2] = True
        visibility[base + 3] = True
        pct_str = calculate_rise(label)

        buttons.append(
            {
                "label": f"{label}\u00a0\u00a0{pct_str}",
                "method": "update",
                "args": [
                    {"visible": visibility},
                    {
                        "yaxis": {
                            "title": "Afkast i %",
                            "ticksuffix": "%",
                            "hoverformat": ".2f",
                        },
                    },
                ],
            }
        )

    fig.update_layout(
        updatemenus=[
            {
                "type": "buttons",
                "direction": "right",
                "x": 0.5,
                "y": -0.1,
                "showactive": True,
                "active": 3,
                "buttons": buttons,
                "pad": {
                    "t": 10,
                    "b": 10,
                    "l": 10,
                    "r": 10,
                },  # padding around whole button group
                "font": {"size": 18, "family": "verdana"},  # make buttons larger
                "xanchor": "center",
                "yanchor": "top",
                # optionally add spacing between buttons by adding spaces in labels
            },
        ],
        yaxis={"title": "Afkast i %", "ticksuffix": "%", "hoverformat": ".2f"},
        hovermode="x unified",
        legend={
            "orientation": "h",
            "x": 0.3,
            "y": 1.15,
            "xanchor": "left",
            "yanchor": "top",
            "bgcolor": "rgba(255,255,255,0.5)",
            "bordercolor": "gray",
            "borderwidth": 1,
        },
        width=1280,
        height=840,
        margin={"t": 140},
    )

    return fig


fig_regular = generate_graph(False)
fig_adjusted = generate_graph(True)

div_regular = to_html(
    fig_regular, full_html=False, include_plotlyjs="cdn", div_id="graph-regular"
)
div_adjusted = to_html(
    fig_adjusted, full_html=False, include_plotlyjs=False, div_id="graph-adjusted"
)

with open("regular.json", "w",encoding="UTF-8") as f:
    json.dump(fig_regular.to_plotly_json(), f, cls=PlotlyJSONEncoder)

with open("adjusted.json", "w",encoding="UTF-8") as f:
    json.dump(fig_adjusted.to_plotly_json(), f, cls=PlotlyJSONEncoder)
