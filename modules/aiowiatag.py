import aiohttp
import asyncio


class WiaTag(object):
    def __init__(self):
        self.link = None
        self.png = None

    async def get_link(self, **kwargs):
        payload = {'mode': 1,
                   'pass': None,
                   'uid': None,
                   'host': '193.193.165.165',
                   'port': 20963,
                   'remoteControl': 1,
                   'adminPassword': None,
                   'bleid': None}
        url = 'https://wiatag.com/genqr?' + '&'.join([f'{i}={payload[i]}' for i in payload])
        payload.update(kwargs)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ) as response:
                text = await response.text()
                self.link = f'https://wiatag.com/l/{text}'

    async def get_qr(self):
        url = f'https://api.qrserver.com/v1/create-qr-code/?format=png&data={self.link}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ) as response:
                png = await response.read()
                self.png = png
