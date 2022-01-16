import os
from datetime import datetime
from pydantic.dataclasses import dataclass
from typing import Optional
from typing_extensions import Self

from utils.api import Api
from utils.logger import logger as Logger


api = Api()
logger = Logger

@dataclass
class CMC():
    base_url: Optional[str] = None
    headers: Optional[dict] = None

    def __init__(self) -> None:
        base_url = os.getenv('CMC_API_ENDPOINT')
        api.setBaseUrl(base_url)

        headers = { 'X-CMC_PRO_API_KEY': os.getenv('CMC_API_KEY') }
        api.setHeaders(headers)

    async def get_ORE_price_USD(self) -> float:
        endpoint = '/v1/cryptocurrency/quotes/latest'
        params = {'slug': 'ore-network'}
        result = await api.makeCall('GET', endpoint, params, None)
        usd_price = float(result['data']['12743']['quote']['USD']['price'])
        return usd_price

cmc = CMC()

@dataclass
class OREPrice():
    price: Optional[float] = 0.0
    datetime: Optional[datetime] = None

    def set_price(self, new_price) -> None:
        self.price = new_price

    def set_datetime(self, new_datetime) -> None:
        self.datetime = new_datetime

    def check_expired(self) -> bool:
        time_diff = datetime.now() - self.datetime
        if time_diff.total_seconds() >= 60:
            return True
        else:
            return False

    async def update_price(self) -> Self:
        self.price = await cmc.get_ORE_price_USD()
        self.datetime = datetime.now()
        return self


