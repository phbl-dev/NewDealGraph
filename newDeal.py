from typing import List, TypedDict
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
import requests
import yfinance as yf


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
    return response.json()["returns"]


def get_data_yf(fund_id) -> List[FundReturn]:
    """Hent data omkring fonde understøttet af yfinance API"""
    data = yf.Ticker(fund_id).history(
        start="2020-01-01", end=str(date.today()), actions=True
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
    """Udregn adjusted close"""
    if not data:
        return []

    adjusted = [data[0]["nav"]]
    for k in range(1, len(data)):
        prev_adj = adjusted[-1]
        nav_today = data[k]["nav"]
        nav_yesterday = data[k - 1]["nav"]
        dividend = data[k]["dividend"]
        new_adj = prev_adj * (nav_today / nav_yesterday) + dividend
        adjusted.append(new_adj)

    return adjusted


def calculate_percentage(values):
    """Udregn percentvis ændring siden start af periode"""
    start_value = values[0]
    return [(v - start_value) / start_value * 100 for v in values]


def add_fund_trace(fig, data, label, color, show_dividends=False, visible=False):
    '''Tilføjer data til graf'''
    dates = [item["date_obj"] for item in data]
    values = [item["value"] for item in data]
    dividends = [item["dividend"] for item in data]

    values_pct = calculate_percentage(values)

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=values_pct,
            mode="lines",
            name=label,
            opacity=0.9,
            line=dict(color=color),
            visible=visible,
        )
    )

    if show_dividends:
        # Dividend markers for PMINDI
        fig.add_trace(
            go.Scatter(
                x=[d for d, div in zip(dates, dividends) if div > 0],
                y=[pct for pct, div in zip(values_pct, dividends) if div > 0],
                text=[f"{div:.2f} DKK" for div in dividends if div > 0],
                mode="markers",
                textposition="top center",
                name=f"{label} Udbytte",
                marker={"color": f"{color}", "size": 16, "symbol": "diamond"},
                visible=visible,
                hoverinfo="text",
            )
        )


# ---- Data Preparation ----

pmindi_data = get_data_mf(1198)
nasdaq_data = get_data_yf("QQQ")

time_labels = ["3M", "6M", "YTD", "12M", "36M"]
fig = go.Figure()

# ---- Add traces for each timespan ----
for i, label in enumerate(time_labels):
    pm_filtered = filter_by_timespan(pmindi_data, label)
    ndx_filtered = filter_by_timespan(nasdaq_data, label)

    # Compute adjusted and set "value" field
    pm_adjusted = calculate_adjusted(pm_filtered)
    for j, adj in enumerate(pm_adjusted):
        pm_filtered[j]["value"] = adj

    ndx_adjusted = calculate_adjusted(ndx_filtered)
    for j, adj in enumerate(ndx_adjusted):
        ndx_filtered[j]["value"] = adj

    add_fund_trace(
        fig,
        pm_filtered,
        "PMINDI.CO",
        "purple",
        show_dividends=True,
        visible=(label == "6M"),
    )
    add_fund_trace(
        fig,
        ndx_filtered,
        "NASDAQ",
        "green",
        show_dividends=True,
        visible=(label == "6M"),
    )


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

    months = label.split("M")[0]

    buttons.append(
        {
            "label": label,
            "method": "update",
            "args": [
                {"visible": visibility},
                {
                    "title": f"PMINDI.CO vs NASDAQ ({label})",
                    "xaxis": {"title": f"Periode: {months} Måneder"},
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
            "type": "dropdown",
            "direction": "right",
            "x": 0,
            "y": 1.1,
            "showactive": True,
            "active": 1,
            "buttons": buttons,
            "xanchor": "left",
            "yanchor": "top",
        }
    ],
    title="PMINDI.CO vs NASDAQ (6M)",
    xaxis_title="Periode: 6 Måneder",
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



fig.write_html("output/fund_performance.html", include_plotlyjs="cdn") #To output as HTML
