from aiogram import Router, Bot, types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder


from logs import do_log as log
from config import autorisation
from scripts.help import shorter


router_atom = Router()


TABLE = """H He
Li Be B C N O F Ne
Na Mg Al Si P S Cl Ar
K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr
Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe
Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn
Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og""".split()



class RequestATOM(StatesGroup):
    mode = State()

    current_atom = State()

    num_of_alpha = State()
    num_of_beta = State()


    mass = State()


@router_atom.message(Command("atom"))
async def data(msg: Message, bot: Bot):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Расписать атом на составляющие', callback_data='atom_info'))
    builder.add(types.InlineKeyboardButton(text='Найти энергию связи', callback_data='atom_energy'))
    builder.add(types.InlineKeyboardButton(text='α и β распад', callback_data='atom_decay'))
    builder.add(types.InlineKeyboardButton(text='Задача на период полураспада', callback_data='atom_half_decay'))
    builder.adjust(1, 1, 1, 1)
    await msg.reply('Что нужно сделать', reply_markup=builder.as_markup())
    await log(msg, (f'/atom запущена', ), bot)
    return None


@router_atom.callback_query(F.data.startswith("atom_"))
async def get_mode(callback: types.CallbackQuery, bot: Bot, state: FSMContext):

    result = await autorisation(bot, callback=callback)  # Авторизация пользователя
    if not result:
        return None

    await log(callback, (f'Выбран вариант {callback.data}',), bot)
    await callback.answer()
    await state.update_data(mode=callback.data.replace('atom_', ''))

    if callback.data == 'atom_half_decay':
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text='Сколько ядер осталось', callback_data='decay_future'))
        builder.add(types.InlineKeyboardButton(text='Сколько ядер было сначала', callback_data='decay_past'))
        builder.add(types.InlineKeyboardButton(text='Сколько времени прошло', callback_data='decay_time'))
        builder.add(types.InlineKeyboardButton(text='Время полураспада', callback_data='decay_period'))
        builder.adjust(1, 1, 1, 1)
        await callback.message.answer('Что просят найти?', reply_markup=builder.as_markup())
        await log(callback, (f'/atom попросила вопрос в задаче',), bot)
        return None
    await callback.message.answer(f'Введите информацию о атоме - обозначение, число сверху и число снизу.\nНапример "Li 6 3"')
    await state.set_state(RequestATOM.current_atom)
    return None

@router_atom.callback_query(F.data.startswith("decay_"))
async def get_decay(callback: types.CallbackQuery, bot: Bot, state: FSMContext):

    result = await autorisation(bot, callback=callback)  # Авторизация пользователя
    if not result:
        return None

    await log(callback, (f'Выбран вариант {callback.data}',), bot)
    await callback.answer()
    await state.update_data(mode=callback.data.replace('decay_', ''))

    text = ['Внимательно прочитай задачу',]


    if callback.data == 'decay_future':
        text.append('В ней будет дан период полураспада (например, 10 часов) - запишем его в дано как T')
        text.append('В ней будет дано время распада (например, 20 часов) - запишем его в дано как t')
        text.append('Если время распада нацело делится на период (то есть t можно поделить на T), то всё верно')
        text.append('В задаче будет дано количество ядер, которое было до начала распада - запишем его как N0 ("большая эн нулевое")')
        text.append('Запишем то, что нужно найти: N - ?')
        text.append('В решении нужно написать формулу: N = N0 / 2^(t / T)')
        text.append('Теперь подставляешь данные и получаешь ответ)')
        await callback.message.answer('\n'.join(text))
        await log(callback, (f'/atom помогла с задачей', *text), bot)
        return None
    if callback.data == 'decay_past':
        text.append('В ней будет дан период полураспада (например, 10 часов) - запишем его в дано как T')
        text.append('В ней будет дано время распада (например, 20 часов) - запишем его в дано как t')
        text.append('Если время распада нацело делится на период (то есть t можно поделить на T), то всё верно')
        text.append('В задаче будет дано количество ядер, которое осталось после распада - запишем его как N')
        text.append('Запишем то, что нужно найти: N0 ("большая эн нулевое") - ?')
        text.append('В решении нужно написать формулу: N = N0 / 2^(t / T)')
        text.append('Под этой строчкой пишешь следующую формулу: N0 = N * 2^(t / T)')
        text.append('Теперь подставляешь данные и получаешь ответ)')
        await callback.message.answer('\n'.join(text))
        await log(callback, (f'/atom помогла с задачей', *text), bot)
        return None
    if callback.data == 'decay_time':
        text.append('В ней будет дан период полураспада - запишем его в дано как T')
        text.append('В задаче будет дано количество ядер (например, 400), которое было до начала распада - запишем его как N0 ("большая эн нулевое")')
        text.append('В задаче будет дано количество ядер, которое осталось после распада (например, 100)- запишем его как N')
        text.append('Если количество ядер до распада нацело делится на количество ядер после (то есть N0 можно поделить на N), то всё верно')
        text.append('Запишем то, что нужно найти: t - ?')
        text.append('В решении нужно написать формулу: N = N0 / 2^(t / T)')
        text.append('Под этой строчкой пишешь следующую формулу: 2^(t / T) = N0 / N')
        text.append('Если посчитать то, что справа от равно, то получится число, которое делится на два (и является степенью двойки)')
        text.append('Найди логарифм этого числа по основанию два - проще говоря, напиши: (t / T) = (число, при возведение в которое, число два становится N0 / N)')
        text.append('Например, если N0 / N равно 8, то я запишу: (t / T) = 3 (потому что 2^3 = 8)')
        text.append('Теперь пишешь t = T * (то, что получилось в прошлом действии)')
        text.append('Считаешь и получаешь ответ)')
        await callback.message.answer('\n'.join(text))
        await log(callback, (f'/atom помогла с задачей', *text), bot)
        return None
    if callback.data == 'decay_period':
        text.append('В ней будет дано время распада - запишем его в дано как t')
        text.append('В задаче будет дано количество ядер (например, 400), которое было до начала распада - запишем его как N0 ("большая эн нулевое")')
        text.append('В задаче будет дано количество ядер, которое осталось после распада (например, 100)- запишем его как N')
        text.append('Если количество ядер до распада нацело делится на количество ядер после (то есть N0 можно поделить на N), то всё верно')
        text.append('Запишем то, что нужно найти: T - ?')
        text.append('В решении нужно написать формулу: N = N0 / 2^(t / T)')
        text.append('Под этой строчкой пишешь следующую формулу: 2^(t / T) = N0 / N')
        text.append('Если посчитать то, что справа от равно, то получится число, которое делится на два (и является степенью двойки)')
        text.append('Найди логарифм этого числа по основанию два - проще говоря, напиши: (t / T) = (число, при возведение в которое, число два становится N0 / N)')
        text.append('Например, если N0 / N равно 8, то я запишу: (t / T) = 3 (потому что 2^3 = 8)')
        text.append('Теперь пишешь T = t / (то, что получилось в прошлом действии)')
        text.append('Считаешь и получаешь ответ)')
        await callback.message.answer('\n'.join(text))
        await log(callback, (f'/atom помогла с задачей', *text), bot)
        return None


    

@router_atom.message(RequestATOM.current_atom)
async def get_atom(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None
    
    data = msg.text.split(' ')
    try:
        dct = {'name': data[0], 'A': int(data[1]), 'Z': int(data[2]), 'N': int(data[1]) - int(data[2])}
    except Exception:
        await log(msg, ('/atom - пользователь не передал информацию о атоме', msg.text), bot)
        await msg.answer(f'Введите информацию о атоме - обозначение, число сверху и число снизу.\nНапример "Li 6 3"')
        return None
    
    await log(msg, ('Команда /atom получила атом', msg.text), bot)
    if data[0] in TABLE and int(data[2]) - 1 != TABLE.index(data[0]):
        if int(data[2]) <= len(TABLE):
            await log(msg, ('Атом может не совпадать',), bot)
            await msg.answer(f'Порядковый номер и название атома не совпадают (элемент № {data[2]} - {TABLE[int(data[2]) - 1]}) - проверь всё ещё раз.\n' +
                                'Если нашёл ошибку, то начни заного')
        else:
            await log(msg, ('Атом может не совпадать',), bot)
            await msg.answer(f'Порядковый номер и название атома не совпадают (элемента с таким большим порядковым номером нет в таблице) - проверь всё ещё раз.\n' +
                                'Если нашлась ошибка, начни заного')

    mode = (await state.get_data())["mode"]
    if mode == 'info':
        await log(msg, ('/atom вывела информацию о атоме', msg.text), bot)
        await msg.reply(f"A = {dct['A']}, Z = {dct['Z']}, N = {dct['N']}")
        return None
    await state.update_data(current_atom=dct)
    if mode == 'energy':
        await log(msg, ('/atom попросила написать массу ядра', msg.text), bot)
        await msg.reply('Напишите массу ядра в а.е.м. (единицу измерения писать не нужно). Она должна быть дана в условии - в ином случае введите "-".\n' +
                        'Например, если в задаче написано Мя = 6, 15089 а.е.м., то нужно ввести "6.15089"')
        await state.set_state(RequestATOM.mass)
        return None
    if mode == 'decay':
        await log(msg, ('/atom попросила написать количество распадов', msg.text), bot)
        await msg.reply('Напишите сколько нужно провести α-распадов')
        await state.set_state(RequestATOM.num_of_alpha)
        return None


@router_atom.message(RequestATOM.mass)
async def get_mass(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None
    
    data = await state.get_data()
    name, A, Z, N = data["current_atom"]['name'], data["current_atom"]['A'], data["current_atom"]['Z'], data["current_atom"]['N']
    try:
        if msg.text == '-':
            mass = float(A)
        else:
            mass = float(msg.text.replace(',', '.').replace(' ', ''))
    except Exception:
        await log(msg, ('/atom - пользователь не передал нужную информацию', msg.text), bot)
        await msg.reply('Напишите массу ядра в а.е.м. (единицу измерения писать не нужно). Она должна быть дана в условии - в ином случае введите "-".\n' +
                        'Например, если в задаче написано Мя = 6,15089 а.е.м., то нужно ввести "6.15089"')
        return None
    
    m_p, m_n, m_a = 1.6726, 1.6749, 1.6606

    text = []

    text.append('Дано:')
    text.append(f'{name} (A = {A}, Z = {Z}, N = {N})')
    text.append(F'Mp = {m_p} кг')
    text.append(F'Mn = {m_n} кг')
    text.append(F'Mя = {mass} * {m_a} кг')
    text.append('E(св) - ?\n')
    text.append('Решение: E(св) = (Z * Mp + N * Mn - Mя) * С^2')
    text.append(f'Е(св) = ({Z} * {m_p} * 10^-27 кг + {N} * {m_n} * 10^-27 кг - {mass} * {m_a} * 10^-27 кг) * (3 * 10^8 м/с)^2 =')
    text.append(f'= ({shorter(Z * m_p, 4)} * 10^-27 кг + {shorter(N * m_n, 4)} * 10^-27 кг - {shorter(mass * m_a, 4)} * 10^-27 кг) * 9 * 10^16 (м/с)^2 =')
    delta_m = shorter(Z * m_p + N * m_n - shorter(mass * m_a, 4), 4)
    text.append(f'= {delta_m} кг * 9 * 10^-11 (м/с)^2 =')
    text.append(f'= {shorter(delta_m * 9, 4)} * 10^-11 Дж ---- Конечный ответ')
    # text.append('E(уд) = E(св) / A ---- если простят найти удельную энергию')
    # text.append(f'E(уд) = ({shorter(delta_m * 9 * 10, 4)} * 10^-12 Дж) / {A} =')
    # text.append(f'{shorter(delta_m * 9 * 10 / A, 4)} * 10^-12 Дж')

    await msg.reply('\n'.join(text))
    await log(msg, ('/atom - работа закончена', *text), bot)
    await state.clear()
    return None


@router_atom.message(RequestATOM.num_of_alpha)
async def do_decay(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None
    
    try:
        alpha = int(msg.text)
    except Exception:
        await log(msg, ('/atom - пользователь не передал нужную информацию', msg.text), bot)
        await msg.reply('Напишите сколько нужно провести α-распадов')
        return None
    
    await state.update_data(num_of_alpha=alpha)
    await log(msg, ('/atom получила количество α-распадов', msg.text), bot)
    await msg.reply('Напишите сколько нужно провести β-распадов')
    await state.set_state(RequestATOM.num_of_beta)
    return None


@router_atom.message(RequestATOM.num_of_beta)
async def do_decay(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None
    
    try:
        beta = int(msg.text)
    except Exception:
        await log(msg, ('/atom - пользователь не передал нужную информацию', msg.text), bot)
        await msg.reply('Напишите сколько нужно провести β-распадов')
        return None

    data = await state.get_data()
    name, A, Z, alpha = data["current_atom"]['name'], data["current_atom"]['A'], data["current_atom"]['Z'], data["num_of_alpha"]
    text = ['Для удобства массовое число (то, что сверху) и порядковый номер (то, что снизу) будут написаны в скобках после атома',
            'Например, "Li (6 3)"\n']
    
    text.append('α-распады:')
    for _ in range(alpha):
        new_atom = TABLE[TABLE.index(name) - 2]
        text.append(f'{name} ({A} {Z}) = {new_atom} ({A - 4} {Z - 2}) + He (4, 2)')
        name = new_atom
        A -= 4
        Z -= 2
    
    text.append('\n')
    
    text.append('β-распады:')
    for _ in range(beta):
        new_atom = TABLE[TABLE.index(name) + 1]
        text.append(f'{name} ({A} {Z}) = {new_atom} ({A} {Z + 1}) + e (0, -1)')
        name = new_atom
        Z += 1
    
    await log(msg, ('/atom закончила распады', *text), bot)
    await msg.reply('\n'.join(text))
    await state.clear()
    return None