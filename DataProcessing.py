from datetime import date, datetime
from typing import List
from FundReturn import FundReturn
from dateutil.relativedelta import relativedelta


class DataProcessing:
    @staticmethod
    def calculate_percentage(values):
        """Udregn percentvis ændring siden start af periode"""
        start_value = values[0]
        return [(v - start_value) / start_value * 100 for v in values]

    @staticmethod
    def calculate_rise(label, data: List[FundReturn]):
        print(f"calculate_rise called with data type: {type(data)}")

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
        print(f"filter_by_timespan called with data type: {type(data)}")
        for item in data:
            print(item)
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
        # TODO: Find korrekt formel for dette?
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
