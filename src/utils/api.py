import aiohttp
import json
# import os
from aiohttp.helpers import BasicAuth
from typing import Optional
from pydantic.dataclasses import dataclass

from utils.logger import logger as Logger

logger = Logger


@dataclass
class Api:
    base_url: Optional[str] = None
    headers: Optional[dict or json] = None
    auth: Optional[BasicAuth] = None

    def set_base_url(self, new_base_url):
        self.base_url = new_base_url

    def set_headers(self, new_headers):
        self.headers = new_headers

    def set_auth(self, auth_user, auth_pass):
        self.auth = aiohttp.BasicAuth(auth_user, auth_pass)

    async def return_response(self, resp):
        if resp.status == 200 or resp.status == 201:
            try:
                return await resp.json()
            except Exception as exc:
                return f'{await resp.text()} - {exc}'
        else:
            return {'status': resp.status, 'message': await resp.text()}

    async def make_call(self, method, **kwargs) -> dict:
        for arg in kwargs:
            match arg:
                case 'endpoint':
                    endpoint = kwargs[arg]
                case 'params':
                    params = kwargs[arg]
                case 'data':
                    data = kwargs[arg]

        if endpoint is None:
            url = self.base_url
        else:
            url = f'{self.base_url}{endpoint}'
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
                        return await self.return_response(resp)
            # NO PARAMS PASSED
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        headers=self.headers
                    ) as resp:
                        return await self.return_response(resp)
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
                        return await self.return_response(resp)
                else:
                    async with session.request(
                        'POST',
                        url,
                        json=data,
                        headers=self.headers
                    ) as resp:
                        return await self.return_response(resp)
        # PUT
        elif method == 'PUT':
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    url,
                    json=data,
                    headers=self.headers
                ) as resp:
                    return await self.return_response(resp)
        # INCORRECT METHOD
        else:
            logger.error(f'An incorrect method was passed to Api class - {method}')
