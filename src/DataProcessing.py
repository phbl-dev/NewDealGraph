from datetime import date, datetime
import math
from typing import List
from dateutil.relativedelta import relativedelta
from src.FundReturn import FundReturn

    
DIVIDEND_FACTORS = [
        0.786,
        0.782
    ]
    

class DataProcessing:
    
    @staticmethod
    def calculate_percentage(values):
        """Udregn percentvis ændring siden start af periode"""
        start_value = values[0]
        return [(v - start_value) / start_value * 100 for v in values]

    @staticmethod
    def calculate_adjusted(data):
        """
        Calculate adjusted close including dividends.

        - Forward approach until first dividend > 0.
        """

        if not data:
            return []
        adjusted = []
        
        cumulative_factor = 1.0
        dividend_index = 0
        
        for _, point in enumerate(data):
            nav = point.get("nav", 0) or 0
            dividend = point.get("dividend", 0) or 0
            
            if dividend > 0 and dividend_index < len(DIVIDEND_FACTORS):
                cumulative_factor *= DIVIDEND_FACTORS[dividend_index]
            
            adjusted.append(nav / cumulative_factor)

        return adjusted
    
    
    @staticmethod
    def calculate_yaxis_range(
        datasource_one: List[FundReturn],
        datasource_two: List[FundReturn],
        show_adjusted: bool,
    ) -> tuple[float, float]:
        """
        Calculate y-axis range consistent with how add_graph
        transforms data.
        """
        if not datasource_one or not datasource_two:
            return 0, 0

        # PMINDI
        if show_adjusted:
            pm_adjusted = DataProcessing.calculate_adjusted(datasource_one)
            pm_plot = list(pm_adjusted)
        else:
            pm_plot = [p["nav"] for p in datasource_one]

        # Starting point for alignment
        pmindi_start_value = pm_plot[0]

        # NASDAQ
        if show_adjusted:
            ndx_plot = [p["adjusted"] for p in datasource_two]
        else:
            ndx_plot = [p["nav"] for p in datasource_two]

        ndx_pct = DataProcessing.calculate_percentage(ndx_plot)
        ndx_pct_offset = [pct + pmindi_start_value for pct in ndx_pct]

        # Collect values actually shown
        values = pm_plot + ndx_pct_offset

        ymin = math.floor(min(values) * 0.9)
        ymax = math.ceil(max(values) * 1.1)

        return ymin, ymax


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
            cutoff = date(today.year, 1, 1) - relativedelta(days=1)
        else:
            cutoff = date.min

        return [item for item in data if item["date_obj"] >= cutoff]

    
