from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from logs import do_log as log
from users import get_users
from config import last_massage

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
        ' and ': (' и ', ' ∧ '),  # Конъюнкция
        ' or ': (' или ', ' ∨ '),  # Дизъюнкция
        ' == ': (' = ', ' ≡ '),  # Эквивалентность
        ' <= ': (' -> ', ' → ')  # Имликация
    }
    for put, take in dct.items():
        for get in take:
            new_value = new_value.replace(get, put) if get in new_value else new_value
    if ' <= ' in new_value and 'not' in new_value:
        new_value = new_value.split(' <= ')
        new_value = f'not {new_value[0]} or {new_value[1]}'
    if ' == ' in new_value and 'not' in new_value:
        new_value = new_value.split(' == ')
        new_value = f'({new_value[0]}) == ({new_value[1]})'
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
    out = 'x y z w'[:num_of_perem * 2] + "  "
    if len(DO.keys()) == 1:
        out += 'F'
    else:
        out += first_space.join([str(i) for i in range(1, len(DO.keys())) if i < 10])
        if len(DO.keys()) >= 10:
            out += second_space + second_space.join([str(i) for i in range(len(DO.keys())) if i >= 10])
        out += first_space + 'F'
    out += '\n'
    for x in range(2):
        if num_of_perem > 1:
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
        else:
            sleest = count(DO, x=x)
            if not need_smth or (need_smth and int(sleest[-1]) == need):
                out += f"{x}  " + first_space.join(sleest) + "\n"
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
        last_massage[msg.from_user.id] = ("sti", )
        log(msg, ('Команда /sti не получила аргументов',))
        await msg.reply("Нужно ввести логическое выражение")
        return None
    if not bracket_check(command.args):
        last_massage[msg.from_user.id] = ("sti", )
        log(msg, ('Команда /sti получила логическое выражение, в котором не все скобки закрыты:', command.args))
        await msg.reply("Все скобки логического выражения должны быть закрыты")
        return None
    perems = (command.args.count('x'), command.args.count('y'), command.args.count('z'), command.args.count('w'))
    if not perems[0] or not perems[1] and (perems[2] or perems[3]) or not perems[2] and perems[3]:
        last_massage[msg.from_user.id] = ("sti", )
        log(msg, ('Команда /sti получила логическое выражение с неверным порядком переменных', command.args))
        await msg.reply('Переменные должны указываться в строгом порядке - "x", "y", "z", "w"')
        return None
    last_massage[msg.from_user.id] = ("sti", [command.args, ])
    log(msg, ('Команда /sti получила логическое выражение', command.args))
    await msg.reply('Введите нужное значение выражения или введите "-", если нужно вывести таблицу целиком')