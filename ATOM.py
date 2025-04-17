from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup



from logs import do_log as log
from users import get_users
from config import last_massage
from free_handler import free_handler
from scripts.help import shorter


router_atom = Router()


class RequestATOM(StatesGroup):
    atom = State()
    mass = State()



@router_atom.message(Command("atom"))
async def starting(msg: Message, bot: Bot, state: FSMContext):
    global INFO
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    last_massage[msg.from_user.id] = ('atom', )

    await log(msg, ('Команда /atom начала свою работу', ), bot)
    await msg.reply('Введите обозначение, массовое число (цифра сверху) и порядковый номер (цифра снизу) через пробел. Например, для лития нужно ввести "Li 6 3"')
    await state.set_state(RequestATOM.atom)
    return None
    


@router_atom.message(RequestATOM.atom)
async def get_atom(msg: Message, bot: Bot, state: FSMContext):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if last_massage[msg.from_user.id] != ("atom", ):
        await state.clear()
        await free_handler(msg, bot)
        return None

    data = msg.text.split(' ')
    try:
        dct = {'name': data[0], 'A': int(data[1]), 'Z': int(data[2]), 'N': int(data[1]) - int(data[2])}
    except Exception:
        await log(msg, ('/atom - пользователь не передал нужную информацию', msg.text), bot)
        await msg.reply("Введите обозначение, массовое число (цифра сверху) и порядковый номер (цифра снизу) через пробел. Например, для лития нужно ввести Li 6 3")
        return None
    await log(msg, ('Команда /atom получила атом', msg.text), bot)
    await msg.reply('Напишите массу ядра в а.е.м. (единицу измерения писать не нужно). Она должна быть дана в условии - в ином случае введите "-"')
    await state.update_data(atom=dct)
    await state.set_state(RequestATOM.mass)
    return None


@router_atom.message(RequestATOM.mass)
async def get_mass(msg: Message, bot: Bot, state: FSMContext):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)
    
    if last_massage[msg.from_user.id] != ("atom", ):
        await state.clear()
        await free_handler(msg, bot)
        return None
    data = await state.get_data()
    A, Z, N = data['atom']['A'], data['atom']['Z'], data['atom']['N']
    try:
        if msg.text == '-':
            mass = float(A)
        else:
            mass = float(msg.text.replace(',', '.'))
    except Exception:
        await log(msg, ('/atom - пользователь не передал нужную информацию', msg.text), bot)
        await msg.reply('Напишите массу ядра в а.е.м. (единицу измерения писать не нужно). Она должна быть дана в условии - в ином случае введите "-"')
        return None
    m_p, m_n, m_a = 1.6726, 1.6749, 1.6606


    text = 'Решение: E(св.) = (Z * Mp + N * Mn - Mя) * С^2\n'
    text += f'Е(св.) = ({Z} * {m_p} * 10^-27 кг + {N} * {m_n} * 10^-27 кг - {mass} * {m_a} * 10^-27 кг) * (3 * 10^8 м/с)^2 =\n'
    text += f'= ({shorter(Z * m_p, 4)} * 10^-27 кг + {shorter(N * m_n, 4)} * 10^-27 кг - {shorter(mass * m_a, 4)} * 10^-27 кг) * 9 * 10^16 (м/с)^2 =\n'
    delta_m = shorter(Z * m_p + N * m_n - shorter(mass * m_a, 4), 4)
    text += f'= {delta_m} кг * 9 * 10^-11 (м/с)^2 =\n'
    text += f'= {shorter(delta_m * 9, 4)} * 10^-11 Дж ---- Конечный ответ\n'
    text += 'E(уд.) = E(св) / A ---- если простят найти удельную энергию\n'
    text += f'E(уд.) = ({shorter(delta_m * 9 * 10, 4)} * 10^-12 Дж) / {A} =\n'
    text += f'{shorter(delta_m * 9 * 10 / A, 4)} * 10^-12 Дж'
    await msg.reply(text)
    await log(msg, ('/atom - работа закончена', text), bot)
    await state.clear()
    return None
    