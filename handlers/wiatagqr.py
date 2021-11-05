import asyncio
import re
import random


from main import dp, types, bot_logger, db, WLN, WLN_HOST, LOGIN_URL, WIALON, wrong_token, wrong_sid, wln_auth_succeed
from keyboards import keyboards as kb
from modules.item_instance import WiaTagInstance
from modules.aiowiatag import WiaTag
#
#
# @dp.callback_query_handler(lambda call: call.data == 'wiatag')
# async def wiatag(call: types.CallbackQuery):
#     bot_logger.info('wiatag')
#     await call.answer()


async def search_wiatags(wialon):
    types = await wialon.get_hw_types(fv=['WiaTag'])
    type_id = types[0]['id']
    list_search_instance = await wialon.search_items(spec={
        "propName": 'rel_hw_type_id,sys_name',
        "propValueMask": f'{type_id},*'
    })
    return list_search_instance['items']


@dp.callback_query_handler(lambda call: call.data == 'wiatag')
async def wiatag_all(call: types.CallbackQuery):
    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:
            await wln_auth_succeed(call.message)
            wiatags = await search_wiatags(wialon)
            await call.message.edit_text('Выберите объект')
            await call.message.edit_reply_markup(kb.wiatags(wiatags))

        else:
            await wrong_sid(call.message)
    else:
        await wrong_token(call.message)
    await call.answer()


@dp.callback_query_handler(lambda call: re.search(r'^wiatag/\d+$', call.data))
async def wiatag_qr(call: types.CallbackQuery):
    object_id = call.data.split('/')[1]
    await call.message.edit_text('Сгенерировать новый QR код?\n'
                                 '<b>⚠ Это действие нельзя отменить! ⚠</b>',
                                 reply_markup=kb.wiatags_new_qr(object_id), parse_mode='html')
    await call.answer()


@dp.callback_query_handler(lambda call: re.search(r'^wiatag/\d+/new$', call.data))
async def wiatag_qr_new(call: types.CallbackQuery):
    object_id = call.data.split('/')[1]
    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:

            instance = WiaTagInstance(wialon, object_id)
            await instance.set(5377)

            new_psw = [str(random.randint(0, 9)) for i in range(10)]
            svc = 'unit/update_access_password'
            params = {"itemId": object_id, "accessPassword": ''.join(new_psw)}
            await instance.wialon.request(svc, params)

            wiatag = WiaTag()
            await wiatag.get_link(host=WLN_HOST.replace('https://', ''),
                                  uid=instance.object['uid'],
                                  **{"pass": new_psw})
            await wiatag.get_qr()

            new_call = types.CallbackQuery()
            answer = await call.message.answer_photo(wiatag.png, f'{instance.object["nm"]}, {wiatag.link}')
            await call.answer()
            await call.message.delete()
            new_call.message = await answer.answer('Возврат к списку объектов WiaTag')

            await wiatag_all(new_call)

        else:
            await wrong_sid(call.message)
    else:
        await wrong_token(call.message)







