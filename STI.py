from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from logs import do_log as log
from users import get_users

DO = dict()
PRIMER = ''
router_sti = Router()


def making():
    global DO
    global PRIMER
    while '(' in PRIMER or ')' in PRIMER:  # Пример ещё не преобразован
        opening = list()
        closing = list()
        for i in range(len(PRIMER)):  # Индексы начала и конца скобок
            if PRIMER[i] == '(':
                opening.append(i)
            elif PRIMER[i] == ')':
                closing.append(i)
        meen = 100  # Минимальный размер скобок
        final = []
        counted = []
        for op in opening:  # Расстояния от начал скобок до концов
            for cl in closing:
                if cl > op:
                    counted.append(cl - op)
                    if 0 < cl - op < meen:
                        meen = cl - op
            final.append(counted[:])
            counted.clear()
        flag = 0  # Пример изменился
        for op in range(len(final)):
            for long in range(len(final[op])):
                if final[op][long] == meen:
                    start = opening.pop(op)
                    end = closing.pop(closing.index(final[op][long] + start))
                    DO['|' + str(len(DO)) + '|'] = PRIMER[start + 1:end]
                    PRIMER = PRIMER.replace(PRIMER[start:end + 1], '|' + str(len(DO) - 1) + '|')  # Замена действий
                    flag = 1
                    break
            if flag:
                break


def changing(value):  # Автоматически заменяет знаки
    new_value = value
    dct = {
        ' and ': (' и ', ' ∧ '),
        ' or ': (' или ', ' ∨ '),
        ' == ': (' = ', ' ≡ ')
    }
    for put, take in dct.items():
        for get in take:
            new_value = new_value.replace(get, put) if get in new_value else new_value
    if ' -> ' in new_value:
        new_value = new_value.split(' -> ')
        new_value = f'not {new_value[0]} or {new_value[1]}'
    if ' → ' in new_value:
        new_value = new_value.split(' → ')
        new_value = f'not {new_value[0]} or {new_value[1]}'
    return new_value

def preps(rest, dct, value):
    new_value = value
    for tri in dct.keys():  # Заменяет предыдущие действия на их результат
        if tri in new_value:
            new_value = new_value.replace(tri, str(dct[tri]))
    for letter in rest.keys():  # Заменяет переменные на их значения
        if letter in str(new_value):
            new_value = new_value.replace(letter, str(rest[letter]))
    return changing(new_value)


def count(do, **rest):  # Вычисления
    leest = list()
    dct = do.copy()
    for key in dct.keys():
        value = preps(rest, dct, dct[key])
        dct[key] = str(int(eval(value)))
        leest.append(dct[key])
    return leest


def sti(primer, only=''):
    global DO
    global PRIMER
    DO = dict()
    PRIMER = '(' + primer.lower() + ')'
    num_of_perem = 0
    if 'x' in PRIMER:
        num_of_perem += 1
        if 'y' in PRIMER:
            num_of_perem += 1
            if 'z' in PRIMER:
                num_of_perem += 1
                if 'w' in PRIMER:
                    num_of_perem += 1
    making()  # Преобразование
    if only != '' and only in '01':
        need_smth = True
        need = int(only)
    else:
        need_smth = False
        need = None
    first_space = "   "
    second_space = " "
    out = ''
    out += 'x y z w'[:num_of_perem * 2] + "  " + first_space.join([str(i + 1) for i in range(len(DO.keys())) if i < 9])
    if len(DO.keys()) >= 10:
        out += second_space + second_space.join([str(i + 1) for i in range(len(DO.keys())) if i >= 9])
    out += '\n'
    for x in range(2):
        for y in range(2):
            if num_of_perem > 2:
                for z in range(2):
                    if num_of_perem > 3:
                        for w in range(2):
                            sleest = count(DO, x=x, y=y, z=z, w=w)
                            if not need_smth or (need_smth and int(sleest[-1]) == need):
                                out += f"{x} {y} {z} {w}  " + first_space.join(sleest) + "\n"
                    else:
                        sleest = count(DO, x=x, y=y, z=z)
                        if not need_smth or (need_smth and int(sleest[-1]) == need):
                            out += f"{x} {y} {z}  " + first_space.join(sleest) + "\n"
            else:
                sleest = count(DO, x=x, y=y)
                if not need_smth or (need_smth and int(sleest[-1]) == need):
                    out += f"{x} {y}  " + first_space.join(sleest) + "\n"
    return out


def bracket_check(test_string):
    open = ('(', '{', '[', '《')
    closed = (')', '}', ']', '》')
    leest = list()
    for sym in test_string:
        if sym in open:
            leest.append(sym)
        elif sym in closed:
            if len(leest) == 0:
                return False
            elif open[closed.index(sym)] == leest[len(leest) - 1]:
                leest.remove(open[closed.index(sym)])
    if len(leest) != 0:
        return False
    return True


@router_sti.message(Command("sti"))
async def solving(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    if not command.args:
        log(msg, ('Команда /sti не получила аргументов',))
        await msg.reply("Нужно ввести логическое выражение")
        return None
    leest = command.args.split('_')
    if not bracket_check(leest[0]):
        log(msg, ('Команда /sti получила логическое выражение, в котором не все скобки закрыты:', command.args))
        await msg.reply("Все скобки логического выражения должны быть закрыты")
        return None
    try:
        out = sti(*leest)
    except Exception as e:
        log(msg, ('Команда /sti:', f'ОШИБКА - {e}, запрос - {command.args}'), error=True)
        await msg.reply("Что-то пошло не так")
        return None
    log(msg, ('Команда /sti выполнила свою работу:', command.args))
    await msg.reply(out)