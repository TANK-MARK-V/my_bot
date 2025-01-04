from aiogram import types, F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import COMMANDS, info, LEVELS, last_massage
from logs import do_log as log

from STI import sti
from coding import encode, decode
from users import get_users
from EVO import step

router = Router()

#                                                                                   Старт
@router.message(CommandStart())
async def start_handler(msg: Message):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    last_massage[msg.from_user.id] = ("start", )
    log(msg, ('команда /start',))
    await msg.answer('Чтобы узнать, что я умею используй "/info"')

#                                                                           Информация о командах
@router.message(Command("info"))
async def information(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg, info=msg.from_user.username)  # Получение информации о пользователе
    
    if command.args and command.args in COMMANDS['__names__']:
        log(msg, (f'команда /info {command.args}',))
        await msg.reply(info(command=command.args))
        return None
    if command.args and command.args in COMMANDS['__admin_names__']:
        if user[2] >= LEVELS[command.args]:
            last_massage[msg.from_user.id] = ("info_one", )
            log(msg, (f'команда /info {command.args}',))
            await msg.reply(info(command=command.args))
            return None
        else:
            log(msg, (f'Пользователь обладает правами администратора уровня {user[2]}, нужен {LEVELS[command.args]}', ))
            await msg.reply(f"Вы не обладаете нужными правами администратора")
            return None
    log(msg, ('команда /info',))
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



@router.callback_query(F.data.startswith("command_"))
async def send_info(callback: types.CallbackQuery):
    log(callback, (f'Выбран вариант {callback.data}',))
    await callback.message.answer(info(callback.data.replace("command_", '')))
    await callback.answer()


#                                                                               Всё остальное
@router.message()
async def message_handler(msg: Message, bot: Bot):
    global last_massage
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)
    
    if msg.from_user.id in last_massage.keys():
        last = last_massage[msg.from_user.id]
        if last[0] == "chat" and len(last) > 1:
            wanted = last[1]
            log(msg, (f'/admin_chat - пользователь написал другому пользователю:', msg.text))
            await bot.send_message(wanted[0], msg.text) 
            await msg.reply(f"Сообщение успешно отправлено")
            return None
        
        if last[0] == "sti" and len(last) > 1 and msg.text in ('0', '1', '-'):
            args = last[1].copy()
            if msg.text in ('0', '1'):
                args.append(msg.text)
            try:
                out = sti(*args)
            except Exception as e:
                last_massage[msg.from_user.id] = ("sti", )
                log(msg, ('Команда /sti:', f'ОШИБКА - {e}, запрос - {args[0]}'), error=True)
                await msg.reply("Что-то пошло не так")
                return None
            log(msg, ('Команда /sti выполнила свою работу:', args[0]))
            await msg.reply(out)
            return None
        
        if last[0] == "encode" and len(last) > 1:
            text = msg.text
            if '<' in text:
                text = text.replace('<', '')
            if '>' in text:
                text = text.replace('>', '')
            if not text:
                log(msg, ('Команда /encode не получила текста',))
                await msg.reply("Нужно ввести текст для зашифровки")
                return None
            try:
                out = encode(text)
            except Exception as e:
                log(msg, ('Команда /encode:', f'ОШИБКА - {e}, запрос - {msg.text}'), error=True)
                await msg.reply("Что-то пошло не так")
                return None
            log(msg, ('Команда /encode выполнила свою работу:', text))
            await msg.reply(out)
            return None
        
        if last[0] == "decode" and len(last) > 1:
            if not msg.text:
                    log(msg, ('Команда /decode не получила текста',))
                    await msg.reply("Нужно ввести текст для расшифровки")
                    return None
            try:
                out = decode(msg.text)
                if '<' in out:
                    out = out.replace('<', '')
                if '>' in out:
                    out = out.replace('>', '')
                if not out:
                    log(msg, ('Команда /decode оставила пустое сообщение',))
                    await msg.reply('Сообщение оказалось пустым')
                    return None
            except Exception as e:
                log(msg, ('Команда /decode:', f'ОШИБКА - {e}, запрос - {msg.text}'), error=True)
                await msg.reply("Что-то пошло не так")
                return None
            log(msg, ('Команда /decode выполнила свою работу:', msg.text))
            await msg.reply(out)
            return None
        
        if last[0] == 'evo' and len(last) > 1:
            await step(last, msg)
            return None
            # if last[1] == 1:
            #     options = msg.text.split('\n')
            #     if len(options) < 2:
            #         log(msg, ('Команда /evo получила меньше двух команд', msg.text))
            #         await msg.reply("Нужно ввести не меньше двух команд")
            #         return None
            #     options = tuple(map(lambda x: ' ' + x if x[0] != ' ' else x, options))
            #     last_massage[msg.from_user.id] = ("evo", 2, options)
            #     log(msg, ('Команда /evo получила команды', msg.text))
            #     await msg.reply("Введите начальное и конечное число")
            #     return None
            # if last[1] == 2:
            #     options = last_massage[msg.from_user.id][2]
            #     numbers = msg.text.split(' ')
            #     if len(numbers) != 2:
            #         log(msg, ('Команда /evo получила не два числа', msg.text))
            #         await msg.reply("Нужно ввести только два числа: начальное и конечное")
            #         return None
            #     try:
            #         numbers = tuple(map(lambda x: int(x), numbers))
            #     except Exception:
            #         log(msg, ('Команда /evo получила не числа', msg.text))
            #         await msg.reply("Нужно ввести только два числа: начальное и конечное")
            #         return None
            #     last_massage[msg.from_user.id] = ("evo", 3, options, numbers)
            #     log(msg, ('Команда /evo получила числа', msg.text))
            #     await msg.reply('Введите числа, которые должна содержать траектория программы. Если таких чисел нет, введите "-"')
            #     return None
            # if last[1] == 3:
            #     options, numbers = last_massage[msg.from_user.id][2], last_massage[msg.from_user.id][3]
            #     throughs = None if msg.text == '-' else msg.split(' ')
            #     if throughs:
            #         try:
            #             throughs = tuple(map(lambda x: int(x), throughs))
            #         except Exception:
            #             log(msg, ('Команда /evo получила не "обязательные" числа', msg.text))
            #             await msg.reply('Введите числа, которые должна содержать траектория программы. Если таких чисел нет, введите "-"')
            #             return None
            #     last_massage[msg.from_user.id] = ("evo", 4, options, numbers, throughs)
            #     log(msg, ('Команда /evo получила "обязательные" числа', msg.text))
            #     await msg.reply('Введите числа, которые должна избегать траектория программы. '
            #     + 'Если траектория программы не должна содержать цифру, начните сообщение с "+". '
            #     + 'Если таких чисел нет, введите "-"')
            #     return None
            # if last[1] == 4:
            #     options, numbers, throughs = last_massage[msg.from_user.id][2], last_massage[msg.from_user.id][3], last_massage[msg.from_user.id][4]
            #     if msg.text[0] == '+':
            #         escapes = set(msg.text[1:])
            #         if len(escapes - set('0123456789')):
            #             log(msg, ('Команда /evo получила не "избегаемые" цифры', msg.text))
            #             await msg.reply('Введите числа или цифры, которые должна избегать траектория программы. Если таких чисел нет, введите "-"')
            #             return None
            #     else:
            #         escapes = None if msg.text == '-' else msg.split(' ')
            #         if escapes:
            #             try:
            #                 escapes = tuple(map(lambda x: int(x), escapes))
            #             except Exception:
            #                 log(msg, ('Команда /evo получила не "избегаемые" числа', msg.text))
            #                 await msg.reply('Введите числа или цифры, которые должна избегать траектория программы. Если таких чисел нет, введите "-"')
            #                 return None
            #     last_massage[msg.from_user.id] = ("evo", 5, options, numbers, throughs, escapes)
            #     log(msg, ('Команда /evo получила "избегаемые" числа или цифры', msg.text))
            #     await msg.reply('Введите номер команды, которая не должна повторяться. Если такого условия нет, введите "-"')
            #     return None
            # if last[1] == 5:
            #     options, numbers = last_massage[msg.from_user.id][2], last_massage[msg.from_user.id][3]
            #     throughs, escapes = last_massage[msg.from_user.id][4], last_massage[msg.from_user.id][5]
            #     double = 0 if msg.text == '-' else msg.text
            #     try:
            #         double = int(double)
            #     except Exception:
            #         log(msg, ('Команда /evo получила не номер команды', msg.text))
            #         await msg.reply('Введите номер команды, которая не должна повторяться. Если такого условия нет, введите "-"')
            #         return None
            #     if double > len(options) or double < 0:
            #         log(msg, ('Команда /evo получила номер несуществующей команды', msg.text))
            #         await msg.reply('Введите номер команды, которая не должна повторяться. Если такого условия нет, введите "-"')
            #         return None
            #     log(msg, ('Команда /evo получила номер команды', msg.text))
            #     try:
            #         out = str(EVO(options, through=throughs, escape=escapes, inverse=numbers[0] > numbers[1], double=double).evo(numbers[0], numbers[1]))
            #     except Exception as e:
            #         last_massage[msg.from_user.id] = ("evo", )
            #         log(msg, ('Команда /evo:', f'ОШИБКА - {e}'), error=True)
            #         await msg.reply("Что-то пошло не так")
            #         return None
            #     log(msg, ('Команда /evo выполнила свою работу', ))
            #     await msg.reply(out)
            #     return None

    last_massage[msg.from_user.id] = ("empty", )
    log(msg, ('Пустое сообщение:', msg.text))
    await msg.answer(f"Твой ID, имя, фамилия и username: {msg.from_user.id}, {msg.from_user.full_name}, {msg.from_user.username},")