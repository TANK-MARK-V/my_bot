from aiogram import F, Router, Bot
# Работа с сообщениями
from aiogram.types import Message
from aiogram.filters import Command
# Работа кнопками
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
# Работа с FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from scripts.Logs import autorisation
from scripts.help import shorter


# Таблица Менделеева
TABLE = """H He
Li Be B C N O F Ne
Na Mg Al Si P S Cl Ar
K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr
Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe
Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn
Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og""".split()


# Помощь на задачки, которые тяжело решать через бота
TEXT_TASK_HELP = {
    "decay_after": ["В ней будет дан период полураспада (например, 10 часов) - запишем его в дано как T",
                     "В ней будет дано время распада (например, 20 часов) - запишем его в дано как t",
                     "Если время распада нацело делится на период (то есть t можно поделить на T), то всё верно",
                     "В задаче будет дано количество ядер, которое было до начала распада - запишем его как N0 (\"большая эн нулевое\")",
                     "Запишем то, что нужно найти: N - ?",
                     "В решении нужно написать формулу: N = N0 / 2^(t / T)",
                     "Теперь подставляешь данные и получаешь ответ)"],

    "decay_before": ["В ней будет дан период полураспада (например, 10 часов) - запишем его в дано как T",
                   "В ней будет дано время распада (например, 20 часов) - запишем его в дано как t",
                   "Если время распада нацело делится на период (то есть t можно поделить на T), то всё верно",
                   "В задаче будет дано количество ядер, которое было до начала распада - запишем его как N0 (\"большая эн нулевое\")",
                   "Запишем то, что нужно найти: N0 (\"большая эн нулевое\") - ?",
                   "В решении нужно написать формулу: N = N0 / 2^(t / T)",
                   "Под этой строчкой пишешь следующую формулу: N0 = N * 2^(t / T)",
                   "Теперь подставляешь данные и получаешь ответ)"],
    
    "decay_time": ["В ней будет дан период полураспада - запишем его в дано как T",
                   "В задаче будет дано количество ядер (например, 400), которое было до начала распада - запишем его как N0 (\"большая эн нулевое\")",
                   "В задаче будет дано количество ядер, которое осталось после распада (например, 100)- запишем его как N",
                   "Если количество ядер до распада нацело делится на количество ядер после (то есть N0 можно поделить на N), то всё верно",
                   "Запишем то, что нужно найти: t - ?",
                   "В решении нужно написать формулу: N = N0 / 2^(t / T)",
                   "Под этой строчкой пишешь следующую формулу: 2^(t / T) = N0 / N",
                   "Если посчитать то, что справа от равно, то получится число, которое делится на два (и является степенью двойки)",
                   "Найди логарифм этого числа по основанию два - проще говоря, напиши: (t / T) = (число, при возведение в которое, число два становится N0 / N)",
                   "Теперь пишешь t = T * (то, что получилось в прошлом действии)",
                   "Считаешь и получаешь ответ)"],

    "decay_period": ["В ней будет дано время распада - запишем его в дано как t",
                     "В задаче будет дано количество ядер (например, 400), которое было до начала распада - запишем его как N0 (\"большая эн нулевое\")",
                     "В задаче будет дано количество ядер, которое осталось после распада (например, 100)- запишем его как N",
                     "Если количество ядер до распада нацело делится на количество ядер после (то есть N0 можно поделить на N), то всё верно",
                     "Запишем то, что нужно найти: T - ?",
                     "В решении нужно написать формулу: N = N0 / 2^(t / T)",
                     "Под этой строчкой пишешь следующую формулу: 2^(t / T) = N0 / N",
                     "Если посчитать то, что справа от равно, то получится число, которое делится на два (и является степенью двойки)",
                     "Найди логарифм этого числа по основанию два - проще говоря, напиши: (t / T) = (число, при возведение в которое, число два становится N0 / N)",
                     "Например, если N0 / N равно 8, то я запишу: (t / T) = 3 (потому что 2^3 = 8)",
                     "Теперь пишешь T = t / (то, что получилось в прошлом действии)",
                     "Считаешь и получаешь ответ)"]
}


router_atom = Router()  # Обработчик ATOM


class RequestATOM(StatesGroup):  # Сбор информации для решения задач
    mode = State()

    current_atom = State()

    num_of_alpha = State()
    num_of_beta = State()

    mass = State()


@router_atom.message(Command("atom"))
async def starting(msg: Message, bot: Bot):  # Начало работы
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None
    
    # Создаём кнопки
    builder = InlineKeyboardBuilder()
    builder.button(text="Расписать атом на составляющие", callback_data="atom_info")
    builder.button(text="Найти энергию связи", callback_data="atom_energy")
    builder.button(text="α и β распад", callback_data="atom_decay")
    builder.button(text="Задача на период полураспада", callback_data="atom_half_decay")
    builder.adjust(1, 1, 1, 1)

    await msg.reply("Что нужно сделать", reply_markup=builder.as_markup())
    await user.log("Command /atom: начало работы")


@router_atom.callback_query(F.data.startswith("atom_"))
async def get_mode(callback: CallbackQuery, bot: Bot, state: FSMContext):  # Обработчик кнопок /atom
    user = await autorisation(info=callback, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    if callback.data == "atom_half_decay":  # Если это задача на период полураспада
        # Создаём ещё кнопки
        builder = InlineKeyboardBuilder()
        builder.button(text="Сколько ядер осталось", callback_data="decay_after")
        builder.button(text="Сколько ядер было сначала", callback_data="decay_before")
        builder.button(text="Сколько времени прошло", callback_data="decay_time")
        builder.button(text="Время полураспада", callback_data="decay_period")
        builder.adjust(1, 1, 1, 1)

        await callback.message.answer("Что просят найти?", reply_markup=builder.as_markup())
    else:
        await callback.message.answer("Введите информацию о атоме - обозначение, число сверху и число снизу.\nНапример \"Li 6 3\"")
        await state.update_data(mode=callback.data.replace("atom_", ''))
        await state.set_state(RequestATOM.current_atom)
    
    await callback.answer()
    await user.log("Callback /atom: выбран вариант " + callback.data)


@router_atom.callback_query(F.data.startswith("decay_"))
async def get_decay(callback: CallbackQuery, bot: Bot, state: FSMContext):  # Обработчик кнопок для задач на полураспад
    user = await autorisation(info=callback, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    await state.update_data(mode=callback.data.replace('decay_', ''))

    text = ['Внимательно прочитай задачу',]
    text += TEXT_TASK_HELP[callback.data]
    await callback.message.answer('\n'.join(text))
    await callback.answer()
    await user.log("Callback /atom.decay: помощь с текстовой задачей " + callback.data)


@router_atom.message(RequestATOM.current_atom)
async def get_atom(msg: Message, bot: Bot, state: FSMContext):  # Получение информации о нужном атоме
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None
    
    data = msg.text.split(' ')
    try:
        dct = {"name": data[0], 'A': int(data[1]), 'Z': int(data[2]), 'N': int(data[1]) - int(data[2])}
    except Exception:
        await user.log("FSM /atom.current_atom: пользователь не передал информацию о атоме", msg.text)
        await msg.answer("Введите информацию о атоме - обозначение, число сверху и число снизу.\nНапример \"Li 6 3\"")
        return None
    
    problem = False  # Проверим, совпадает ли номер и название атома
    if data[0] in TABLE and int(data[2]) - 1 != TABLE.index(data[0]):  # Не совпадают
        # Напишем текст для пользователя
        problem = ["Порядковый номер и название атома не совпадают "]
        if int(data[2]) <= len(TABLE):
            problem.append(f"(элемент № {data[2]} - {TABLE[int(data[2]) - 1]})")
        else:
            problem.append("(элемента с таким большим порядковым номером нет в таблице)")
        problem.append(" - проверь всё ещё раз.\n" + "Если нашёл ошибку, то начни заного")
        problem = ''.join(problem)
        await msg.answer(problem)
        await user.log('Атом может не совпадать')
    await user.log("FSM /atom.current_atom: получен атом", msg.text, repr(dct), problem if problem else "Номер и название атома совпадают")

    mode = (await state.get_data())["mode"]
    await state.update_data(current_atom=dct)
    if mode == "info":
        answer_text = f"A = {dct['A']}, Z = {dct['Z']}, N = {dct['N']}"
        await msg.reply(f"A = {dct['A']}, Z = {dct['Z']}, N = {dct['N']}")
        log_text = ["FSM /atom.current_atom: пользователь получил информацию о атоме", msg.text, answer_text]
    elif mode == "energy":
        answer_text = ''.join(["Напишите массу ядра в а.е.м. (единицу измерения писать не нужно). ",
                       "Она должна быть дана в условии - в ином случае введите \"-\".\n",
                       "Например, если в задаче написано Мя = 6, 15089 а.е.м., то нужно ввести \"6.15089\""])
        await state.set_state(RequestATOM.mass)
        log_text = ["FSM /atom.current_atom: помощь с нахождением энергии связи", msg.text]
    elif mode == "decay":
        answer_text = "Напишите сколько нужно провести α-распадов"
        await state.set_state(RequestATOM.num_of_alpha)
        log_text = ["FSM /atom.current_atom: помощь с распадами", msg.text]
    
    await msg.reply(answer_text)
    await user.log(*log_text)


@router_atom.message(RequestATOM.mass)
async def get_mass(msg: Message, bot: Bot, state: FSMContext):  # Получение массы атома и решение задачи о энергии связи
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None
    
    data = await state.get_data()  # Получим данные о атоме
    name, A, Z, N = data["current_atom"]["name"], data["current_atom"]["A"], data["current_atom"]["Z"], data["current_atom"]["N"]
    m_p, m_n, m_a = 1.6726, 1.6749, 1.6606  # Константы массы
    
    try:  # Проверим корректность информации
        if msg.text == '-':
            mass = float(A)
        else:
            mass = float(msg.text.replace(',', '.').replace(' ', ''))
    except Exception:
        await msg.reply("Напишите массу ядра в а.е.м. (единицу измерения писать не нужно). Она должна быть дана в условии - в ином случае введите \"-\".\n" +
                        "Например, если в задаче написано Мя = 6, 15089 а.е.м., то нужно ввести \"6.15089\"")
        await user.log("FSM /atom.mass: пользователь не передал нужную информацию", msg.text)
        return None
    
    text = []
    text.append("Дано:")
    text.append(f"{name} (A = {A}, Z = {Z}, N = {N})")
    text.append(F"Mp = {m_p} кг")
    text.append(F"Mn = {m_n} кг")
    text.append(F"Mя = {mass} * {m_a} кг")
    text.append("E(св) - ?\n")
    text.append("Решение: E(св) = (Z * Mp + N * Mn - Mя) * С^2")
    text.append(f"Е(св) = ({Z} * {m_p} * 10^-27 кг + {N} * {m_n} * 10^-27 кг - {mass} * {m_a} * 10^-27 кг) * (3 * 10^8 м/с)^2 =")
    text.append(f"= ({shorter(Z * m_p, 4)} * 10^-27 кг + {shorter(N * m_n, 4)} * 10^-27 кг - {shorter(mass * m_a, 4)} * 10^-27 кг) * 9 * 10^16 (м/с)^2 =")
    delta_m = shorter(Z * m_p + N * m_n - shorter(mass * m_a, 4), 4)
    text.append(f"= {delta_m} кг * 9 * 10^-11 (м/с)^2 =")
    text.append(f"= {shorter(delta_m * 9, 4)} * 10^-11 Дж ---- Конечный ответ")
    # text.append('E(уд) = E(св) / A ---- если простят найти удельную энергию')
    # text.append(f'E(уд) = ({shorter(delta_m * 9 * 10, 4)} * 10^-12 Дж) / {A} =')
    # text.append(f'{shorter(delta_m * 9 * 10 / A, 4)} * 10^-12 Дж')

    await msg.reply('\n'.join(text))
    await state.clear()
    await user.log("FSM /atom.mass: работа закончена", *text)


@router_atom.message(RequestATOM.num_of_alpha)
async def get_alpha(msg: Message, bot: Bot, state: FSMContext):  # Получение количества альфа-распадов
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None
    
    try:
        alpha = int(msg.text)
    except Exception:
        await msg.reply("Напишите сколько нужно провести α-распадов")
        await user.log("FSM /atom.num_of_alpha: пользователь не передал нужную информацию", msg.text)
        return None
    
    await state.update_data(num_of_alpha=alpha)
    await state.set_state(RequestATOM.num_of_beta)
    await msg.reply("Напишите сколько нужно провести β-распадов")
    await user.log("FSM /atom.num_of_alpha: пользователь ввёл количество α-распадов", msg.text)


@router_atom.message(RequestATOM.num_of_beta)
async def get_beta(msg: Message, bot: Bot, state: FSMContext):  # Получение количества бета-распадов и проведение распадов
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None
    
    try:
        beta = int(msg.text)
    except Exception:
        await msg.reply("Напишите сколько нужно провести β-распадов")
        await user.log("FSM /atom.num_of_beta: пользователь не передал нужную информацию", msg.text)
        return None

    data = await state.get_data()
    name, A, Z, alpha = data["current_atom"]['name'], data["current_atom"]['A'], data["current_atom"]['Z'], data["num_of_alpha"]
    head = ["Для удобства массовое число (то, что сверху) и порядковый номер (то, что снизу) будут написаны в скобках после атома",
            "Например, \"Li (6 3)\"\n"]
    
    # Проведём распады
    first = ["α-распады:",]
    for _ in range(alpha):
        new_atom = TABLE[TABLE.index(name) - 2]
        first.append(f"{name} ({A} {Z}) = {new_atom} ({A - 4} {Z - 2}) + He (4, 2)")
        name = new_atom
        A -= 4
        Z -= 2
    
    second = ["β-распады:",]
    for _ in range(beta):
        new_atom = TABLE[TABLE.index(name) + 1]
        second.append(f"{name} ({A} {Z}) = {new_atom} ({A} {Z + 1}) + e (0, -1)")
        name = new_atom
        Z += 1
    
    await msg.reply('\n'.join(head + first + ['\n',] + second))
    await state.clear()
    await user.log("FSM /atom.num_of_beta: работа закончена", *(first + second))