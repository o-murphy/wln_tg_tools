import asyncio
from aiogram import Bot, executor, types
from aiogram.dispatcher import Dispatcher


from config import Init
from handlers import *

TOKEN = Init.BOT_TOKEN
bot = Bot(token=TOKEN, parse_mode='html')
dp = Dispatcher(bot)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

