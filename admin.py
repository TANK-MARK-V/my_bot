from aiogram import types, F, Router, Bot
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import COMMANDS, info
from logs import do_log as log
from users import get_users, get_user_list

from os import path
import datetime

router_admin = Router()

#                                                                               Инструменты админа
@router_admin.message(Command("admin"))
async def admin(msg: Message):
    user = get_users(msg=msg, info=msg.from_user.username)
    if not user[2]:
        log(msg, (f'Пользователь не обладает правами администратора', ))
        await msg.reply(f"Вы не обладаете правами администратора")
        return None
    log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}', ))
    await msg.reply(f"Вы обладаете правами администратора уровня {user[2]}")
    return None

#                                                                           Информация о командах админа
@router_admin.message(Command("admin_info"))
async def admin_information(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg, info=msg.from_user.username)
    need = 1
    if user[2] < need:
        log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {need}', ))
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None

    if command.args and command.args in COMMANDS['__admin_names__']:
        log(msg, (f'команда /info {command.args}',))
        await msg.reply(info(command=command.args))
        return None
    log(msg, ('команда /info',))
    builder = InlineKeyboardBuilder()
    for command in COMMANDS["__admin_names__"]:
        builder.add(types.InlineKeyboardButton(
            text=f'/{command}',
            callback_data=f'command_{command}'))
        grid = [2 for _ in range(len(COMMANDS["__admin_names__"]) // 2)]
        if len(COMMANDS["__admin_names__"]) % 2:
            grid.append(1)
        builder.adjust(*grid)
    await msg.reply("Выберете нужную команду", reply_markup=builder.as_markup())


@router_admin.callback_query(F.data.startswith("command_"))
async def send_info(callback: types.CallbackQuery):
    log(callback, (f'Выбран вариант {callback.data}',))
    await callback.message.answer(info(callback.data.replace("command_", '')))

#                                                                               Получить список пользователей
@router_admin.message(Command("admin_users"))
async def user_list(msg: Message):
    user = get_users(msg=msg, info=msg.from_user.username)
    need = 3
    if user[2] < need:
        log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {need}', ))
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    users = get_user_list()
    log(msg, (f'/admin - получена информация о пользователях', ))
    text = '\n'.join([' ~~~ '.join(tuple(map(lambda x: str(x), line))) for line in users])
    await msg.reply(text)

#                                                                               Получить логи пользователя
@router_admin.message(Command("admin_logs"))
async def admin_logs(msg: Message, command: CommandObject):
    user = get_users(msg=msg, info=msg.from_user.username)
    if not command.args:
        log(msg, (f'/admin_logs - пользователь не передал аргументов', ))
        await msg.reply(f"Некорректно введена команда")
        return None
    args = command.args.split(' ')
    need = 3
    if user[2] < need:
        log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {need}', ))
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    try:
        args[0] = args[0].replace('@', '') if '@' in args[0] else args[0]
        wanted = get_users(info=args[0])
    except Exception:
        log(msg, (f'Пользователь некорректно ввёл информацию о пользователе:', command.args))
        await msg.reply(f"Некорректно введена информация о пользователе")
        return None
    if not wanted:
        log(msg, (f'/admin_logs - искомый пользователь не существует:', command.args))
        await msg.reply(f"Такого пользователя не существует")
        return None
    args[0] = wanted[0]
    if len(args) == 1:
        args.append(datetime.datetime.now().strftime("%y-%m.%d"))
    way = f"{path.join('logs', *args)}.txt"
    if not path.isfile(way):
        log(msg, (f'/admin_logs:', f'файл не найден - {way}'))
        await msg.reply('Файл не найден')
        return None
    log(msg, (f'/admin_logs:', f'файл найден - {way}'))
    text = FSInputFile(way)
    await msg.reply_document(text)

#                                                                               Получить ошибки пользователя
@router_admin.message(Command("admin_errors"))
async def admin_errors(msg: Message, command: CommandObject):
    user = get_users(msg=msg, info=msg.from_user.username)
    if not command.args:
        log(msg, (f'/admin_errors - не передал аргументов', ))
        await msg.reply(f"Некорректно введена команда")
        return None
    args = command.args.split(' ')
    need = 3
    if user[2] < need:
        log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {need}', ))
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    try:
        args[0] = args[0].replace('@', '') if '@' in args[0] else args[0]
        wanted = get_users(info=args[0])
    except Exception:
        log(msg, (f'Пользователь некорректно ввёл информацию о пользователе:', command.args))
        await msg.reply(f"Некорректно введена информация о пользователе")
        return None
    if not wanted:
        log(msg, (f'/admin_errors - искомый пользователь не существует:', command.args))
        await msg.reply(f"Такого пользователя не существует")
        return None
    args[0] = wanted[0]
    if len(args) == 1:
        args.append(datetime.datetime.now().strftime("%y-%m.%d"))
    way = f"{path.join('errors', *args)}.txt"
    if not path.isfile(way):
        log(msg, (f'/admin_errors:', f'файл не найден - {way}'))
        await msg.reply('Файл не найден')
        return None
    log(msg, (f'/admin_errors:', f'файл найден - {way}'))
    text = FSInputFile(way)
    await msg.reply_document(text)

#                                                                               Написать пользователю
@router_admin.message(Command("admin_chat"))
async def admin_chat(msg: Message, command: CommandObject, bot: Bot):
    user = get_users(msg=msg, info=msg.from_user.username)
    if not command.args or len(command.args) < 2:
        log(msg, (f'/admin_chat - пользователь не передал аргументов', ))
        await msg.reply(f"Некорректно введена команда")
        return None
    args = command.args.split()
    need = 2
    if user[2] < need:
        log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {need}', ))
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    if len(args) < 2:
        log(msg, (f'/admin_chat - пользователь некорректно ввёл команду', command.args))
        await msg.reply(f"Некорректно введена команда")
        return None
    try:
        args[0] = args[0].replace('@', '') if '@' in args[0] else args[0]
        wanted = get_users(info=args[0])
    except Exception:
        log(msg, (f'Пользователь некорректно ввёл информацию о пользователе:', command.args))
        await msg.reply(f"Некорректно введена информация о пользователе")
        return None
    if not wanted:
        log(msg, (f'/admin_chat - нужный пользователь не существует:', command.args))
        await msg.reply(f"Такого пользователя не существует")
        return None
    args[1] = ' '.join(args[1:])
    log(msg, (f'/admin_chat - пользователь написал другому пользователю:', f'{args[0]}: {args[1]}'))
    await bot.send_message(wanted[0], args[1]) 
    await msg.reply(f"Сообщение успешно отправлено")