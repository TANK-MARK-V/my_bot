from aiogram import Router, Bot
# Работа с сообщениями
from aiogram.types import Message


from scripts.Logs import autorisation


free_router = Router()  # Обработчик всех сообщений, не попавших под остальные обработчики

@free_router.message()
async def free_handler(msg: Message, bot: Bot):
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    if not msg.text:  # Пользователь отправил какую-то картинку или что-то подобное
        await msg.reply(f"Извини, я могу читать только текстовые сообщения")
        await user.log("Пользователь отправил \"пустое\" сообщение")
        return None
    
    if 'привет' in msg.text.lower():
        await msg.answer("Привет")
    elif 'дела' in msg.text.lower():
        await msg.answer("Хорошо, а у тебя?")
    else:
        await msg.answer("Я тебя не понял(")
    await user.log("Пустое сообщение:", msg.text)