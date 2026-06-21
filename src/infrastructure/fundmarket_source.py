from typing import List

import requests

from src.domain.fund_data_source import FundDataSource
from src.domain.fund_return import FundReturn


class FundMarketDataSource(FundDataSource):
    """Fetches NAV + dividend history from the FundMarket node API."""

    _BASE_URL = "https://node-api.fundmarket.dk/funds/ninfo"

    def __init__(self, timeout: int = 60) -> None:
        self._timeout = timeout

    def fetch(self, fund_id: str) -> List[FundReturn]:
        url = f"{self._BASE_URL}/{fund_id}"
        response = requests.get(url, timeout=self._timeout)
        response.raise_for_status()
        return response.json()["returns"]
