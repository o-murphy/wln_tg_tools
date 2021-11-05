import aiohttp
import asyncio
from asyncio import sleep
import json

import logging

logging.basicConfig()
wialon_logger = logging.getLogger('wialon')
wialon_logger.setLevel(logging.INFO)

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


class WLN(object):
    """
    init of WLN object make request to login and get session
    """

    def __init__(self, host, token, user=''):
        self.host = host
        self.token = token
        self.user = user
        self.sid = None
        self.error = None

    async def session_update(self):
        await self.login()
        while True:
            avl_evts = await self.avl_evts()
            if 'error' in avl_evts:
                wialon_logger.warning('Session closed. Trying to open session')
                await self.login()
            await asyncio.sleep(60)

    async def update_sid(self, response_data):
        if response_data['error'] == 1:
            await self.login()

    async def login(self):
        url = '{}/wialon/ajax.html'.format(self.host)
        payload = {
            'svc': 'token/login',
            'params': json.dumps({'token': self.token, 'operateAs': self.user})
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=HEADERS) as response:
                response_data = await response.json()
                wialon_logger.info('Login {}, {}, [{}]'.format(response.url, payload['svc'], response.status))
                if 'error' in response_data:
                    self.error = response_data['error']
                    self.sid = None
                    wialon_logger.error('LOGIN ERROR: {error}'.format(**response_data))
                else:
                    self.sid = response_data['eid']
                    self.error = None
                    wialon_logger.info('LOGIN SUCSESS')
                return response_data

    async def login_by_hash(self, access_hash):
        url = '{}/wialon/ajax.html'.format(self.host)
        payload = {
            'svc': 'core/use_auth_hash',
            'params': json.dumps({'authHash': access_hash})
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=HEADERS) as response:
                response_data = await response.json()
                wialon_logger.info('UseHash {}, {}, [{}]'.format(response.url, payload['svc'], response.status))

                if 'error' in response_data:
                    self.error = response_data['error']
                    wialon_logger.error('HASH ERROR: {error}'.format(**response_data))
                else:
                    self.sid = response_data['eid']
                    self.error = None
                return response_data

    async def request(self, svc, params=None):
        url = '{}/wialon/ajax.html'.format(self.host)
        payload = {
            'sid': self.sid,
            'svc': svc,
            'params': json.dumps(params)
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=HEADERS) as response:
                response_data = await response.json()
                wialon_logger.info('Request {}, {}, [{}]'.format(url, svc, response.status))
                if 'error' in response_data:
                    self.error = response_data['error']
                    wialon_logger.error('REQUEST ERROR: {error}'.format(**response_data))
                else:
                    self.error = None
                return response_data

    async def avl_evts(self):
        url = '{}/avl_evts'.format(self.host)
        payload = {'sid': self.sid}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=HEADERS) as response:
                response_data = await response.json()
                wialon_logger.info('Request {}, [{}], {}'.format(url, response.status, response_data))
            if 'error' in response_data:
                self.error = response_data['error']
                wialon_logger.error('REQUEST ERROR: {error}'.format(**response_data))
            else:
                self.error = None
            return response_data

    async def get_hw_types(self, ft='name', fv: list = None, include=True, ignore=True):
        """
        :param ft: "filterType": name, id, type (default: name)
        :param fv: "filterValue": list of values (if ft == type: values must be in ["auto", "tracker", "mobile", "soft"])
        :param include: "includeType" default True
        :param ignore: "ignoreRename" default True
        :return:
        """

        s = 'core/get_hw_types'
        p = {
            "filterType": ft,
            "filterValue": fv,
            "includeType": include,
            "ignoreRename": ignore
        }
        response = await self.request(s, p)
        return response

    async def search_items(self, **kwargs):
        s = "core/search_items"
        p = {
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_name",
                "propValueMask": "*",
                "sortType": "sys_name",
                "propType": ""
            },
            "force": 1,
            "flags": 5377,
            "from": 0,
            "to": 0
        }

        for i in kwargs:
            if isinstance(p[i], dict):
                p[i].update(kwargs[i])
            else:
                p.update({i: kwargs[i]})
        response = await self.request(s, p)
        return response

    async def search_item(self, object_id=None, flags=257):
        s = 'core/search_item'
        p = {"id": object_id, "flags": flags}
        response = await self.request(s, p)
        return response

    def sensors_search_by_name(self, instance, name):
        sensors = instance['sens']
        return [sensors[i] for i in sensors if sensors[i]['n'] == name]

    async def check_updates(self):
        s = 'events/check_updates'
        p = {'detalization': 3}
        updates = await self.request(s, p)
        return updates

    async def calc_last_message(self, object_id=None):
        s = 'unit/calc_last_message'
        p = {"unitId": object_id}
        calculated_last_message = await self.request(s, p)
        return calculated_last_message

    async def update_sensor(self, params):
        s = 'unit/update_sensor'
        updated_sensor = await self.request(s, params)
        return updated_sensor

    async def create_locator_token(self, object_ids: list = None, **kwargs):
        s = 'token/update'
        p = {"callMode": 'create',
             "h": 'locator',
             "app": 'locator',
             "at": 0,
             "dur": 86400,
             "fl": 256,
             "p": "{\"note\":\"\",\"zones\":1,\"tracks\":1,\"sensorMasks\":[\"*\"]}",
             "items": object_ids}
        p.update(kwargs)
        locator_token = await self.request(s, p)
        return locator_token

    async def exec_cmd(self, object_id, cmd):
        s = 'unit/exec_cmd'
        p = {"itemId": object_id,
             "commandName": cmd['n'],
             "linkType": cmd['t'],
             "param": cmd['p'],
             "timeout": 0,
             "flags": 0}
        print(p)
        exec = await self.request(s, p)
        return exec

    async def token_update(self, **kwargs):
        s = 'token/update'
        p = {"callMode": 'create',
             "h": 'TelegramBotAuth',
             "app": 'TelegramBotAuth',
             "at": 0,
             "dur": 86400,
             "fl": -1,
             "p": "{}"}
        p.update(kwargs)
        token = await self.request(s, p)
        return token
