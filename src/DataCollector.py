from datetime import date
from typing import List
import requests
import yfinance as yf

from src.FundReturn import FundReturn


class DataCollector:

    @staticmethod
    def get_data_mf(fund_id: str) -> List[FundReturn]:
        """Hent data omkring fonde understøttet af FundMarket"""
        try:
            url = f"https://node-api.fundmarket.dk/funds/ninfo/{fund_id}"
            response = requests.get(url, timeout=1000)
            data = response.json()["returns"]
            
            print(data)
            return data
        except TimeoutError:
            return None

    @staticmethod
    def get_data_yf(fund_id: str) -> List[FundReturn]:
        """Hent data omkring fonde understøttet af yfinance API"""
        data = yf.download(
            fund_id,
            start="2023-9-22",
            end=str(date.today()),
            auto_adjust=False,
            actions=True,
        )

        data = data.reset_index()
        data.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in data.columns]
        nasdaq_cleaned = [
            {
                "org_date": row["Date_"].date().isoformat(),  # giver "2023-09-22"
                "nav": row["Close_QQQ"],
                "dividend": row["Dividends_QQQ"],
                "value": row["Close_QQQ"],
                "adjusted": row["Adj Close_QQQ"],
            }
            for _, row in data.iterrows()
        ]

        return nasdaq_cleaned
