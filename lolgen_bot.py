from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from logs import do_log as log
from users import get_users
from config import last_massage

from scripts.Lolgen import brain, adding
router_lolgen = Router()

last_command = {}



@router_lolgen.message(Command("lolgen"))
async def do_lol(msg: Message, command: CommandObject, bot: Bot):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    args = command.args if command.args else ''
    if '<' in args:
        args = args.replace('<', '')
    if '>' in args:
        args = args.replace('>', '')
    if not args:
        try:
            args = last_command[msg.from_user.id]
        except Exception as e:
            last_massage[msg.from_user.id] = ("lolgen", )
            await log(msg, ('Команда /lolgen не получила схему',), bot)
            await msg.reply("Необходимо передать схему предложения хотя бы раз")
            return None
    else:
        last_command[msg.from_user.id] = args
    try:
        text = brain(order=args)
    except Exception as e:
        last_massage[msg.from_user.id] = ("lolgen", )
        await log(msg, ('Команда /lolgen:', f'ОШИБКА - {e}, запрос - {args}'), bot, error=True)
        await msg.reply("Что-то пошло не так")
        return None
    last_massage[msg.from_user.id] = ("lolgen", )
    await log(msg, ('Команда /lolgen выполнила свою работу:', text), bot)
    await msg.reply(text)
    return None



@router_lolgen.message(Command("word"))
async def adding_word(msg: Message, command: CommandObject, bot: Bot):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if not command.args:
        last_massage[msg.from_user.id] = ("word", )
        await log(msg, ('Команда /word не получила аргументов',), bot)
        await msg.reply("Нужно ввести слово и его часть речи")
        return None
    leest = command.args.split(' ')
    if len(leest) != 2:
        last_massage[msg.from_user.id] = ("word", )
        await log(msg, ('Команда /word получила не 2 аргумента:', command.args), bot)
        await msg.reply('Нужно ввести только одно слово и его часть речи')
        return None
    result = adding(leest[0], leest[1])
    last_massage[msg.from_user.id] = ("word", )
    await log(msg, ('Команда /word выполнила свою работу с результатом:', result, command.args), bot)
    await msg.reply(result)
    return None