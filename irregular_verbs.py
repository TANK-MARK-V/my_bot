from aiogram import Router, Bot, types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


from random import choice, sample

from logs import do_log as log
from users import get_users, set_score, get_score
from config import last_massage
from free_handler import free_handler

import csv

INFO = {'en': 'глаголы в третьей форме кончаются на -en',
        'ne': 'глаголы в третьей форме кончаются на -ne',
        'd/t': 'в третьей форме буква t, стоящая в конце первой формы, заменяется на d',
        '+t': 'добавляется окончание -t во второй и третьей форме',
        'double': 'в первой форме стоят две одинаковые буквы подряд',
        'ell': 'первая форма кончается на -ell',
        'ay': 'первая форма кончается на -ay',
        'ught': 'вторая и третья формы кончаются на -ught',
        'three': 'формы не отличаются друг от друга',
        'ew': 'вторая форма кончается на -ew',
        'i_a_u': 'буква "i" в первой форме, "a" во второй и "u" в третьей стоят в том же месте',
        'pairs': 'глаголы, похожие на друг друга или имеющие большую общую часть',
        'else': 'всё остальное'}
router_verbs = Router()


class VerbsCallback(CallbackData, prefix='verbs'):
    start: str
    mode: int


class RequestVerbs(StatesGroup):
    data = dict()
    mode = State()
    number = State()
    test = State()


def read_verbs(delim='-'):
    words = ([], [], [])
    with open('data/words.csv', 'r', newline='') as file:
        word_reader = csv.reader(file, delimiter=delim)
        for base, past, part in tuple(word_reader)[1:]:
            if base not in words[0] and past not in words[1] and part not in words[2]:
                words[0].append(base)
                words[1].append(past)
                words[2].append(part)
    return words


def sorting_verbs(words):
    lines = []
    for i in range(len(words[0])):
        lines.append(f'{words[0][i]} {words[1][i]} {words[2][i]}')
    lines.sort()
    lines = tuple(map(lambda x: x.split(), lines))
    new_words = ([], [], [])
    for base, past, part in lines:
        new_words[0].append(base)
        new_words[1].append(past)
        new_words[2].append(part)
    return new_words


def write_verbs(new_words=([], [], []), delim='-'):
    words = read_verbs()
    words = sorting_verbs((words[0] + new_words[0], words[1] + new_words[1], words[2] + new_words[2]))
    with open('data/words.csv', 'w', newline='') as file:
        word_writer = csv.writer(file, delimiter=delim)
        word_writer.writerow(['Base', 'Past', 'Participle'])
        for i in range(len(words[0])):
            word_writer.writerow([words[0][i].lower(), words[1][i].lower(), words[2][i].lower()])


def kinds_of_verbs():
    words = read_verbs()
    
    kinds = {'en': [], 'ne': [], 'd/t': [], '+t': [], 'double': [], 'ell': [], 'ay': [], 'ught': [], 'three': [], 'ew': [], 'i_a_u': [], 'pairs': [], 'else': []}

    for i in range(len(words[0])):
        line = f'{words[0][i]} - {words[1][i]} - {words[2][i]}'

        if 'come' in words[0][i] or 'wear' in words[0][i] or 'stand' in words[0][i] or 'get' in words[0][i] or 'give' in words[0][i]:
            kinds['pairs'].append(line)
            continue

        if len({words[0][i], words[1][i], words[2][i]}) == 1:
            kinds['three'].append(line)
            continue

        if len({words[0][i], words[1][i], words[2][i]}) == 2:
            if words[2][i][-4:] == 'ught':
                kinds['ught'].append(line)
                continue

            if words[2][i][-1] == 't':
                if words[0][i][:2] == words[1][i][:2] and words[0][i][:2] + words[0][i][3] == words[1][i][:3]:
                    kinds['double'].append(line)
                    continue
                if words[0][i][-1] == 'd':
                    kinds['d/t'].append(line)
                    continue
                if len(words[0][i]) + 1 == len(words[2][i]):
                    kinds['+t'].append(line)
                    continue
            
            if words[2][i][-1] == 'd':
                if words[0][i][-3:] == 'ell':
                    kinds['ell'].append(line)
                    continue
                if words[0][i][-2:] == 'ay':
                    kinds['ay'].append(line)
                    continue
        
        if words[2][i][-2:] == 'en':
            kinds['en'].append(line)
            continue
        if words[2][i][-2:] == 'ne':
            kinds['ne'].append(line)
            continue
        if words[1][i][-2] == 'e' and words[2][i][-1] == 'n':
            kinds['ew'].append(line)
            continue
        if 'i' in words[0][i] and 'a' in words[1][i] and 'u' in words[2][i]:
            kinds['i_a_u'].append(line)
            continue
        if words[2][i][-2:] == 'ne':
            kinds['ne'].append(line)
            continue

        kinds['else'].append(line)

    return kinds


@router_verbs.message(Command("verbs"))
async def starting(msg: Message, bot: Bot, state: FSMContext):
    global INFO
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    last_massage[msg.from_user.id] = ('verbs', )

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
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if last_massage[msg.from_user.id] != ("verbs", ):
        await state.clear()
        await free_handler(msg, bot)
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
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)
    
    if last_massage[msg.from_user.id] != ("verbs", ):
        await state.clear()
        await free_handler(msg, bot)
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
    