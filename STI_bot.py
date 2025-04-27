from aiogram import Router, Bot, types
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from logs import do_log as log
from config import autorisation

from scripts.STI import sti
router_sti = Router()


class STICallback(CallbackData, prefix='sti'):
    primer: str
    need: str


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
async def starting(msg: Message, command: CommandObject, bot: Bot):

    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    if not command.args:
        await log(msg, ('Команда /sti не получила аргументов',), bot)
        await msg.reply("Нужно ввести логическое выражение")
        return None
    if not bracket_check(command.args):
        await log(msg, ('Команда /sti получила логическое выражение, в котором не все скобки закрыты:', command.args), bot)
        await msg.reply("Все скобки логического выражения должны быть закрыты")
        return None
    perems = (command.args.count('x'), command.args.count('y'), command.args.count('z'), command.args.count('w'))
    if not perems[0] or not perems[1] and (perems[2] or perems[3]) or not perems[2] and perems[3]:
        await log(msg, ('Команда /sti получила логическое выражение с неверным порядком переменных', command.args), bot)
        await msg.reply('Переменные должны указываться в строгом порядке - "x", "y", "z", "w"')
        return None
    await log(msg, ('Команда /sti получила логическое выражение', command.args), bot)

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Вывести только 0', callback_data=STICallback(primer=command.args, need='0').pack()))
    builder.add(types.InlineKeyboardButton(text='Вывести только 1', callback_data=STICallback(primer=command.args, need='1').pack()))
    builder.add(types.InlineKeyboardButton(text='Вывести таблицу целиком', callback_data=STICallback(primer=command.args, need='').pack()))
    builder.adjust(1, 1, 1)
    await msg.reply('Выберите, какую часть таблицы нужно вывести', reply_markup=builder.as_markup())
    return None


@router_sti.callback_query(STICallback.filter())
async def get_table(callback: types.CallbackQuery, callback_data: STICallback, bot: Bot):

    result = await autorisation(bot, callback=callback)  # Авторизация пользователя
    if not result:
        return None

    await log(callback, (f"Выбран вариант {'вывести только ' + callback_data.need if callback_data.need else 'вывести целиком'}",), bot)
    args = [callback_data.primer, callback_data.need]
    try:
        out = sti(*args)
    except Exception as e:
        await log(callback, ('Команда /sti:', f'ОШИБКА - {e}, запрос - {args[0]}'), bot, error=True)
        await callback.message.answer("Что-то пошло не так")
        await callback.answer()
        return None
    await log(callback, ('Команда /sti выполнила свою работу:', args[0]), bot)
    await callback.message.answer(out)
    await callback.answer()
    return None