from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import COMMANDS, info
from logs import do_log as log
from users import get_users


router = Router()

#                                                                                   Старт
@router.message(CommandStart())
async def start_handler(msg: Message):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    log(msg, ('команда /start',))
    await msg.answer('Чтобы узнать, что я умею используй "/info"')

#                                                                           Информация о командах
@router.message(Command("info"))
async def information(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    if command.args and command.args in COMMANDS['__names__']:
        log(msg, (f'команда /info {command.args}',))
        await msg.reply(info(command=command.args))
        return None
    log(msg, ('команда /info',))
    builder = InlineKeyboardBuilder()
    for command in COMMANDS["__names__"]:
        builder.add(types.InlineKeyboardButton(
            text=f'/{command}',
            callback_data=f'command_{command}'))
        grid = [3 for _ in range(len(COMMANDS["__admin_names__"]) // 3)]
    if len(COMMANDS["__names__"]) % 3:
        grid.append(len(COMMANDS["__names__"]) % 3)
    builder.adjust(*grid)
    print(grid)
    await msg.reply("Выберете нужную команду", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("command_"))
async def send_info(callback: types.CallbackQuery):
    log(callback, (f'Выбран вариант {callback.data}',))
    await callback.message.answer(info(callback.data.replace("command_", '')))


#                                                                               Всё остальное
@router.message()
async def message_handler(msg: Message):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    log(msg, ('Пустое сообщение:', msg.text))
    await msg.answer(f"Твой ID, имя, фамилия и username: {msg.from_user.id}, {msg.from_user.full_name}, {msg.from_user.username},")