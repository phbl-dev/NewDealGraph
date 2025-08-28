from datetime import date, datetime
from typing import List
from src.FundReturn import FundReturn
from dateutil.relativedelta import relativedelta


class DataProcessing:
    @staticmethod
    def calculate_percentage(values):
        """Udregn percentvis ændring siden start af periode"""
        start_value = values[0]
        return [(v - start_value) / start_value * 100 for v in values]

    @staticmethod
    def calculate_rise(data: List[FundReturn]):
        if data:
            start_val = data[0]["nav"]
            end_val = data[-1]["nav"]
            pct_change = (end_val - start_val) / start_val * 100
            sign = "🟢" if pct_change >= 0 else "🔴"
            pct_str = f"{sign} {pct_change:+.1f}%"
        else:
            pct_str = ""
        return pct_str

    @staticmethod
    def filter_by_timespan(data: List[FundReturn], timespan: str):
        """
        Filtrering af data med måneder. Måneder angives i hele tal og afsluttes med "M".
        F.eks. vil man skrive "6M", hvis man skal bruge 6 måneder.
        """
        today = date.today()
        for item in data:
            item["date_obj"] = datetime.strptime(item["org_date"], "%Y-%m-%d").date()

        t = timespan.upper()
        if t.endswith("M"):
            months = int(t[:-1])
            cutoff = today - relativedelta(months=months)
        elif t == "YTD":
            cutoff = date(today.year, 1, 1)
        else:
            cutoff = date.min

        return [item for item in data if item["date_obj"] >= cutoff]

    @staticmethod
    def calculate_adjusted(data):
        """
        Calculate adjusted close including dividends.

        - Forward approach until first dividend > 0.
        - After first dividend, use hardcoded formula: adjusted_nav = nav / 0.768
        """

        if not data:
            return []
        print(data)
        adjusted = []
        first_dividend_found = False

        for _, point in enumerate(data):
            nav = point.get("nav", 0) or 0
            dividend = point.get("dividend", 0) or 0
            VALUE = 0.786   
            if not first_dividend_found and dividend > 0:
                first_dividend_found = True
            adjusted.append(nav / VALUE if first_dividend_found else nav)
        return adjusted

