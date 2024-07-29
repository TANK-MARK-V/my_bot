from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import COMMANDS, ADMIN, info
from logs import do_log as log

from os import path
import datetime

router = Router()

#                                                                                   Старт
@router.message(Command("start"))
async def start_handler(msg: Message):
    log(msg, ('Комманда /start',))
    await msg.answer('Чтобы узнать, что я умею используй "/info"')

#                                                                           Информация о коммандах
@router.message(Command("info"))
async def information(msg: Message, command: CommandObject):
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
async def admin(msg: Message, command: CommandObject):
    nope = '' if (str(msg.from_user.id), msg.from_user.username) in ADMIN else 'не '
    if not command.args:
        log(msg, (f'Пользователь {nope}обладает правами администратора', ))
        await msg.reply(f"Вы {nope}обладаете правами администратора")
        return None
    if not nope:
        args = command.args.split('_')
        if args[0] in ('logs', 'errors'):
            if len(args) == 2:
                args.append(datetime.datetime.now().strftime("%d.%m-%y"))
            if len(args) == 3:
                if '-' not in args[2]:
                    args[2] += '-' + str(datetime.datetime.now().strftime("%y"))
            way = f"{path.join(*args)}.txt"
            if not path.isfile(way):
                log(msg, (f'Комманда /admin {args[0]}:', f'файл не найден - {way}'))
                await msg.reply('Файл не найден')
                return None
            log(msg, (f'Комманда /admin {args[0]}:', f'файл найден - {way}'))
            with open(way, 'r', encoding='UTF-8') as file:
                await msg.reply(''.join(file.readlines()))

#                                                                               Всё остальное
@router.message()
async def message_handler(msg: Message):
    log(msg, ('Пустое сообщение:', msg.text))
    await msg.answer(f"Твой ID, имя, фамилия и username: {msg.from_user.id}, {msg.from_user.full_name}, {msg.from_user.username},")