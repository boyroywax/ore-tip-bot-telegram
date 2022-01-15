import os
from utils.api import Api
from typing import Optional

api = Api()

class CMCApi(Api):
    base_url: Optional[str] = None
    headers: Optional[dict] = None

    async def start_api(self):
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


