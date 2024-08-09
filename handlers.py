from aiogram import types, F, Router, Bot
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import COMMANDS, info
from logs import do_log as log
from users import get_users, get_user_list

from os import path
import datetime

router = Router()

#                                                                                   Старт
@router.message(CommandStart())
async def start_handler(msg: Message):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    log(msg, ('Комманда /start',))
    await msg.answer('Чтобы узнать, что я умею используй "/info"')

#                                                                           Информация о коммандах
@router.message(Command("info"))
async def information(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    if command.args and command.args in COMMANDS['_names_']:
        log(msg, (f'Комманда /info {command.args}',))
        await msg.reply(info(command=command.args))
        return None
    log(msg, ('Комманда /info',))
    builder = InlineKeyboardBuilder()
    for command in COMMANDS["_names_"]:
        builder.add(types.InlineKeyboardButton(
            text=f'/{command}',
            callback_data=f'command_{command}'))
        
    await msg.reply("Выберете нужную комманду", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("command_"))
async def send_info(callback: types.CallbackQuery):
    log(callback, (f'Выбран вариант {callback.data}',))
    await callback.message.answer(info(callback.data.replace("command_", '')))
    await callback.answer()

#                                                                               Инструменты админа
@router.message(Command("admin"))
async def admin(msg: Message, command: CommandObject, bot: Bot):
    user = get_users(msg=msg, info=msg.from_user.username)
    if not user[2]:
        log(msg, (f'Пользователь не обладает правами администратора', ))
        await msg.reply(f"Вы не обладаете правами администратора")
        return None
    if not command.args:
            log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}', ))
            await msg.reply(f"Вы обладаете правами администратора уровня {user[2]}")
            return None
    if command.args == 'users':
        await user_list(msg, user)
        return None
    args = command.args.split(' ')
    if args[0] in ('logs', 'errors'):
        await admin_logs(msg, command, user, args)
        return None
    if args[0] in ('chat'):
        await admin_chat(msg, command, user, args, bot)
        return None
    log(msg, (f'/admin - несуществующая комманда:', command.args))
    await msg.reply(f"Такой комманды не существует")

#                                                                               Получить список пользователей
async def user_list(msg, user):
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
async def admin_logs(msg, command, user, args):
    need = 3
    if user[2] < need:
        log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {need}', ))
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    if len(args) == 1:
        log(msg, (f'/admin - пользователь некорректно ввёл команду:', command.args))
        await msg.reply(f"Некорректно введена комманда")
        return None
    try:
        args[1] = args[1].replace('@', '') if '@' in args[1] else args[1]
        wanted = get_users(info=args[1])
    except Exception:
        log(msg, (f'Пользователь некорректно ввёл информацию о пользователе:', command.args))
        await msg.reply(f"Некорректно введена информация о пользователе")
        return None
    if not wanted:
        log(msg, (f'/admin - искомый пользователь не существует:', command.args))
        await msg.reply(f"Такого пользователя не существует")
        return None
    args[1] = wanted[0]
    if len(args) == 2:
        args.append(datetime.datetime.now().strftime("%y-%m.%d"))
    way = f"{path.join(*args)}.txt"
    if not path.isfile(way):
        log(msg, (f'/admin {args[0]}:', f'файл не найден - {way}'))
        await msg.reply('Файл не найден')
        return None
    log(msg, (f'/admin {args[0]}:', f'файл найден - {way}'))
    text = FSInputFile(way)
    await msg.reply_document(text)

#                                                                               Написать пользователю
async def admin_chat(msg, command, user, args, bot):
    need = 2
    if user[2] < need:
        log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {need}', ))
        await msg.reply(f"Вы не обладаете нужными правами администратора")
        return None
    if len(args) < 3:
        log(msg, (f'/admin - пользователь некорректно ввёл команду:', command.args))
        await msg.reply(f"Некорректно введена комманда")
        return None
    try:
        args[1] = args[1].replace('@', '') if '@' in args[1] else args[1]
        wanted = get_users(info=args[1])
    except Exception:
        log(msg, (f'Пользователь некорректно ввёл информацию о пользователе:', command.args))
        await msg.reply(f"Некорректно введена информация о пользователе")
        return None
    if not wanted:
        log(msg, (f'/admin - нужный пользователь не существует:', command.args))
        await msg.reply(f"Такого пользователя не существует")
        return None
    args[2] = ' '.join(args[2:])
    log(msg, (f'/admin - пользователь написал другому пользователю:', f'{args[1]}: {args[2]}'))
    await bot.send_message(wanted[0], args[2]) 
    await msg.reply(f"Сообщение успешно отправлено")
    
#                                                                               Всё остальное
@router.message()
async def message_handler(msg: Message):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    log(msg, ('Пустое сообщение:', msg.text))
    await msg.answer(f"Твой ID, имя, фамилия и username: {msg.from_user.id}, {msg.from_user.full_name}, {msg.from_user.username},")