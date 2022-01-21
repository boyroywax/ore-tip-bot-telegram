import aiohttp
import json
import os

from aiohttp.helpers import BasicAuth
from utils.logger import logger as Logger
from typing import Optional

from pydantic.dataclasses import dataclass

logger = Logger


@dataclass
class Api:
    baseUrl: Optional[str] = None
    headers: Optional[dict or json] = None
    auth: Optional[BasicAuth] = None

    # def __init__(self):
    #     """ Declare base url and headers for standard oreid interaction
    #     """
    #     self.baseUrl = os.getenv('API_URL')
    #     self.headers = {
    #         'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
    #                        'AppleWebKit/537.36 (KHTML, like Gecko) '
    #                        'Chrome/45.0.2454.101 Safari/537.36'),
    #         'api-key': os.getenv('API_KEY'),
    #         'app_id': os.getenv('API_ID'),
    #         'Content-Type': 'application/json'
    #     }

    def setBaseUrl(self, newBaseUrl):
        self.baseUrl = newBaseUrl

    def setHeaders(self, newHeaders):
        self.headers = newHeaders

    def setAuth(self, auth_user, auth_pass):
        self.auth = aiohttp.BasicAuth(auth_user, auth_pass)

    async def returnResponse(self, resp):
        if resp.status == 200 or resp.status == 201:
            try:
                return await resp.json()
            except Exception as exc:
                return f'{await resp.text()} - {exc}'
        else:
            return {'status': resp.status, 'message': await resp.text()}

    async def makeCall(self, method, **kwargs) -> dict:
        for arg in kwargs:
            match arg:
                case 'endpoint':
                    endpoint = kwargs[arg]
                case 'params':
                    params = kwargs[arg]
                case 'data':
                    data = kwargs[arg]

        if endpoint is None:
            url = self.baseUrl
        else:
            url = f'{self.baseUrl}{endpoint}'
        logger.debug(f'API endpoint called: {url}')

        # GET
        if method == 'GET':
            # PARAMS PASSED
            if params is not None:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers=self.headers,
                        params=params
                    ) as resp:
                        return await self.returnResponse(resp)
            # NO PARAMS PASSED
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers=self.headers
                    ) as resp:
                        return await self.returnResponse(resp)
        # POST
        elif method == 'POST':
            async with aiohttp.ClientSession() as session:
                if self.auth is not None:
                    async with session.request(
                        'POST',
                        url,
                        json=data,
                        headers=self.headers,
                        auth=self.auth
                    ) as resp:
                        return await self.returnResponse(resp)
                else:
                    async with session.request(
                        'POST',
                        url,
                        json=data,
                        headers=self.headers
                    ) as resp:
                        return await self.returnResponse(resp)
        # PUT
        elif method == 'PUT':
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    url,
                    json=data,
                    headers=self.headers
                ) as resp:
                    return await self.returnResponse(resp)
        # INCORRECT METHOD
        else:
            logger.error(f'An incorrect method was passed to Api class - {method}')
