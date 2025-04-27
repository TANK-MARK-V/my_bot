from aiogram import Router, Bot, types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


from random import choice, sample

from logs import do_log as log
from users import set_score, get_score
from config import autorisation
from scripts.Verbs import kinds_of_verbs, read_verbs, INFO

router_verbs = Router()


class VerbsCallback(CallbackData, prefix='verbs'):
    start: str
    mode: int


class RequestVerbs(StatesGroup):
    data = dict()
    mode = State()
    number = State()
    test = State()


@router_verbs.message(Command("verbs"))
async def starting(msg: Message, bot: Bot):

    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    await log(msg, ('Команда /verbs начала свою работу', ), bot)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Вывести все глаголы', callback_data=VerbsCallback(start= 'mode_', mode=1).pack()))
    builder.add(types.InlineKeyboardButton(text='Проверить знания', callback_data=VerbsCallback(start= 'mode_', mode=2).pack()))
    builder.add(types.InlineKeyboardButton(text='Таблица лидеров', callback_data=VerbsCallback(start= 'mode_', mode=3).pack()))
    builder.adjust(1, 1, 1)
    await msg.reply("Выберите режим:", reply_markup=builder.as_markup())
    return None


@router_verbs.callback_query(VerbsCallback.filter(F.start == "mode_"))
async def get_table(callback: types.CallbackQuery, callback_data: VerbsCallback, bot: Bot, state: FSMContext):

    result = await autorisation(bot, callback=callback)  # Авторизация пользователя
    if not result:
        return None

    await log(callback, (f"Выбран вариант {callback_data.mode}",), bot)

    if callback_data.mode == 1:
        await log(callback, ('Команда /verbs вывела все глаголы',), bot)
        kinds = kinds_of_verbs()
        for key in kinds.keys():
            kind = f'{INFO[key]}:\n'
            for line in kinds[key]:
                kind += f'\n{line}'
            await callback.message.answer(kind)
        await state.clear()
        await callback.answer()
        return None
    
    elif callback_data.mode == 2:
        verbs = read_verbs()
        await log(callback, ('Команда /verbs попросила ввести число глаголов',), bot)
        await callback.message.answer(f"Введите число глаголов, из которых будет составлен тест. Это может быть число от 1 до {len(verbs[0])}")
        await state.set_state(RequestVerbs.number)
        await callback.answer()
        return None
    
    table = get_score('verbs')
    leest, nums = [], sorted(table.keys())[::-1]
    for i in range(len(nums)):
        leest.append(f"{i + 1} место - {nums[i]}: {', '.join(table[nums[i]])}")
    await log(callback, ('Команда /verbs вывела таблицу лидеров', ), bot)
    text = '\n'.join(leest)
    if text:
        await callback.message.answer(text)
    else:
        await callback.message.answer("Таблица пока пуста")
    await state.clear()
    await callback.answer()
    return None
    


@router_verbs.message(RequestVerbs.number)
async def get_number(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    verbs = read_verbs()
    try:
        nums = tuple(sorted(sample(tuple(range(0, len(verbs[0]))), k=int(msg.text))))
    except Exception:
        await log(msg, ('Команда /verbs не получила число глаголов', msg.text), bot)
        await msg.reply(f'Введите число глаголов, из которых будет составлен тест. Это может быть число от 1 до {len(verbs[0])}')
        return None
    await log(msg, ('Команда /verbs получила число глаголов', msg.text), bot)

    await msg.answer('Чтобы ответить, напишите два подходящих слова, разделяя их пробелом')

    new_verbs = (tuple(verbs[0][i] for i in range(len(verbs[0])) if i in nums), tuple(verbs[1][i] for i in range(len(verbs[1])) if i in nums), tuple(verbs[2][i] for i in range(len(verbs[2])) if i in nums))[:]
    take, ran = [new_verbs[0][0], new_verbs[1][0], new_verbs[2][0]], sorted(sample(range(3), k=2))
    first, second = take[:][ran[0]], take[:][ran[1]]
    take[ran[0]], take[ran[1]] = '*****', '*****'
    await msg.answer(f'1: {take[0]} - {take[1]} - {take[2]}')
    RequestVerbs.data[msg.from_user.id] = {'verbs': new_verbs, 'answers': {'cor': [], 'err': [], 'chk': (first, second)}, 'cur': 1}
    await state.set_state(RequestVerbs.test)
    return None


@router_verbs.message(RequestVerbs.test)
async def check_answer(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    cur = RequestVerbs.data[msg.from_user.id]['cur']
    verbs = RequestVerbs.data[msg.from_user.id]['verbs'][:]
    if tuple(msg.text.lower().split()) == RequestVerbs.data[msg.from_user.id]['answers']['chk']:
        RequestVerbs.data[msg.from_user.id]['answers']['cor'].append(cur - 1)
        await msg.reply(choice(('Верно', 'Всё верно', 'Правильно',  'Всё правильно')))
    else:
        RequestVerbs.data[msg.from_user.id]['answers']['err'].append(cur - 1)
        await msg.reply(choice(('Неверно', 'Неправильно')))
    if cur < len(verbs[0]):
        take, ran = [verbs[0][cur], verbs[1][cur], verbs[2][cur]], sorted(sample(range(3), k=2))
        first, second = take[:][ran[0]], take[:][ran[1]]
        take[ran[0]], take[ran[1]] = '*****', '*****'
        await msg.answer(f'{cur + 1}: {take[0]} - {take[1]} - {take[2]}')
        RequestVerbs.data[msg.from_user.id]['cur'] += 1
        RequestVerbs.data[msg.from_user.id]['answers']['chk'] = (first, second)
        return None
    correct = RequestVerbs.data[msg.from_user.id]['answers']['cor']
    error = RequestVerbs.data[msg.from_user.id]['answers']['err']
    await msg.answer(f"Тест окончен.\n" +
                    f"Верно: {len(correct)}, неверно: {len(error)}")
    if msg.from_user.username != None:
        place = set_score('verbs', msg.from_user.username, len(correct))
    else:
        place = set_score('verbs', str(msg.from_user.id), len(correct))
    if place[1]:
        await msg.answer(f'Вы заняли {place[0]} в рейтинге')
    else:
        await msg.answer(place[0])
    await log(msg, (f'Пользователь закончил тест: {len(correct)} + , {len(error)} - , {place[0]}', ), bot)
    await state.clear()
    return None
    