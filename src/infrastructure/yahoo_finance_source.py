from datetime import date
from typing import List

import yfinance as yf

from src.domain.fund_data_source import FundDataSource
from src.domain.fund_return import FundReturn


class YahooFinanceDataSource(FundDataSource):
    """Fetches OHLCV + dividend history from Yahoo Finance via yfinance."""

    def __init__(self, start_date: str = "2023-09-22") -> None:
        self._start_date = start_date

    def fetch(self, fund_id: str) -> List[FundReturn]:
        data = yf.download(
            fund_id,
            start=self._start_date,
            end=str(date.today()),
            auto_adjust=False,
            actions=True,
        )

        data = data.reset_index()
        # Flatten MultiIndex columns (e.g. ("Close", "QQQ") → "Close_QQQ")
        data.columns = [
            "_".join(col).strip() if isinstance(col, tuple) else col
            for col in data.columns
        ]

        return [
            FundReturn(
                org_date=row["Date_"].date().isoformat(),
                nav=row[f"Close_{fund_id}"],
                dividend=row[f"Dividends_{fund_id}"],
                value=row[f"Close_{fund_id}"],
                adjusted=row[f"Adj Close_{fund_id}"],
            )
            for _, row in data.iterrows()
        ]
