from aiogram import types, F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


from aiogram.fsm.context import FSMContext

from random import sample

from config import COMMANDS, SHORTS, info, LEVELS, autorisation
from users import find_user
from logs import do_log as log
from scripts.help import numeral, to_ten, sft, get_RPN

router = Router()

#                                                                                   Старт
@router.message(CommandStart())
async def start_handler(msg: Message, bot: Bot):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    await log(msg, ('Команда /start',), bot)
    await msg.answer('Чтобы узнать, что я умею, используй "/info"')
    return None

#                                                                           Информация о командах
@router.message(Command("info"))
async def information(msg: Message, command: CommandObject, bot: Bot):

    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None
    
    user = find_user(msg.from_user.id)

    if command.args and command.args in COMMANDS['__names__']:
        await log(msg, (f'Команда /info {command.args}',), bot)
        await msg.reply(info(command=command.args))
        return None
    elif command.args and command.args in COMMANDS['__admin_names__']:
        if user["access"] >= LEVELS[command.args]:
            await log(msg, (f'Команда /info {command.args}',), bot)
            await msg.reply(info(command=command.args))
            return None
        else:
            await log(msg, (f'Пользователь обладает правами доступа уровня {user["access"]}, нужен {LEVELS[command.args]}', ), bot)
            await msg.reply(f"Вы не обладаете нужными правами доступа")
            return None
    
    await log(msg, ('Команда /info',), bot)
    await msg.reply("Список команд:\n" + SHORTS)
    builder = InlineKeyboardBuilder()

    for command in COMMANDS["__names__"]:
        if user["access"] >= LEVELS[command]:
            builder.add(types.InlineKeyboardButton(
                text=f'/{command}',
                callback_data=f'command_{command}'))

    for command in COMMANDS["__admin_names__"]:
        if user["access"] >= LEVELS[command]:
            builder.add(types.InlineKeyboardButton(
                text=f'/{command}',
                callback_data=f'command_{command}'))

    normal, admin = 3, 2
    grid = [normal for _ in range(len(COMMANDS["__names__"]) // normal)]
    if len(COMMANDS["__names__"]) % normal:
        grid.append(len(COMMANDS["__names__"]) % normal)
    grid += [admin for _ in range(len(COMMANDS["__admin_names__"]) // admin)]
    if len(COMMANDS["__admin_names__"]) % admin:
        grid.append(1)
    builder.adjust(*grid)
    await msg.answer("Выберете нужную команду", reply_markup=builder.as_markup())
    return None


@router.callback_query(F.data.startswith("command_"))
async def send_info(callback: types.CallbackQuery, bot: Bot):

    result = await autorisation(bot, callback=callback)  # Авторизация пользователя
    if not result:
        return None
    
    user = find_user(callback.from_user.id)

    if callback.data.replace("command_", "") in LEVELS.keys() and user["access"] < LEVELS[callback.data.replace("command_", "")]:
        await log(callback, (f'Пользователь обладает правами доступа уровня {user["access"]}, нужен {LEVELS[callback.data.replace("command_", "")]}', ), bot)
        await callback.message.answer(f"Вы не обладаете нужными правами доступа")
        await callback.answer()
        return None
    await log(callback, (f'Выбран вариант {callback.data}',), bot)
    await callback.message.answer(info(callback.data.replace("command_", "")))
    await callback.answer()
    return None


@router.message(Command('cancel'))
async def stop(msg: Message, bot: Bot, state: FSMContext):

    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    await log(msg, ('Пользователь отменил команду',), bot)
    await state.clear()
    return None


#                                                                                   Рандомное число
@router.message(Command('random'))
async def start_handler(msg: Message, command: CommandObject, bot: Bot):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    if command.args:
        try:
            nums = tuple(map(int, command.args.split()[:3]))
            if len(nums) == 2:
                nums = (nums[0], nums[1] + 1, 1)
            elif len(nums) == 1:
                nums = (1, nums[0] + 1, 1)
        except Exception:
            await log(msg, ('Команда /random не получила чисел: ' + command.args, ), bot)
            nums = (0, 2, 1)
    else:
        nums = (0, 2, 1)
    try:
        text = ', '.join(map(str, sorted(sample(range(*nums[:2]), k=nums[2]))))
    except Exception:
        await log(msg, ('Команда /random получила некорректные данные: ' + command.args, ), bot)
        await msg.reply('Некорректные данные')
        return None
    await log(msg, ('Команда /random',), bot)
    await msg.reply(text)
    return None


#                                                                               Перевод в другую СС

@router.message(Command('numeral'))
async def start_handler(msg: Message, command: CommandObject, bot: Bot):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None
    
    args = command.args.split(' ') if command.args else []

    if len(args) < 2:
        await log(msg, ('Команда /numeral получила меньше двух аргументов',), bot)
        await msg.reply("Нужно ввести число и его систему счисления")
        return None
    elif len(args) == 2:
        if args[1] in ('double', 'float'):
            try:
                num, use = float(args[0].replace(',', '.')), args[1]
                res = sft(num, use)
                if not res[0]:
                    await log(msg, ('Команда /numeral могла допустить ошибку',), bot)
                    await msg.reply("Извини, произошла непредвиденная ошибка - напиши @markusha_v3")
                    return None
                line_1, line_2 = res[:4], hex(int(res[:4], 2))[2:].upper()
                for i in range(4, len(res), 4):
                    line_1 += '.' + res[i:i + 4]
                    line_2 += (' ' if i != 0 and (i // 4) % 2 == 0 else '') + hex(int(res[i:i + 4], 2))[2:].upper()
                await log(msg, (f'Команда /numeral перевела число в {use}', ), bot)
                await msg.reply("bin: " + line_1 + '\nhex: ' + line_2)
                return None
            except Exception as e:
                await log(msg, ('Команда /numeral получила некорректные аргументы', e), bot)
                await msg.reply("Нужно ввести число и его систему счисления")
                return None
        try:
            res = numeral(int(args[0]), int(args[1]))
        except Exception:
            await log(msg, ('Команда /numeral получила некорректные аргументы',), bot)
            await msg.reply("Нужно ввести число и его систему счисления")
            return None
    else:
        try:
            res = str(to_ten(args[0], int(args[1])))
            if args[2] != '10':
                res = numeral(int(res), int(args[2]))
        except Exception:
            await log(msg, ('Команда /numeral получила некорректные аргументы',), bot)
            await msg.reply("Нужно ввести число и его систему счисления")
            return None
    await log(msg, ('Команда /numeral завершила свою работу',
                    'Запрос:' + command.args, 'Ответ' + res), bot)
    await msg.reply(res)
    return None


@router.message(Command('post'))
async def start_handler(msg: Message, command: CommandObject, bot: Bot):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    if command.args:
        try:
            text = msg.text.replace("/post ", '').replace("(", '( ').replace(")", ' )').replace("  ", ' ').split(' ')
            output = ' '.join(get_RPN(text))
        except Exception:
            await log(msg, ('Команда /post получила некорректное выражение ' + command.args, ), bot)
            await msg.reply('Некорректные данные /post')
            return None
        await log(msg, ('Команда /post завершила работу',), bot)
        await msg.reply(output)
        return None
    else:
        await log(msg, ('Команда /post не получила выражение ' + command.args, ), bot)
        await msg.reply('Нужно ввести выражение')
        return None
