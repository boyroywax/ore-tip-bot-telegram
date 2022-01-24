
import os
from pydantic.dataclasses import dataclass
from typing import Optional

from utils.api import Api


@dataclass
class Pinata():
    pinata_api: Optional[Api] = None
    pinata_api_key: Optional[str] = os.getenv('PINATA_API_KEY')
    pinata_secret_api_key: Optional[str] = os.getenv('PINATA_SECRET_API_KEY')

    def __init__(self):
        self.pinata_api = Api()
        self.pinata_api.set_base_url('https://api.pinata.cloud/')
        self.pinata_api.set_headers({
            'pinata_api_key': self.pinata_api_key,
            'pinata_secret_api_key': self.pinata_secret_api_key
        })

    async def get_access_token(self):
        body = {
            'keyName': 'Example Key',
            'permissions': {
                'endpoints': {
                    'data': {
                        'userPinnedDataTotal': True
                    },
                    'pinning': {
                        'pinJobs': True,
                        'unpin': True,
                        'userPinPolicy': True
                    }
                }
            }
        }
        endpoint = 'users/generateApiKey'
        kwargs = {'endpoint': endpoint, 'data': body}
        return await self.pinata_api.make_call('POST', **kwargs)

    async def upload_file(self, file):
        endpoint = 'pinning/pinFileToIPFS'
        name = file
        # data = {'file': file, 'keyvalues': key_values}
        data = {"file": file}
        kwargs = {"endpoint": endpoint, "data": data}
        result = await self.pinata_api.make_call('POST', **kwargs)
        return result
