import asyncio
from modules import aiowlapi


class ItemInstance(object):
    def __init__(self, wialon, object_id):
        self.wialon = wialon
        self.object_id = object_id
        self.item = None
        self.object = None
        self.calc_last_msg = None
        self.pos_x = None
        self.pos_y = None

    async def set(self, flags):
        self.item = await self.wialon.search_item(self.object_id, flags)  # 5377
        self.object = self.item['item']
        self.calc_last_msg = await self.wialon.calc_last_message(self.object_id)
        self.pos_x = self.object['pos']['x'] if self.object['pos'] else None
        self.pos_y = self.object['pos']['y'] if self.object['pos'] else None

    def sensors_search_by_name(self, name):
        sensors = self.object['sens'] if self.object['sens'] else None
        return [sensors[i] for i in sensors if sensors[i]['n'] == name][0]


class CicadaInstance(ItemInstance):
    async def sens_update(self, sensors):
        ret = None
        svc = 'core/batch'
        payload = []
        for s_ in sensors:
            sensors[s_].update({
                "itemId": self.object['id'],
                "unlink": 0,
                "callMode": "create",
            })

            payload.append({
                'svc': 'unit/update_sensor',
                'params': cicada_sensors[s_]
            })

        if not self.object['sens']:
            ret = await self.wialon.request(svc, payload)

        if self.object['sens']:
            current = [self.object['sens'][s]['d'] for s in self.object['sens']
                       if self.object['sens'][s]['d'].startswith('cicada_tools_aс')]
            if not current:
                ret = await self.wialon.request(svc, payload)

        if ret:
            reset = [i[1] for i in ret if i[1]['n'] == 'reset_battery_value'][0]
            bat = [i[1] for i in ret if i[1]['n'] == 'Заряд аккумулятора'][0]
            alarm = [i[1] for i in ret if i[1]['n'] == 'Режим погони'][0]
            if reset:
                await self.set(5377)
                new_val = self.calc_last_msg[str(bat['id'] - 1)] // 1000 * 1000
                reset['p'] = f"const{new_val}"
                reset.update({
                    "itemId": self.object['id'],
                    "unlink": 0,
                    "callMode": "update",
                })
                await self.wialon.update_sensor(reset)
                svc = 'item/update_custom_property'
                params = {"itemId": self.object['id'],
                          "name": "monitoring_battery_id",
                          "value": bat['id']}
                await self.wialon.request(svc, params)
                params.update({"name": "monitoring_sensor_id", "value": alarm['id']})
                await self.wialon.request(svc, params)

    async def update_cmds(self):
        svc = 'unit/update_command_definition'
        payload = {"itemId": self.object['id'],
                   "id": 10,
                   "callMode": "create",
                   "n": "custom",
                   "c": "custom_msg",
                   "l": "vrt",
                   "p": "",
                   "a": 1}
        await self.wialon.request(svc, payload)

    async def exec_cmd(self, cmd):
        s = 'unit/exec_cmd'
        p = {"itemId": self.object['id'],
             "commandName": "custom",
             "linkType": cmd['t'],
             "param": cmd['p'],
             "timeout": 0,
             "flags": 0}
        exec = await self.wialon.request(s, p)
        return exec


class WiaTagInstance(ItemInstance):
    async def update_qr(self):
        pass


cicada_commands_list = [
    {'n': 'Интервал передачи 2ч.', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0213 120&saveparams',
     'jp': ''},
    {'n': 'Интервал передачи 4ч.', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0213 240&saveparams',
     'jp': ''},
    {'n': 'Интервал передачи 8ч.', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0213 480&saveparams',
     'jp': ''},
    {'n': 'Интервал передачи 1ч.', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0213 60&saveparams',
     'jp': ''},
    {'n': 'Интервал передачи 6ч.', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0213 360&saveparams',
     'jp': ''},
    {'n': 'Интервал передачи 12ч.', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0213 720&saveparams',
     'jp': ''},
    {'n': 'Интервал передачи 24ч.', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0213 1440&saveparams',
     'jp': ''},
    {'n': 'Интервал передачи 48ч.', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0213 2880&saveparams',
     'jp': ''},
    {'n': 'Включить режим погони', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0104 1&saveparams', 'jp': ''},
    {'n': 'Выключить режим погони', 'a': 1, 't': 'vrt', 'c': 'custom_msg', 'p': '&setparam 0104 0&saveparams',
     'jp': ''}]

cicada_sensors = {
    "1": {
        "id": 0,
        "n": "Интервал передачи",
        "t": "custom",
        "d": "cicada_tools_aс",
        "m": "ч.",
        "p": "par213/const60",
        "f": 0,
        "c": "{\"act\":1,\"appear_in_popup\":true,\"ci\":{},\"cm\":1,\"mu\":0,\"pos\":1,\"show_time\":false,\"text_params\":1,\"timeout\":0}",
        "vt": 0,
        "vs": 0,
        "tbl": []
    },
    "2": {
        "id": 0,
        "n": "Интервал в режиме погони",
        "t": "custom",
        "d": "cicada_tools_aс",
        "m": "мин.",
        "p": "par215",
        "f": 0,
        "c": "{\"act\":1,\"appear_in_popup\":true,\"ci\":{},\"cm\":1,\"mu\":0,\"pos\":2,\"show_time\":false,\"timeout\":0}",
        "vt": 0,
        "vs": 0,
        "tbl": []
    },
    "3": {
        "id": 0,
        "n": "Режим погони",
        "t": "digital",
        "d": "cicada_tools_aс",
        "m": "Вкл/Выкл",
        "p": "par104",
        "f": 0,
        "c": "{\"act\":1,\"appear_in_popup\":true,\"ci\":{\"0\":{\"c\":1669936},\"1\":{\"c\":16711680}},\"cm\":1,\"pos\":3,\"show_time\":false,\"timeout\":0}",
        "vt": 0,
        "vs": 0,
        "tbl": []
    },
    "4": {
        "id": 0,
        "n": "Выходов на связь",
        "t": "custom",
        "d": "cicada_tools_aс",
        "m": "",
        "p": "sens103",
        "f": 0,
        "c": "{\"act\":1,\"appear_in_popup\":true,\"ci\":{},\"cm\":1,\"mu\":0,\"pos\":4,\"show_time\":false,\"timeout\":0}",
        "vt": 0,
        "vs": 0,
        "tbl": []
    },
    "5": {
        "id": 0,
        "n": "Заряд аккумулятора",
        "t": "custom",
        "d": "cicada_tools_aс|-1:0:0:0:100:100:101:100",
        "m": "%",
        "p": "const100-(sens103-[reset_battery_value])/const10",
        "f": 0,
        "c": "{\"act\":0,\"appear_in_popup\":true,\"ci\":{},\"cm\":1,\"mu\":0,\"pos\":5,\"show_time\":false,\"timeout\":0,\"upper_bound\":101}",
        "vt": 0,
        "vs": 0,
        "tbl": [
            {
                "x": -1,
                "a": 0,
                "b": 0
            },
            {
                "x": 0,
                "a": 1,
                "b": 0
            },
            {
                "x": 100,
                "a": 0,
                "b": 100
            }
        ]
    },
    "6": {
        "id": 0,
        "n": "reset_battery_value",
        "t": "custom",
        "d": "cicada_tools_aс",
        "m": "",
        "p": "const1000",
        "f": 0,
        "c": "{\"act\":0,\"appear_in_popup\":false,\"ci\":{},\"cm\":1,\"mu\":0,\"pos\":6,\"show_time\":false,\"timeout\":0}",
        "vt": 0,
        "vs": 0,
        "tbl": []
    }
}
