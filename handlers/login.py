import asyncio

from main import dp, types, bot_logger, WLN, WLN_HOST, db, LOGIN_URL, wrong_token, wrong_sid, wln_auth_succeed
from keyboards import keyboards as kb


@dp.callback_query_handler(lambda call: call.data == 'start_cmd')
async def to_start_cmd(call: types.CallbackQuery):
    await call.message.delete()
    await start_cmd(call.message)


@dp.message_handler(lambda message: message.text == '/start', commands=['start'])
async def start_cmd(message: types.Message):
    answer = await message.answer('Подключение к Wialon')
    try:
        await message.delete()
    except Exception as exception:
        bot_logger.warning(exception)
    token = db.search_token(message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        if wialon.sid:
            await wln_auth_succeed(answer)
            await answer.edit_reply_markup(kb.start_logged())
        else:
            await wrong_sid(answer)
    else:
        await wrong_token(answer)


@dp.message_handler(commands=['start'])
async def login(message: types.Message):

    token = db.search_token(message.chat.id)
    if token:
        db.user_logout(message.chat.id)

    answer = await message.answer('Подключение к Wialon')
    await message.delete()
    access_hash = message.text.replace('/start ', '')
    if access_hash:
        bot_logger.info('Your access hash: {}'.format(access_hash))
        await answer.edit_text('Авторизация')
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        await wialon.login_by_hash(access_hash)
        bot_logger.info('Current session id: {}'.format(wialon.sid))
        await answer.edit_text('Создание авторизационного токена')

        params = {"callMode": 'create',
                  "h": 'TelegramBotAuth',
                  "app": 'TelegramBotAuth.{}'.format(message.chat.id),
                  "at": 0,
                  "dur": 86400,
                  "fl": -1,
                  "p": "{}"}

        token = await wialon.token_update(**params)

        wialon.token = token['h'] if 'h' in token else None
        await wialon.login()
        if wialon.sid:
            bot_logger.info('Created token: {}'.format(wialon.token))
            db.user_login(message.chat.id, message.chat.username, wialon.token, 'user', '', '')

            for i in range(2):
                try:
                    await dp.bot.delete_message(message.chat.id, message.message_id - i)
                except Exception as exception:
                    bot_logger.warning(exception)

            await wln_auth_succeed(answer)
            await answer.edit_reply_markup(kb.start_logged())
        else:
            await wrong_sid(answer)

    else:
        await wrong_token(answer)


@dp.callback_query_handler(lambda call: call.data == 'logout')
async def logout(call: types.CallbackQuery):
    token = db.search_token(call.message.chat.id)
    if token:
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        db.user_logout(call.message.chat.id)
        if wialon.sid:
            await wialon.token_update(callMode='delete', h=token)
        else:
            await wrong_sid(call.message)
    await wrong_token(call.message)
    await call.answer('Вы вышли из аккаунта')