from aiogram import Router, Bot
# Работа с сообщениями
from aiogram.types import Message
from aiogram.filters import Command


import random


from scripts.Logs import autorisation


WORDS = ["ты — мой личный сорт счастья! С Днём святого Валентина!",
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
            "познакомиться с тобой это как урвать последнюю вкусную булочку в столовой. С Днём святого Валентина!"]


router_val = Router()  # Обработчик команды valentine

@router_val.message(Command("valentine"))
async def valentine(msg: Message, bot: Bot):  # Получение валентинок
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    selebr = random.choice(WORDS)
    personal = f"{msg.from_user.first_name}, {selebr}"
    await msg.reply(personal)
    await user.log("Command /valentine: пользователь получил валентику", personal)