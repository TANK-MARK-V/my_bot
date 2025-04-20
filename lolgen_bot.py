from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from logs import do_log as log
from config import autorisation, last_massage

from scripts.Lolgen.Lolgen import brain, adding, getting
router_lolgen = Router()


@router_lolgen.message(Command("lolgen"))
async def do_lol(msg: Message, command: CommandObject, bot: Bot):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    args = command.args.replace('<', '').replace('>', '') if command.args else ''
    if args:
        last_massage[msg.from_user.id] = ("lolgen", args)
    else:
        if msg.from_user.id in last_massage.keys() and len(last_massage[msg.from_user.id]) > 1 and last_massage[msg.from_user.id][0] == "lolgen":
            args = (last_massage[msg.from_user.id][1])
        else:
            await log(msg, ('Команда /lolgen не получила схему',), bot)
            await msg.reply("Необходимо передать схему предложения хотя бы раз")
            return None
    try:
        text = brain(order=args)
    except Exception as e:
        await log(msg, ('Команда /lolgen:', f'ОШИБКА - {e}, запрос - {args}'), bot, error=True)
        await msg.reply("Что-то пошло не так")
        return None
    await log(msg, ('Команда /lolgen выполнила свою работу:', text), bot)
    await msg.reply(text)
    return None



@router_lolgen.message(Command("add_word"))
async def adding_word(msg: Message, command: CommandObject, bot: Bot):
    
    last_massage[msg.from_user.id] = ("add_word", )

    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    if not command.args:
        await log(msg, ('Команда /add_word не получила аргументов',), bot)
        await msg.reply("Нужно ввести слово и его часть речи")
        return None
    leest = command.args.split(' ')
    if len(leest) != 2:
        await log(msg, ('Команда /add_word получила не 2 аргумента:', command.args), bot)
        await msg.reply('Нужно ввести только одно слово и его часть речи')
        return None
    result = adding(leest[0], leest[1])
    await log(msg, ('Команда /add_word выполнила свою работу с результатом:', result, command.args), bot)
    await msg.reply(result)
    return None


@router_lolgen.message(Command("get_words"))
async def getting_word(msg: Message, bot: Bot):

    last_massage[msg.from_user.id] = ("get_words",)
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    words = getting()
    speech = {"сущ": "Существительные", "прил": "Прилагательные", "глаг": "Глаголы"}
    for part in words.keys():
        text = speech[part] + ':\n' + ', '.join(sorted(words[part]))
        await msg.answer(text)
    await log(msg, ('Команда /get_words выполнила свою работу',), bot)
    return None