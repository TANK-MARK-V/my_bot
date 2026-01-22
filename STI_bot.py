from aiogram import F, Router, Bot
# Работа с сообщениями
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
# Работа кнопками
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery


from scripts.Logs import autorisation
from scripts.STI import sti
from scripts.help import bracket_check


router_sti = Router()  # Обработчик STI


@router_sti.message(Command("sti"))
async def starting(msg: Message, command: CommandObject, bot: Bot):  # Начало работы
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    # Проверим корректность введённого выражения
    if not command.args:
        await msg.reply("Нужно ввести логическое выражение")
        await user.log("Command /sti: пользователь не передал аргументы")
        return None
    if not bracket_check(command.args):
        await msg.reply("Все скобки логического выражения должны быть закрыты")
        await user.log("Command /sti: пользователь передал логическое выражение, в котором не все скобки закрыты:", command.args)
        return None
    
    # Проверим, что порядок переменных соблюдается
    x, y, z, w = command.args.count('x'), command.args.count('y'), command.args.count('z'), command.args.count('w')
    if (not x) or (not y and (z or w)) or (not z and w):
        await msg.reply("Переменные должны указываться в строгом порядке - \"x\", \"y\", \"z\", \"w\"")
        await user.log("Command /sti: пользователь передал логическое выражение с неверным порядком переменных", command.args, f"x: {x}, y: {y}, z: {z}, w: {w}")
        return None
    
    # Создаём кнопки
    builder = InlineKeyboardBuilder()
    builder.button(text='Вывести только 0', callback_data="sti_" + command.args + '0')
    builder.button(text='Вывести только 1', callback_data="sti_" + command.args + '1')
    builder.button(text='Вывести таблицу целиком', callback_data="sti_" + command.args + '2')
    builder.adjust(1, 1, 1)

    await msg.reply("Выберите, какую часть таблицы нужно вывести", reply_markup=builder.as_markup())
    await user.log("Command /sti: полученио логическое выражение", command.args)


@router_sti.callback_query(F.data.startswith("sti_"))
async def get_table(callback: CallbackQuery, bot: Bot):  # Вывод таблицы по введённым данным
    user = await autorisation(info=callback, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    example, need = callback.data[4:-1], callback.data[-1] if callback.data[-1] != '2' else ''
    try:  # Пробуем выполнить запрос
        out = sti(example, need)
    except Exception as e:
        await callback.message.answer("Что-то пошло не так")
        await user.log(text=("Script /sti: произошла ошибка:", *repr(e).split("\n"),
                             "Запрос: " + callback.data), folder="errors")
    else:
        await callback.message.answer(out)
        await user.log(f"Command /sti: выполнен запрос \"{callback.data}\"")
    finally:
        await callback.answer()