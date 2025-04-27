from aiogram import Router, Bot
from aiogram.types import Message

from config import autorisation
from logs import do_log as log

free_router = Router()


@free_router.message()
async def free_handler(msg: Message, bot: Bot):

    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    if not msg.text:
        await log(msg, (f'Пользователь отправил "пустое" сообщение', ), bot)
        await msg.reply(f"Извини, я могу читать только текстовые сообщения")
        return None
    
    await log(msg, ('Пустое сообщение:', msg.text), bot)
    if 'привет' in msg.text.lower():
        await msg.answer(f"Привет")
    elif 'дела' in msg.text.lower():
        await msg.answer(f"Хорошо, а у тебя?")
    else:
        await msg.answer(f"Я тебя не понял(")
    return None