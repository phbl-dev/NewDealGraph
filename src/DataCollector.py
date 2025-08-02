from datetime import date
from typing import List
import requests
import yfinance as yf

from src.FundReturn import FundReturn


class DataCollector:

    @staticmethod
    def get_data_mf(fund_id: str) -> List[FundReturn]:
        """Hent data omkring fonde understøttet af FundMarket"""
        url = f"https://node-api.fundmarket.dk/funds/ninfo/{fund_id}"
        response = requests.get(url, timeout=1000)
        data = response.json()["returns"]

        return data

    @staticmethod
    def get_data_yf(fund_id: str) -> List[FundReturn]:
        """Hent data omkring fonde understøttet af yfinance API"""
        data = yf.Ticker(fund_id).history(
            start="2023-9-22", end=str(date.today()), actions=True
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
