from aiogram import types, F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from random import sample

from config import COMMANDS, info, LEVELS, last_massage
from logs import do_log as log

from users import get_users

router = Router()

#                                                                                   Старт
@router.message(CommandStart())
async def start_handler(msg: Message, bot: Bot):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    last_massage[msg.from_user.id] = ("start", )
    await log(msg, ('Команда /start',), bot)
    await msg.answer('Чтобы узнать, что я умею, используй "/info"')
    return None

#                                                                           Информация о командах
@router.message(Command("info"))
async def information(msg: Message, command: CommandObject, bot: Bot):
    
    user = get_users(msg=msg, info=msg.from_user.username)  # Получение информации о пользователе
    
    if command.args and command.args in COMMANDS['__names__']:
        await log(msg, (f'Команда /info {command.args}',), bot)
        await msg.reply(info(command=command.args))
        return None
    if command.args and command.args in COMMANDS['__admin_names__']:
        if user[2] >= LEVELS[command.args]:
            last_massage[msg.from_user.id] = ("info_one", )
            await log(msg, (f'Команда /info {command.args}',), bot)
            await msg.reply(info(command=command.args))
            return None
        else:
            await log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {LEVELS[command.args]}', ), bot)
            await msg.reply(f"Вы не обладаете нужными правами администратора")
            return None
    await log(msg, ('Команда /info',), bot)
    builder = InlineKeyboardBuilder()
    for command in COMMANDS["__names__"]:
        builder.add(types.InlineKeyboardButton(
            text=f'/{command}',
            callback_data=f'command_{command}'))
    for command in COMMANDS["__admin_names__"]:
        if user[2] >= LEVELS[command]:
            builder.add(types.InlineKeyboardButton(
                text=f'/{command}',
                callback_data=f'command_{command}'))
    normal, admin = 2, 2
    grid = [normal for _ in range(len(COMMANDS["__names__"]) // normal)]
    if len(COMMANDS["__names__"]) % normal:
        grid.append(len(COMMANDS["__names__"]) % normal)
    grid += [admin for _ in range(len(COMMANDS["__admin_names__"]) // admin)]
    if len(COMMANDS["__admin_names__"]) % admin:
        grid.append(1)
    builder.adjust(*grid)
    last_massage[msg.from_user.id] = ("info", )
    await msg.reply("Выберете нужную команду", reply_markup=builder.as_markup())
    return None


@router.callback_query(F.data.startswith("command_"))
async def send_info(callback: types.CallbackQuery, bot: Bot):
    await log(callback, (f'Выбран вариант {callback.data}',), bot)
    await callback.message.answer(info(callback.data.replace("command_", '')))
    await callback.answer()
    return None


@router.message(Command('cancel'))
@router.message(Command('stop'))
async def stop(msg: Message, bot: Bot):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    last_massage[msg.from_user.id] = (None, )
    await log(msg, ('Пользователь отменил команду',), bot)
    return None


#                                                                                   Рандомное число
@router.message(Command('random'))
async def start_handler(msg: Message, command: CommandObject, bot: Bot):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if command.args:
        try:
            nums = tuple(map(int, command.args.split()))
            if len(nums) == 2:
                nums = (nums[0], nums[1] + 1, 1)
            elif len(nums) == 1:
                nums = (0, nums[0] + 1, 1)
        except Exception as e:
            print(e)
            await log(msg, ('Команда /random не получила чисел', command.args), bot)
            nums = (0, 2, 1)
    else:
        nums = (0, 2, 1)
    last_massage[msg.from_user.id] = ("random", )
    await log(msg, ('Команда /random',), bot)
    text = ', '.join(map(str, sorted(sample(range(*nums[:2]), k=nums[2]))))
    await msg.reply(text)
    return None