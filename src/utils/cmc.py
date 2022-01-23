import os
from datetime import datetime
from pydantic.dataclasses import dataclass
from typing import Optional
from typing_extensions import Self

from utils.api import Api
from utils.logger import logger as Logger

logger = Logger
RESET_TIME = float(os.getenv('CMC_API_RESET_TIME'))


@dataclass
class CMC():
    latest_result: Optional[dict] = None
    result_datetime: Optional[datetime] = None
    api: Optional[Api] = None

    def __init__(self) -> None:
        self.api = Api()
        base_url = os.getenv('CMC_API_ENDPOINT')
        self.api.set_base_url(base_url)

        headers = {
            'X-CMC_PRO_API_KEY': os.getenv('CMC_API_KEY'),
            'Content-Type': 'application/json'
        }
        self.api.set_headers(headers)

    def check_expired(self) -> bool:
        if (self.result_datetime is None):
            return True

        time_diff = datetime.now() - self.result_datetime
        if (time_diff.total_seconds() >= RESET_TIME):
            return True
        else:
            return False

    async def get_ORE_price_info(self) -> dict:
        if self.check_expired():
            endpoint = '/v1/cryptocurrency/quotes/latest'
            params = {'slug': 'ore-network'}
            kwargs = {"endpoint": endpoint, "params": params}
            self.latest_result = await self.api.make_call('GET', **kwargs)
            self.result_datetime = datetime.now()

        return self.latest_result

    async def get_ORE_price_USD(self) -> float:
        result = await self.get_ORE_price_info()
        usd_price = float(result['data']['12743']['quote']['USD']['price'])
        logger.debug(f'result: {result}')
        return usd_price

    async def get_ORE_24h_volume(self) -> float:
        result = await self.get_ORE_price_info()
        volume_24h = float(
            result['data']['12743']['quote']['USD']['volume_24h']
        )
        logger.debug(f'volume (24h) info: {volume_24h}')
        return volume_24h

    async def get_ORE_24h_price_change(self) -> float:
        result = await self.get_ORE_price_info()
        percent_change_24h = float(
            result['data']['12743']['quote']['USD']['percent_change_24h']
        )
        logger.debug(f'percent change (24h) info: {percent_change_24h}')
        return percent_change_24h


@dataclass
class OREPrice():
    price: Optional[float] = 0.0
    volume_24h: Optional[float] = 0.0
    price_change_24h: Optional[float] = 0.0
    datetime: Optional[datetime] = None
    cmc: Optional[CMC] = None

    def __init__(self) -> None:
        self.cmc = CMC()
        self.datetime = datetime.now()

    def set_price(self, new_price) -> None:
        self.price = new_price

    def set_datetime(self, new_datetime) -> None:
        self.datetime = new_datetime

    def check_expired(self) -> bool:
        time_diff = datetime.now() - self.datetime
        if time_diff.total_seconds() >= RESET_TIME:
            return True
        else:
            return False

    async def update_price(self) -> Self:
        self.price = await self.cmc.get_ORE_price_USD()
        self.volume_24h = await self.cmc.get_ORE_24h_volume()
        self.price_change_24h = await self.cmc.get_ORE_24h_price_change()
        self.datetime = datetime.now()
        return self
