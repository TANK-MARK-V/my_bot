from aiogram import Router, Bot
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandObject

from config import last_massage, LEVELS
from logs import do_log as log
from users import get_users, get_user_list

from os import path
import datetime

router_admin = Router()

#                                                                               Инструменты админа
@router_admin.message(Command("admin"))
async def admin(msg: Message, bot: Bot):
    user = get_users(msg=msg, info=msg.from_user.username)
    if not user[2]:
        last_massage[msg.from_user.id] = ("admin", )
        await log(msg, (f'Пользователь не обладает правами администратора', ), bot)
        await msg.reply(f"Вы не обладаете правами администратора")
        return None
    last_massage[msg.from_user.id] = ("admin", )
    await log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}', ), bot)
    await msg.reply(f"Вы обладаете правами администратора уровня {user[2]}")
    return None


#                                                                               Получить список пользователей
@router_admin.message(Command("users"))
async def user_list(msg: Message, bot: Bot):
    user = get_users(msg=msg, info=msg.from_user.username)
    if user[2] < LEVELS["users"]:
        last_massage[msg.from_user.id] = ("users", )
        await log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {LEVELS["users"]}', ), bot)
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    text = []
    for line in get_user_list():
        text.append(f"{line[0]} ~~~ @{line[1]} ~~~ {line[2]}")
    last_massage[msg.from_user.id] = ("users", )
    await log(msg, (f'/users - получена информация о пользователях', ), bot)
    await msg.reply('\n'.join(text))
    return None

#                                                                               Получить логи пользователя
@router_admin.message(Command("logs"))
async def admin_logs(msg: Message, command: CommandObject, bot: Bot):
    user = get_users(msg=msg, info=msg.from_user.username)
    if user[2] < LEVELS["logs"]:
        last_massage[msg.from_user.id] = ("logs", )
        await log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {LEVELS["logs"]}', ), bot)
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    if not command.args:
        last_massage[msg.from_user.id] = ("logs", )
        await log(msg, (f'/logs - пользователь не передал аргументов', ), bot)
        await msg.reply(f"Некорректно введена команда")
        return None
    args = command.args.split(' ')
    try:
        wanted = get_users(info=args[0])
    except Exception:
        last_massage[msg.from_user.id] = ("logs", )
        await log(msg, (f'Пользователь некорректно ввёл информацию о пользователе:', command.args), bot)
        await msg.reply(f"Некорректно введена информация о пользователе")
        return None
    if not wanted:
        last_massage[msg.from_user.id] = ("logs", )
        await log(msg, (f'/logs - искомый пользователь не существует:', command.args), bot)
        await msg.reply(f"Такого пользователя не существует")
        return None
    args[0] = wanted[0]
    if len(args) == 1:
        args.append(datetime.datetime.now().strftime("%y-%m.%d"))
    way = f"{path.join('logs', *args)}.txt"
    if not path.isfile(way):
        last_massage[msg.from_user.id] = ("logs", )
        await log(msg, (f'/logs:', f'файл не найден - {way}'), bot)
        await msg.reply('Файл не найден')
        return None
    last_massage[msg.from_user.id] = ("logs", )
    await log(msg, (f'/logs:', f'файл найден - {way}'), bot)
    text = FSInputFile(way)
    await msg.reply_document(text)
    return None

#                                                                               Получить ошибки пользователя
@router_admin.message(Command("errors"))
async def admin_errors(msg: Message, command: CommandObject, bot: Bot):
    user = get_users(msg=msg, info=msg.from_user.username)
    if not command.args:
        last_massage[msg.from_user.id] = ("errors", )
        await log(msg, (f'/errors - не передал аргументов', ), bot)
        await msg.reply(f"Некорректно введена команда")
        return None
    args = command.args.split(' ')
    if user[2] < LEVELS["errors"]:
        last_massage[msg.from_user.id] = ("errors", )
        await log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {LEVELS["errors"]}', ), bot)
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    try:
        wanted = get_users(info=args[0])
    except Exception:
        last_massage[msg.from_user.id] = ("errors", )
        await log(msg, (f'Пользователь некорректно ввёл информацию о пользователе:', command.args), bot)
        await msg.reply(f"Некорректно введена информация о пользователе")
        return None
    if not wanted:
        last_massage[msg.from_user.id] = ("errors", )
        await log(msg, (f'/errors - искомый пользователь не существует:', command.args), bot)
        await msg.reply(f"Такого пользователя не существует")
        return None
    args[0] = wanted[0]
    if len(args) == 1:
        args.append(datetime.datetime.now().strftime("%y-%m.%d"))
    way = f"{path.join('errors', *args)}.txt"
    if not path.isfile(way):
        last_massage[msg.from_user.id] = ("errors", )
        await log(msg, (f'/errors:', f'файл не найден - {way}'), bot)
        await msg.reply('Файл не найден')
        return None
    last_massage[msg.from_user.id] = ("errors", )
    await log(msg, (f'/errors:', f'файл найден - {way}'), bot)
    text = FSInputFile(way)
    await msg.reply_document(text)
    return None

#                                                                               Написать пользователю
@router_admin.message(Command("chat"))
async def admin_chat(msg: Message, command: CommandObject, bot: Bot):
    global last_massage
    user = get_users(msg=msg, info=msg.from_user.username)
    if user[2] < LEVELS["chat"]:
        last_massage[msg.from_user.id] = ("chat", )
        await log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {LEVELS["chat"]}', ), bot)
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    if not command.args:
        if msg.from_user.id in last_massage.keys() and last_massage[msg.from_user.id][0] == "chat" and len(last_massage[msg.from_user.id]) > 1:
            last_massage[msg.from_user.id] = ("chat", )
            await log(msg, (f'/chat - пользователь закончил чат', ), bot)
            await msg.reply(f"Сообщения больше не отправляются")
            return None
        last_massage[msg.from_user.id] = ("chat", )
        await log(msg, (f'/chat - пользователь не передал информацию о пользователе', ), bot)
        await msg.reply(f"Не была указана информация о пользователе")
        return None
    try:
        wanted = get_users(info=command.args)
    except Exception:
        last_massage[msg.from_user.id] = ("chat", )
        await log(msg, (f'Пользователь некорректно ввёл информацию о пользователе:', command.args), bot)
        await msg.reply(f"Некорректно введена информация о пользователе")
        return None
    if not wanted:
        last_massage[msg.from_user.id] = ("chat", )
        await log(msg, (f'/chat - нужный пользователь не существует:', command.args), bot)
        await msg.reply(f"Такого пользователя не существует")
        return None
    last_massage[msg.from_user.id] = ("chat", wanted)
    await log(msg, (f'/chat - пользователь начал чат с другим пользователем:', wanted[0] + ' ~~~ ' + wanted[1]), bot)
    await msg.reply(f"Пользователь @{wanted[1]} найден. Напишите сообщение")
    return None