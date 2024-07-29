from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from logs import do_log as log

PORYADOK = ["первое", "второе", "третье", "четвёртое", "пятое", "шестое", "седьмое", "восьмое", "девятое"]
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
                    DO[PORYADOK[len(DO)]] = PRIMER[start + 1:end]
                    PRIMER = PRIMER.replace(PRIMER[start:end + 1], PORYADOK[len(DO) - 1])  # Замена действий
                    flag = 1
                    break
            if flag:
                break


def preps(rest, dct, value):
    new_value = value
    for tri in dct.keys():  # Заменяет предыдущие действия на их результат
        if tri in new_value:
            new_value = str(new_value.replace(tri, str(dct[tri])))
    for letter in rest.keys():  # Заменяет переменные на их значения
        if letter in str(new_value):
            new_value = str(new_value).replace(letter, str(rest[letter]))
    # Кусок кода, который мог облегчить мой прошлый урок (автоматические заменяет импликацию, "или" и "и")
    if 'или' in new_value:
        new_value = str(new_value).replace('или', 'or')
    if 'и' in new_value:
        new_value = str(new_value).replace('и', 'and')
    if '->' in new_value:
        new_value = new_value.split(' -> ')
        new_value = f'not {new_value[0]} or {new_value[1]}'
    return new_value


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
    PRIMER = primer
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

    out = ''
    out += f"{'x y z w'[:num_of_perem * 2]}  {'1 2 3 4 5 6 7 8 9'[:len(DO.keys()) * 2 - 1]}\n"
    for x in range(2):
        for y in range(2):
            if num_of_perem > 2:
                for z in range(2):
                    if num_of_perem > 3:
                        for w in range(2):
                            sleest = count(DO, x=x, y=y, z=z, w=w)
                            if not need_smth or (need_smth and int(sleest[-1]) == need):
                                out += f"{x} {y} {z} {w}  {' '.join(sleest)}\n"
                    else:
                        sleest = count(DO, x=x, y=y, z=z)
                        if not need_smth or (need_smth and int(sleest[-1]) == need):
                            out += f"{x} {y} {z}  {' '.join(sleest)}\n"
            else:
                sleest = count(DO, x=x, y=y)
                if not need_smth or (need_smth and int(sleest[-1]) == need):
                    out += f"{x} {y}  {' '.join(sleest)}\n"
    return out


@router_sti.message(Command("sti"))
async def adding_word(msg: Message, command: CommandObject):
    if not command.args:
        log(msg, ('Комманда /sti не получила аргументов',))
        await msg.reply("Нужно ввести логическое выражение в скобках")
        return None
    leest = command.args.split('_')
    if leest[0][0] + leest[0][-1] != "()":
        log(msg, ('Комманда /sti получила логическое выражение без скобок:', command.args))
        await msg.reply("Логическое выражение должно быть в скобках")
        return None
    try:
        out = sti(*leest)
    except Exception as e:
        log(msg, ('Комманда /sti:', f'ОШИБКА - {e}, запрос - {command.args}'), error=True)
        await msg.reply("Что-то пошло не так")
        return None
    log(msg, ('Комманда /sti выполнила свою работу:', command.args))
    await msg.reply(out)