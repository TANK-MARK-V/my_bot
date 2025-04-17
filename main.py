import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties


import config
from handlers import router
from lolgen_bot import router_lolgen as lolgen
from STI_bot import router_sti as sti
from EVO_bot import router_evo as evo
from admin import router_admin as admin
from coding import router_coding as coding
from irregular_verbs import router_verbs as verbs
from ATOM import router_atom as atom
from valent import router_val as val
from free_handler import free_router as free

ROUTERS = [router, lolgen, admin, coding, val, sti, evo, verbs, atom, free]


async def main():
    print("Старт\n")
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(*ROUTERS)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())