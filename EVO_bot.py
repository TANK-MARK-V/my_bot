from aiogram import Router, Bot
# Работа с сообщениями
from aiogram.types import Message
from aiogram.filters import Command
# Работа с FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from scripts.Logs import autorisation
from scripts.EVO.EVO import EVO


router_evo = Router()  # Обработчик EVO


class RequestEVO(StatesGroup):  # Сбор информации для выполнения алгоритма
    options = State()
    numbers = State()
    throughs = State()
    escapes = State()
    double = State()


@router_evo.message(Command("evo"))
async def starting(msg: Message, bot: Bot, state: FSMContext):  # Запуск сбора информации для evo
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None
    
    await state.set_state(RequestEVO.options)
    await msg.reply("Введите команды")
    await user.log("Command /evo: начало работы")


@router_evo.message(RequestEVO.options)
async def get_options(msg: Message, bot: Bot, state: FSMContext):  # Ввод команд алгоритма
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    options = msg.text.split('\n')
    if len(options) < 2:
        await msg.reply("Нужно ввести не меньше двух команд")
        await user.log("FSM /evo.options: пользователь ввёл меньше двух команд:", msg.text)
        return None
    
    for i in range(len(options)):  # Проверим, не ввёл ли пользователь запрещённых команд
        opt = options[i]
        if '*0' in opt.replace(' ', ''):  # Умножение на 0
            await msg.reply("Эти команды не приводят к ответу")
            await user.log("FSM /evo.options: пользователь ввёл команду умножить на ноль:", msg.text)
            return None
        elif '/0' in opt.replace(' ', ''):  # Деление на 0
            await msg.reply("На ноль делить нельзя")
            await user.log("FSM /evo.options: пользователь ввёл команду поделить на ноль:", msg.text)
            return None
        elif '=' in opt:  # Это равенство, а не команда
            await msg.reply("Некорректные команды")
            await user.log(text=("FSM /evo.options: пользователь ввёл команду, содержащую \"=\":", msg.text))
            return None
        else:
            if opt[0] != ' ':  # Команда должна начинаться на пробел
                opt = ' ' + opt

    await state.update_data(options=options)
    await state.set_state(RequestEVO.numbers)
    await msg.reply("Введите начальное и конечное число")
    await user.log("FSM /evo: пользователь ввёл команды:", *msg.text.split('\n'))


@router_evo.message(RequestEVO.numbers)
async def get_numbers(msg: Message, bot: Bot, state: FSMContext):  # Ввод начального и конечного числа
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    try:
        numbers = msg.text.split(' ')
        numbers = (int(numbers[0]), int(numbers[1]))  # Преобразовываем в int
    except Exception as e:
        await msg.reply("Нужно ввести только два числа: начальное и конечное")
        await user.log("FSM /evo.numbers: пользователь не ввёл два числа", msg.text, *repr(e).split("\n"))
        return None
    
    await state.update_data(numbers=numbers)
    await state.set_state(RequestEVO.throughs)
    await msg.reply("Введите числа, которые должна содержать траектория программы.\n"
                    + "Если таких чисел нет, введите \"-\"")
    await user.log("FSM /evo.numbers: пользователь ввёл числа", msg.text)


@router_evo.message(RequestEVO.throughs)
async def get_throughs(msg: Message, bot: Bot, state: FSMContext):  # Ввод чисел, через которые проходит траектория программы
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    throughs = None if msg.text == '-' else msg.text.split(' ')
    if throughs:
        try:
            throughs = tuple(map(lambda x: int(x), throughs))
        except Exception as e:
            await msg.reply("Введите числа, которые должна содержать траектория программы.\n"
                            + "Если таких чисел нет, введите \"-\"")
            await user.log("FSM /evo.throughs: пользователь не ввёл \"обязательные\" числа", msg.text, *repr(e).split("\n"))
            return None
        
    await state.update_data(throughs=throughs)
    await state.set_state(RequestEVO.escapes)
    await msg.reply("Введите числа, которые должна избегать траектория программы.\n"
            + "Если траектория программы не должна содержать цифру, начните сообщение с \"+\".\n"
            + "Если таких чисел нет, введите \"-\"")
    await user.log("FSM /evo.throughs: пользователь ввёл \"обязательные\" числа", msg.text)


@router_evo.message(RequestEVO.escapes)
async def get_escapes(msg: Message, bot: Bot, state: FSMContext):  # Ввод чисел, которые избегает траектория программы
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    if msg.text[0] == '+':  # Траектория программы не должна содержать цифру
        escapes = set(msg.text[1:])
        if len(escapes - set(map(str, range(10)))):
            await msg.reply("Введите числа или цифры, которые должна избегать траектория программы.\n"
                            + "Если таких чисел нет, введите \"-\"")
            await user.log("FSM /evo.escapes: пользователь не ввёл \"избегаемые\" цифры", msg.text)
            return None
    else:
        escapes = None if msg.text == '-' else msg.text.split(' ')
        if escapes:
            try:
                escapes = tuple(map(lambda x: int(x), escapes))
            except Exception as e:
                await msg.reply("Введите числа или цифры, которые должна избегать траектория программы.\n"
                                + "Если таких чисел нет, введите \"-\"")
                await user.log("FSM /evo.escapes: пользователь не ввёл \"избегаемые\" числа", msg.text, *repr(e).split("\n"))
                return None
    
    await state.update_data(escapes=escapes)
    await state.set_state(RequestEVO.double)
    await msg.reply("Введите номер команды, которая не должна повторяться.\n"
                    + "Если такого условия нет, введите \"-\"")
    await user.log("FSM /evo.escapes: пользователь ввёл \"избегаемые\" числа или цифры", msg.text)


@router_evo.message(RequestEVO.double)
async def get_escapes(msg: Message, bot: Bot, state: FSMContext):  # Ввод номеров команд, которые не повторяются
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    double = 0 if msg.text == '-' else msg.text
    data = await state.get_data()  # Получаем всю информацию с прошлых обработчиков
    options, numbers, throughs, escapes = data["options"], data["numbers"], data["throughs"], data["escapes"]
    
    is_error = False
    try:
        double = int(double)
    except Exception as e:
        is_error = e
    if is_error or double > len(options) or double < 0:
        await msg.reply("Введите номер команды, которая не должна повторяться.\n"
                    + "Если такого условия нет, введите \"-\"")
        await user.log("FSM /evo.double: пользователь не ввёл номер команды", msg.text, *repr(is_error).split("\n"))
        return None
    
    await user.log("FSM /evo.double: пользователь ввёл номер команды", msg.text)
    try:  # Пробуем выполнить запрос
        out = str(EVO(options, through=throughs, escape=escapes, inverse=numbers[0] > numbers[1], double=double).evo(numbers[0], numbers[1]))
    except Exception as e:
        await msg.reply("Что-то пошло не так")
        await user.log(text=("Script /evo: произошла ошибка:", *repr(e).split("\n"),
                             "Запрос: ", f"options - {options}", f"numbers - {numbers}",
                             f"throughs - {throughs}", f"escapes - {escapes}", f"double - {double}"), folder="errors")
    else:
        await msg.reply(out)
        await user.log("Command /evo: конец работы")
    finally:
        await state.clear()