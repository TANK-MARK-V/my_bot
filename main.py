import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

import config


# Основные роутеры
from handlers import router
from admin import router_admin as admin
from free_handler import free_router as free

# Роутеры для решения задач
from STI_bot import router_sti as sti
from EVO_bot import router_evo as evo
from ATOM import router_atom as atom

# Развлекательные роутеры
from lolgen_bot import router_lolgen as lolgen
from coding_bot import router_coding as coding
from irregular_verbs import router_verbs as verbs
from valent import router_val as val


ROUTERS = [router, admin]  # Основные роутеры
ROUTERS += [lolgen, coding, val, sti]  # Обычные роутеры
ROUTERS += [evo, atom, verbs]  # Роутеры, которые имеют FSM
ROUTERS += [free,]  # Обработчик пустых сообщений


async def main():
    print("Старт\n")
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(*ROUTERS)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())