import asyncio

from main import dp, types, bot_logger


@dp.message_handler()
async def all_msg_listener(message: types.Message):
    bot_logger.info('undefined message {} by @{} {}'.format(message.from_user.id,
                                                            message.from_user.username,
                                                            message.text))