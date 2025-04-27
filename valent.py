from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command

from config import autorisation
from logs import do_log as log

import random

router_val = Router()


@router_val.message(Command('valentine'))
async def start_handler(msg: Message, bot: Bot):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    selebr = random.choice(["ты — мой личный сорт счастья! С Днём святого Валентина!",
            "влюбляться в тебя — моё любимое занятие. С праздником!",
            "ты — мой лучший подарок судьбы. С 14 февраля!",
            "моё сердце бьётся только для тебя. С Днём всех влюблённых!",
            "ты — моя половинка, моё всё. С Валентином!",
            "с тобой каждый день — праздник. С 14 февраля!",
            "ты делаешь меня счастливым. С Днём святого Валентина!",
            "моя любовь к тебе бесконечна. С праздником!",
            "ты — лучшее, что случилось со мной. С 14 февраля!",
            "просто спасибо, что ты есть. С Днём святого Валентина!",
            "ты как последний урок в пятницу, всегда жду с нетерпением. С 14 февраля!",
            "ты как пятерка по очень сложному предмету, даришь невероятные эмоции. С праздником!",
            "познакомиться с тобой это как урвать последнюю вкусную булочку в столовой. С Днём святого Валентина!"])

    personal = f'{msg.from_user.first_name}, {selebr}'
    await log(msg, ('команда /valentine', personal), bot)
    await msg.answer(personal)
    return None