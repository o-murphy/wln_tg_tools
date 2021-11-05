import asyncio
import re
from datetime import datetime
import json


from main import dp, types, bot_logger, db, WLN, WLN_HOST, WIALON, wrong_token, wrong_sid, wln_auth_succeed
from keyboards import keyboards as kb

from modules.item_instance import CicadaInstance, cicada_sensors, cicada_commands_list


async def search_cicadas(wialon):
    types = await wialon.get_hw_types(fv=['Bitrek BI 310'])
    type_id = types[0]['id']
    list_search_instance = await wialon.search_items(spec={
        "propName": 'rel_hw_type_id,sys_name',
        "propValueMask": f'{type_id},*'
    })
    return list_search_instance['items']


def sensors_search_by_name(instance, name):
    sensors = instance['sens'] if instance['sens'] else None
    return [sensors[s] for s in sensors if sensors[s]['n'] == name][0]


async def calculate(wialon, instance):
    if instance['sens']:
        try:
            charge = sensors_search_by_name(instance, 'Заряд аккумулятора')
            last_msg = await wialon.calc_last_message(instance['id'])
            instance['last_charge'] = last_msg[str(charge['id'])]
            # print(charge['id'], last_msg[str(charge['id'])])
        except IndexError:
            instance['last_charge'] = None
    else:
        instance['last_charge'] = None
    return instance


@dp.callback_query_handler(lambda call: call.data == 'cicada')
async def cicada_all(call: types.CallbackQuery):
    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:
            await wln_auth_succeed(call.message)
            cicadas = await search_cicadas(wialon)

            await asyncio.gather(*[calculate(wialon, instance) for instance in cicadas])

            await call.message.edit_reply_markup(kb.cicadas(cicadas))

        else:
            await wrong_sid(call.message)
    else:
        await wrong_token(call.message)
    await call.answer()


@dp.callback_query_handler(lambda call: re.search(r'^cicada/\d+/reset$', call.data))
async def cicada_reset(call: types.CallbackQuery):
    object_id = call.data.split('/')[1]
    await call.message.edit_text('Вы действительно хотите сбросить заряд аккумулятора?\n'
                                 '<b>⚠ Это действие нельзя отменить! ⚠</b>',
                                 reply_markup=kb.reset_q(object_id), parse_mode='html')
    await call.answer()


@dp.callback_query_handler(lambda call: re.search(r'^cicada/\d+/reset/ok$', call.data))
async def cicada_reset_question(call: types.CallbackQuery):

    object_id = call.data.split('/')[1]

    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:

            instance = CicadaInstance(wialon, object_id)
            await instance.set(5377)

            current_sensor = instance.sensors_search_by_name('Выходов на связь')
            reset_sensor = instance.sensors_search_by_name('reset_battery_value')

            reset_sensor.update({
                    "itemId": object_id,
                    "callMode": 'update',
                    "unlink": False,
                    "p": 'const{}'.format(instance.calc_last_msg[str(current_sensor['id'])])
            })
            updated = await wialon.update_sensor(reset_sensor)
            if 'error' not in updated:
                await call.answer('Заряд аккумулятора успешно сброшен', show_alert=True)
            else:
                await call.answer('Произошла ошибка')
        else:
            await wrong_sid(call.message)
    else:
        await wrong_token(call.message)
    await call.answer()
    await cicada_details(call)


@dp.callback_query_handler(lambda call: re.search(r'^cicada/\d+/location$', call.data))
async def cicada_location(call: types.CallbackQuery):
    object_id = call.data.split('/')[1]

    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:

            instance = CicadaInstance(wialon, object_id)
            await instance.set(5377)

            send_interval = instance.sensors_search_by_name('Интервал передачи')
            send_interval_value = instance.calc_last_msg[str(send_interval['id'])]

            locator = await wialon.create_locator_token([object_id], dur=3600*send_interval_value)
            await call.message.answer_location(instance.pos_y, instance.pos_x,
                                               reply=True,
                                               reply_markup=kb.location(object_id,
                                                                        instance.pos_y, instance.pos_x,
                                                                        WLN_HOST, locator['h']),
                                               live_period=3600*send_interval_value)
            await call.answer()
        else:
            await wrong_sid(call.message)
    else:
        await wrong_token(call.message)
    await call.answer()


@dp.callback_query_handler(lambda call: re.search(r'^cicada/\d+/location/update$', call.data))
async def cicada_location_update(call: types.CallbackQuery):
    object_id = call.data.split('/')[1]

    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:
            instance = CicadaInstance(wialon, object_id)
            await instance.set(5377)

            send_interval = instance.sensors_search_by_name('Интервал передачи')
            send_interval_value = instance.calc_last_msg[str(send_interval['id'])]
            locator = await wialon.create_locator_token([object_id], dur=3600*send_interval_value)

            await call.message.edit_live_location(instance.pos_y, instance.pos_x,
                                                  reply_markup=kb.location(object_id,
                                                                           instance.pos_y, instance.pos_x,
                                                                           WLN_HOST, locator['h']))
            await call.answer('Местоположение обновлено')
        else:
            await wrong_sid(call.message)
    else:
        await wrong_token(call.message)
    await call.answer()


@dp.callback_query_handler(lambda call: re.search(r'^cicada/\d+/location/close$', call.data))
async def cicada_location_close(call: types.CallbackQuery):
    await call.message.delete()


@dp.callback_query_handler(lambda call: re.search(r'^cicada/\d+$', call.data))
async def cicada_details(call: types.CallbackQuery):

    object_id = call.data.split('/')[1]

    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:
            instance = CicadaInstance(wialon, object_id)
            await instance.set(5377)

            await instance.sens_update(cicada_sensors)

            if not instance.object:
                await call.answer('Нет данных')
                await cicada_all(call)
            if not instance.object['pos']:
                await call.answer('Нет данных')
                return

            t = instance.object['pos']['t']

            last_datetime = datetime.fromtimestamp(t)
            last_pos_time = last_datetime.strftime("%d.%m.%Y %H:%M:%S")

            def calc_io(io_val, io_m):
                if io_m == 'Вкл/Выкл':
                    return 'Выкл.' if io_val == 0 else 'Вкл'
                else:
                    return f'{io_val} {io_m}'

            for i in instance.object['sens']:
                instance.object['sens'][i]['c'] = json.loads(instance.object['sens'][i]['c'])

            curent = [
                '{}: <pre>{}</pre>'.format(instance.object['sens'][i]['n'],
                                           calc_io(instance.calc_last_msg[i],
                                                   instance.object['sens'][i]['m']))
                for i in instance.object['sens']
                if instance.object['sens'][i]['c']["appear_in_popup"]
                and str(instance.object['sens'][i]['d']).startswith('cicada_tools_aс')
            ]

            curent.insert(0, f'<b>Объект: {instance.object["nm"]}</b>\n')
            curent.insert(1, f'Последнее сообщение: <pre>{last_pos_time}</pre>\n')

            text = '\n'.join(curent)
            await call.message.edit_text(text, parse_mode='HTML')
            await call.message.edit_reply_markup(kb.details(object_id))

            await call.answer()

        else:
            await wrong_sid(call.message)
    else:
        await wrong_token(call.message)
    await call.answer()


@dp.callback_query_handler(lambda call: re.search(r'^cicada/\d+/cmd$', call.data))
async def cicada_commands(call: types.CallbackQuery):
    object_id = call.data.split('/')[1]

    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:
            instance = CicadaInstance(wialon, object_id)
            await instance.set(5889)

            custom = [i for i in instance.object['cmds'] if i['n'] == 'custom']
            if len(custom) == 0:
                await instance.update_cmds()

            await call.message.edit_reply_markup(kb.commands(object_id, cicada_commands_list))
        else:
            await wrong_sid(call.message)
    else:
        await wrong_token(call.message)
    await call.answer()


@dp.callback_query_handler(lambda call: re.search(r'^cicada/\d+/cmd/[\w\s&.;:,]+$', call.data))
async def cicada_commands_exec(call: types.CallbackQuery):
    object_id = call.data.split('/')[1]
    command = call.data.split('/')[3]

    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:

            instance = CicadaInstance(wialon, object_id)
            await instance.set(5889)

            cmds = {cmd['p']: cmd for cmd in cicada_commands_list}
            ret = await instance.exec_cmd(cmds[command])

            if 'error' not in ret:
                await call.answer('Выполнена команда: ' + command)
            else:
                await call.answer('Произошла ошибка')
        else:
            await wrong_sid(call.message)
    else:
        await wrong_token(call.message)
    await call.answer()
    await cicada_details(call)



