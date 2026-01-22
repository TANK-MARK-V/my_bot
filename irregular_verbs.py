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


from random import choice, sample


from scripts.Logs import autorisation
from scripts.UsersBase import set_score, get_score
from scripts.Verbs import kinds_of_verbs, read_verbs, INFO


router_verbs = Router()  # Обработчик действий с неправильными глаголами


class RequestVerbs(StatesGroup):  # Сбор информации для начала теста и сам тест
    data = dict()
    number = State()
    test = State()


# Какие функции будет давать команда и внутренние названия для кнопок
modes = {
    "Вывести все глаголы": "verbs_1",
    "verbs_1": "Вывести все глаголы",

    "Проверить знания": "verbs_2",
    "verbs_2": "Проверить знания",

    "Таблица лидеров": "verbs_3",
    "verbs_3": "Таблица лидеров"}


@router_verbs.message(Command("verbs"))
async def starting(msg: Message, bot: Bot):  # Начало работы и выбор режима
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    # Создаём кнопки
    builder = InlineKeyboardBuilder()
    buttons = tuple(modes.keys())
    for i in range(0, 6, 2):
        builder.button(text=buttons[i], callback_data=buttons[i + 1])
    builder.adjust(1, 1, 1)

    await msg.reply("Выберите режим:", reply_markup=builder.as_markup())
    await user.log('Command /verbs: начало работы')


@router_verbs.callback_query(F.data.startswith("verbs_"))
async def get_table(callback: CallbackQuery, bot: Bot, state: FSMContext):  # Обработка кнопок /verbs
    user = await autorisation(info=callback, bot=bot)  # Авторизация пользователя
    if not user:
        return None
    
    await state.clear()
    if callback.data[-1] == '1':  # Вывести все глаголы
        kinds = kinds_of_verbs()
        for key in kinds.keys():  # Проходимся по каждой категории
            await callback.message.answer("<b>" + INFO[key] + "</b>:\n" + '\n'.join(kinds[key]))
    elif callback.data[-1] == '2':  # Проверить знания
        verbs = read_verbs()
        await callback.message.answer(f"Введите число глаголов, из которых будет составлен тест. Это может быть число от 1 до {len(verbs[0])}")
        await state.set_state(RequestVerbs.number)
    else:  # Таблица лидеров
        table = get_score("verbs")
        leest, nums = ["<b>Таблица лидеров:</b>"], sorted(table.keys(), reverse=True)
        for i in range(len(nums)):
            leest.append(f"{i + 1} место - {nums[i]}: " + ", ".join(table[nums[i]]))
        await callback.message.answer('\n'.join(leest) if len(leest) > 1 else "Таблица пока пуста")

    await callback.answer()
    await user.log(f"Callback /verbs: выбран вариант \"{modes[callback.data]}\"")


@router_verbs.message(RequestVerbs.number)
async def get_number(msg: Message, bot: Bot, state: FSMContext):  # Ввод количества глаголов на тест и начало
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    verbs = read_verbs()
    try:  # Попробуем получить введённое число глаголов
        nums = tuple(sorted(sample(tuple(range(0, len(verbs[0]))), k=int(msg.text))))
    except Exception as e:
        await msg.reply(f"Введите число глаголов, из которых будет составлен тест. Это может быть число от 1 до {len(verbs[0])}")
        await user.log(f"FSM /verbs.number: пользователь ввёл некорректное число глаголов - \"{msg.text}\"", *repr(e).split("\n"))
        return None

    # Оставим только нужные глаголы
    new_verbs = [[], [], []]
    for num in nums:
        new_verbs[0].append(verbs[0][num])
        new_verbs[1].append(verbs[1][num])
        new_verbs[2].append(verbs[2][num])

    # Выбираем первый по списку глагол и начинаем тест
    await msg.answer("Для ответа нужно написать два подходящих слова, разделяя их пробелом")
    take, ran = [new_verbs[0][0], new_verbs[1][0], new_verbs[2][0]], sorted(sample(range(3), k=2))
    first, second = take[:][ran[0]], take[:][ran[1]]
    take[ran[0]], take[ran[1]] = "*****", "*****"
    await msg.answer("1: " + " - ".join(take))

    await state.update_data(test={"verbs": new_verbs, "answers": {"cor": [], "err": [], "chk": (first, second)}, "cur": 1})  # <- Обязательно нужно это поменять
    await state.set_state(RequestVerbs.test)
    await user.log("FSM /verbs.number: пользователь ввёл число глаголов - " + msg.text)


@router_verbs.message(RequestVerbs.test)
async def check_answer(msg: Message, bot: Bot, state: FSMContext):  # Обработка ответов и подведение итогов
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    user_data = (await state.get_data())["test"]
    verbs, answers, cur = user_data["verbs"], user_data["answers"], user_data["cur"]

    if tuple(msg.text.lower().split()) == answers["chk"]:  # Это правильный ответ
        answers["cor"].append(cur - 1)
        await msg.reply(choice(("Верно", "Всё верно", "Правильно",  "Всё правильно")))
    else:  # Это неправильный ответ
        answers["err"].append(cur - 1)
        await msg.reply(choice(("Неверно", "Неправильно")))
    
    if cur < len(verbs[0]):  # Если ещё есть глаголы, которые нужно спросить
        take, ran = [verbs[0][cur], verbs[1][cur], verbs[2][cur]], sorted(sample(range(3), k=2))
        first, second = take[:][ran[0]], take[:][ran[1]]
        take[ran[0]], take[ran[1]] = "*****", "*****"
        await msg.answer(str(cur + 1) + ": " + " - ".join(take))
        user_data["cur"] += 1
        answers["chk"] = (first, second)
        await state.update_data(test=user_data)

    else:  # Это был последний вопрос
        text = ["Тест окончен", "Верно: " + str(len(answers["cor"])) + ", неверно: " + str(len(answers["err"]))]
        place = set_score("verbs", msg.from_user.id, len(answers["cor"]))
        text += [f"Вы заняли {place} в рейтинге"] if place else ["Вы не заняли места в рейтинге"]
        await msg.answer('\n'.join(text))
        await state.clear()
        await user.log(f"FSM /verbs.test: пользователь закончил тест:", text[1], place if place else "Не занял места")
    