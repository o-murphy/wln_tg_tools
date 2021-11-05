import requests
import json

HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}


def request(host, svc, params, eid):
    url = f'{host}/wialon/ajax.html?svc={svc}&sid={eid}'
    data = f'&params={json.dumps(params)}'
    r = requests.post(url=url, data=data.encode('utf-8'), headers=HEADERS)
    # print(url + str(data))
    return r.json()


def login(host, token, user=''):
    params = {'token': token, 'operateAs': user}
    url = f'{host}/wialon/ajax.html?svc=token/login'
    data = f'&params={json.dumps(params)}'
    # print(url+str(data))
    r = requests.post(url=url, data=data.encode('utf-8'), headers=HEADERS)
    return r.json()


def avl_evts(host, eid):
    r = request(host, svc='avl_evts', params={}, eid=eid)
    return r.json


PARAMS = {
    "core/search_items": {
        "spec": {
            "itemsType": "avl_unit_group",
            "propName": "sys_name",
            "propValueMask": "*",
            "sortType": "sys_name",
            "propType": ""
        },
        "force": 1,
        "flags": 1,
        "from": 0,
        "to": 0
    },
    'unit_group/update_units': {"itemId": 0, "units": []},
    'core/search_item': {"id": 0, "flags": 1},
    'core/get_hw_types': {
        "filterType": "name",
        "filterValue": [],
        "includeType": True,
        "ignoreRename": True
    }
}
