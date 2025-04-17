from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from logs import do_log as log
from users import get_users
from config import last_massage
from free_handler import free_handler

from scripts.EVO.EVO import EVO
router_evo = Router()


class RequestEVO(StatesGroup):
    options = State()
    numbers = State()
    throughs = State()
    escapes = State()
    double = State()


@router_evo.message(Command("evo"))
async def starting(msg: Message, bot: Bot, state: FSMContext):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)
    
    last_massage[msg.from_user.id] = ("evo", )

    await log(msg, ('Команда /evo начала свою работу', ), bot)
    await msg.reply("Введите команды")
    await state.set_state(RequestEVO.options)
    return None


@router_evo.message(RequestEVO.options)
async def get_options(msg: Message, bot: Bot, state: FSMContext):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if last_massage[msg.from_user.id] != ("evo", ):
        await state.clear()
        await free_handler(msg, bot)
        return None

    options = msg.text.split('\n')
    if len(options) < 2:
        await log(msg, ('Команда /evo получила меньше двух команд', msg.text), bot)
        await msg.reply("Нужно ввести не меньше двух команд")
        return None
    for opt in options:
        if '*0' in opt.replace(' ', ''):
            await log(msg, ('Команда /evo получила команду умножить на ноль', msg.text), bot)
            await msg.reply("Эти команды не приводят к ответу")
            return None
        if '/0' in opt.replace(' ', ''):
            await log(msg, ('Команда /evo получила команду поделить на ноль', msg.text), bot)
            await msg.reply("На ноль делить нельзя")
            return None
        if '=' in opt:
            await log(msg, ('Команда /evo получила команду, содержащую "="', msg.text), bot)
            await msg.reply("Некорректные команды")
            return None
    options = tuple(map(lambda x: ' ' + x if x[0] != ' ' else x, options))
    await log(msg, ('Команда /evo получила команды', msg.text), bot)
    await msg.reply("Введите начальное и конечное число")
    await state.update_data(options=options)
    await state.set_state(RequestEVO.numbers)
    return None


@router_evo.message(RequestEVO.numbers)
async def get_numbers(msg: Message, bot: Bot, state: FSMContext):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)
    
    if last_massage[msg.from_user.id] != ("evo", ):
        await state.clear()
        await free_handler(msg, bot)
        return None

    numbers = msg.text.split(' ')
    if len(numbers) != 2:
        await log(msg, ('Команда /evo получила не два числа', msg.text), bot)
        await msg.reply("Нужно ввести только два числа: начальное и конечное")
        return None
    try:
        numbers = tuple(map(lambda x: int(x), numbers))
    except Exception:
        await log(msg, ('Команда /evo получила не числа', msg.text), bot)
        await msg.reply("Нужно ввести только два числа: начальное и конечное")
        return None
    await log(msg, ('Команда /evo получила числа', msg.text), bot)
    await msg.reply('Введите числа, которые должна содержать траектория программы. Если таких чисел нет, введите "-"')
    await state.update_data(numbers=numbers)
    await state.set_state(RequestEVO.throughs)
    return None


@router_evo.message(RequestEVO.throughs)
async def get_throughs(msg: Message, bot: Bot, state: FSMContext):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if last_massage[msg.from_user.id] != ("evo", ):
        await state.clear()
        await free_handler(msg, bot)
        return None

    throughs = None if msg.text == '-' else msg.text.split(' ')
    if throughs:
        try:
            throughs = tuple(map(lambda x: int(x), throughs))
        except Exception:
            await log(msg, ('Команда /evo получила не "обязательные" числа', msg.text), bot)
            await msg.reply('Введите числа, которые должна содержать траектория программы. Если таких чисел нет, введите "-"')
            return None
    await log(msg, ('Команда /evo получила "обязательные" числа', msg.text), bot)
    await msg.reply('Введите числа, которые должна избегать траектория программы. '
    + 'Если траектория программы не должна содержать цифру, начните сообщение с "+". '
    + 'Если таких чисел нет, введите "-"')
    await state.update_data(throughs=throughs)
    await state.set_state(RequestEVO.escapes)
    return None


@router_evo.message(RequestEVO.escapes)
async def get_escapes(msg: Message, bot: Bot, state: FSMContext):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if last_massage[msg.from_user.id] != ("evo", ):
        await state.clear()
        await free_handler(msg, bot)
        return None

    if msg.text[0] == '+':
        escapes = set(msg.text[1:])
        if len(escapes - set('0123456789')):
            await log(msg, ('Команда /evo получила не "избегаемые" цифры', msg.text), bot)
            await msg.reply('Введите числа или цифры, которые должна избегать траектория программы. Если таких чисел нет, введите "-"')
            return None
    else:
        escapes = None if msg.text == '-' else msg.text.split(' ')
        if escapes:
            try:
                escapes = tuple(map(lambda x: int(x), escapes))
            except Exception:
                await log(msg, ('Команда /evo получила не "избегаемые" числа', msg.text), bot)
                await msg.reply('Введите числа или цифры, которые должна избегать траектория программы. Если таких чисел нет, введите "-"')
                return None
    await log(msg, ('Команда /evo получила "избегаемые" числа или цифры', msg.text), bot)
    await msg.reply('Введите номер команды, которая не должна повторяться. Если такого условия нет, введите "-"')
    await state.update_data(escapes=escapes)
    await state.set_state(RequestEVO.double)
    return None


@router_evo.message(RequestEVO.double)
async def get_escapes(msg: Message, bot: Bot, state: FSMContext):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if last_massage[msg.from_user.id] != ("evo", ):
        await state.clear()
        await free_handler(msg, bot)
        return None

    double = 0 if msg.text == '-' else msg.text
    data = await state.get_data()
    options, numbers, throughs, escapes = data['options'], data['numbers'], data['throughs'], data['escapes']
    try:
        double = int(double)
    except Exception:
        await log(msg, ('Команда /evo получила не номер команды', msg.text), bot)
        await msg.reply('Введите номер команды, которая не должна повторяться. Если такого условия нет, введите "-"')
        return None
    if double > len(options) or double < 0:
        await log(msg, ('Команда /evo получила номер несуществующей команды', msg.text), bot)
        await msg.reply('Введите номер команды, которая не должна повторяться. Если такого условия нет, введите "-"')
        return None
    await log(msg, ('Команда /evo получила номер команды', msg.text), bot)
    try:
        out = str(EVO(options, through=throughs, escape=escapes, inverse=numbers[0] > numbers[1], double=double).evo(numbers[0], numbers[1]))
    except Exception as e:
        last_massage[msg.from_user.id] = ("evo", )
        await log(msg, ('Команда /evo:', f'ОШИБКА - {e}'), bot, error=True)
        await msg.reply("Что-то пошло не так")
        return None
    last_massage[msg.from_user.id] = ("evo", )
    await log(msg, ('Команда /evo выполнила свою работу', ), bot)
    await msg.reply(out)
    await state.clear()
    return None