import asyncio
from handlers.cicada_tools import search_cicadas, calculate
from main import dp, db, WLN_HOST, WLN
from keyboards.keyboards import charge_to_icon
from datetime import datetime
import logging


logging.basicConfig()
notify_logger = logging.getLogger(name='notification')
notify_logger.setLevel(logging.INFO)


class CicadaNotify(object):
    def __init__(self):
        pass

    async def check(self, wialon):
        cicadas = await search_cicadas(wialon)
        ret = await asyncio.gather(*[calculate(wialon, instance) for instance in cicadas])
        return ret

    async def send(self, rec):
        token = rec[4]
        user_id = rec[1]
        wialon = WLN(WLN_HOST, token)
        await wialon.login()
        ret = await self.check(wialon)
        low_bat_list = []
        for r in ret:
            if not r['last_charge']:
                pass
            elif r['last_charge'] <= 10:
                low_bat_list.append(f"🔴 {r['nm']} | {charge_to_icon(r['last_charge']).replace('🟥', '')}\n")
        text = f"⚠ Внимание! ⚠\n" \
               f"{'Необходима замена элемента питания на следующих объектах:'}\n" \
               f"{''.join(low_bat_list)}"
        await dp.bot.send_message(user_id, text)

    async def check_loop(self):
        ret = db.search_all()
        await asyncio.gather(*[self.send(rec) for rec in ret])
        while True:
            cur_time = datetime.now().time()
            if cur_time.hour == 0 and cur_time.minute == 0:
                notify_logger.info('CicadaNotify Script Executing...')
                ret = db.search_all()
                await asyncio.gather(*[self.send(rec) for rec in ret])
                notify_logger.info('CicadaNotify Script Success')
            await asyncio.sleep(60)





