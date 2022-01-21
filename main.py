import asyncio
import os
import logging


from aiogram import Bot, executor, types
from aiogram.dispatcher import Dispatcher

from config import Init

from keyboards import keyboards as kb

from modules.aiowlapi import WLN
from modules import db_worker


abspath = os.path.abspath(__file__)
d_name = os.path.dirname(abspath)
os.chdir(d_name)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s] : %(message)s')
bot_logger = logging.getLogger('bot')
bot_logger.setLevel(logging.INFO)


TOKEN = Init.BOT_TOKEN
DEFAULTS = Init.DEFAULTS
WLN_HOST = Init.WLN_HOST
WLN_TOKEN = Init.WLN_ADMIN_TOKEN

db_path = Init.DB_PATH
db = db_worker.DataBase(db_path)
db.check_db()

bot = Bot(token=TOKEN, parse_mode='html')
dp = Dispatcher(bot)

WIALON = WLN(WLN_HOST, WLN_TOKEN)


def login_url():
    params_list = '&'.join(['{}={}'.format(i, REDIRECT_PARAMS[i]) for i in REDIRECT_PARAMS])
    return '{}/login.html?{}'.format(WLN_HOST, params_list)


BOT_NAME = asyncio.get_event_loop().run_until_complete(dp.bot.get_me())['username']
START_PARAMETER = Init.START_PARAMETER
REDIRECT_URI = '{}{},{}'.format(Init.REDIRECT_URI, BOT_NAME, START_PARAMETER)
REDIRECT_PARAMS = Init.REDIRECT_PARAMS
REDIRECT_PARAMS.update({'redirect_uri': REDIRECT_URI})
LOGIN_URL = login_url()


async def wrong_token(message):
    db.user_logout(message.chat.id)
    await message.edit_text('Выполните вход в Wialon для подключения аккаунта Telegram')
    await message.edit_reply_markup(kb.start(LOGIN_URL))


async def wrong_sid(message):
    db.user_logout(message.chat.id)
    await message.edit_text('Подключение устарело, выполните вход в Wialon')
    await message.edit_reply_markup(kb.start(LOGIN_URL))


async def wln_auth_succeed(message):
    await message.edit_text('Подключение успешно установлено')


if __name__ == '__main__':
    from handlers import *
    from modules import *
    loop = asyncio.get_event_loop()
    loop.create_task(WIALON.session_update())

    # notifications = notify()
    #
    #
    # loop.create_task(notifications.check_loop())
    executor.start_polling(dp, skip_updates=True)
