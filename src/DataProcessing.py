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
    def calculate_rise(label, data: List[FundReturn]):
        pm_filtered = DataProcessing.filter_by_timespan(data, label)
        if pm_filtered:
            start_val = pm_filtered[0]["nav"]
            end_val = pm_filtered[-1]["nav"]
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
        """Calculate adjusted close including dividends (forward approach)"""
        if not data:
            return []

        dividend = 0
        adjusted = []
        for point in data:
            nav = point.get("nav", 0) or 0
            if point.get("dividend", 0) > 0:
                dividend = point.get("dividend", 0)
            adjusted.append(nav + dividend)
        return adjusted
