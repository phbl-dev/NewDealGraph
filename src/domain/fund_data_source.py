from abc import ABC, abstractmethod
from typing import List

from src.domain.fund_return import FundReturn


class FundDataSource(ABC):
    """Abstract contract for fetching fund price/dividend history."""

    @abstractmethod
    def fetch(self, fund_id: str) -> List[FundReturn]:
        """Return a list of FundReturn records for the given fund identifier."""
        ...
