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
    latest_result: Optional[dict] = None
    result_datetime: Optional[datetime] = None

    def __init__(self) -> None:
        base_url = os.getenv('CMC_API_ENDPOINT')
        api.setBaseUrl(base_url)

        headers = { 'X-CMC_PRO_API_KEY': os.getenv('CMC_API_KEY'), 'Content-Type': 'application/json' }
        api.setHeaders(headers)

    def check_expired(self) -> bool:
        if (self.result_datetime is None):
            return True
        
        time_diff = datetime.now() - self.result_datetime
        if (time_diff.total_seconds() >= 60):
            return True
        else:
            return False

    async def get_ORE_price_info(self) -> dict:
        if self.check_expired():
            endpoint = '/v1/cryptocurrency/quotes/latest'
            params = {'slug': 'ore-network'}
            kwargs = {"endpoint": endpoint, "params": params}
            self.latest_result = await api.makeCall('GET', **kwargs)
            self.result_datetime = datetime.now()
        
        return self.latest_result

    async def get_ORE_price_USD(self) -> float:
        result = await self.get_ORE_price_info()
        usd_price = float(result['data']['12743']['quote']['USD']['price'])
        logger.debug(f'result: {result}')
        return usd_price

    async def get_ORE_24h_volume(self):
        result = await self.get_ORE_price_info()
        volume_24h = float(result['data']['12743']['quote']['USD']['volume_24h'])
        logger.debug(f'volume (24h) info: {volume_24h}')
        return volume_24h

    async def get_ORE_24h_price_change(self):
        result = await self.get_ORE_price_info()
        percent_change_24h = float(result['data']['12743']['quote']['USD']['percent_change_24h'])
        logger.debug(f'percent change (24h) info: {percent_change_24h}')
        return percent_change_24h

cmc = CMC()

@dataclass
class OREPrice():
    price: Optional[float] = 0.0
    volume_24h: Optional[float] = 0.0
    price_change_24h: Optional[float] = 0.0
    datetime: Optional[datetime] = None

    def __init__(self) -> None:
        self.datetime = datetime.now()

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
        self.volume_24h = await cmc.get_ORE_24h_volume()
        self.price_change_24h = await cmc.get_ORE_24h_price_change()
        self.datetime = datetime.now()
        return self
