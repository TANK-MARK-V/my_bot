from aiogram import Router, Bot
from aiogram.types import Message

from config import last_massage
from logs import do_log as log

from coding import encode_words, decode_words
from users import get_users

free_router = Router()


@free_router.message()
async def free_handler(msg: Message, bot: Bot):

    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if not msg.text:
        await log(msg, (f'Пользователь отправил "пустое" сообщение', ), bot)
        await msg.reply(f"Извини, я могу читать только сообщения")
        return None
    
    global last_massage
    
    if msg.from_user.id in last_massage.keys():
        last = last_massage[msg.from_user.id]
        if last[0] == "chat" and len(last) > 1:
            wanted = last[1]
            await log(msg, (f'/chat - пользователь написал другому пользователю:', msg.text), bot)
            await bot.send_message(wanted[0], msg.text.replace('<', '').replace('>', '')) 
            await msg.reply(f"Сообщение успешно отправлено")
            return None
        
        if last[0] == "encode" and len(last) > 1:
            await encode_words(msg, bot)
            return None
        
        if last[0] == "decode" and len(last) > 1:
            await decode_words(msg, bot)
            return None
        
    last_massage[msg.from_user.id] = ("empty", )
    await log(msg, ('Пустое сообщение:', msg.text), bot)
    await msg.answer(f"Твой ID, имя, фамилия и username: {msg.from_user.id}, {msg.from_user.full_name}, {msg.from_user.username},")
    return None