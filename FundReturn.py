from typing import TypedDict

class FundReturn(TypedDict):
    """Interface klasse, så det er lettere at arbejde med data"""

    org_date: str
    nav: float
    dividend: float
    value: float