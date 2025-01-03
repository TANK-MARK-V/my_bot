import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties


import config
from handlers import router
from lolgen import router_lolgen
from STI import router_sti
# from EVO import router_evo
from admin import router_admin
from coding import router_coding


async def main():
    print("Старт\n")
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    # dp.include_routers(router_lolgen, router_sti, router_evo, router_admin, router_coding, router)
    dp.include_routers(router_lolgen, router_sti, router_admin, router_coding, router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())



if __name__ == "__main__":
    asyncio.run(main())