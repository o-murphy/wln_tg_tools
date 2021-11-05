import asyncio


from main import dp, types, bot_logger, db, WLN, WLN_HOST, WIALON, wrong_token, wrong_sid, wln_auth_succeed
from keyboards import keyboards as kb


@dp.message_handler(commands=['test'])
async def dealer(message: types.Message):
    a = await dp.bot.me
    print(a)
    await message.answer('ok')