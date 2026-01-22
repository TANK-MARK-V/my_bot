from aiogram import Router, Bot
# Работа с сообщениями
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
# Работа с FSM
from aiogram.fsm.context import FSMContext


from scripts.Logs import autorisation
from scripts.Lolgen.Lolgen import brain, adding, getting


router_lolgen = Router()  # Обработчик Lolgen


@router_lolgen.message(Command("lolgen"))
async def do_lol(msg: Message, command: CommandObject, bot: Bot, state: FSMContext):  # Запуск Lolgen
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None
    
    args = command.args.replace('<', '').replace('>', '') if command.args else ''
    if not args:
        data = await state.get_data()
        if "by_plan" in data.keys():
            args = data["by_plan"]
        else:
            await msg.reply("Необходимо передать схему предложения хотя бы раз")
            await user.log("Command /lolgen: пользователь не передал схему")
            return None
    else:
        await state.update_data(by_plan=args)

    try:
        text = brain(order=args)
    except Exception as e:
        await msg.reply("Что-то пошло не так")
        await user.log(text=("Script /lolgen: произошла ошибка", *repr(e).split("\n"), f"Запрос: {args}"), folder="errors")
        return None
    
    await msg.reply(text)
    await user.log("Command /lolgen: пользователь получил текст:", text)


@router_lolgen.message(Command("add_word"))
async def adding_word(msg: Message, command: CommandObject, bot: Bot):  # Добавление слова в БД
    user = await autorisation(info=msg, bot=bot, need=2)  # Авторизация пользователя
    if not user:
        return None

    if not command.args:
        await msg.reply("Нужно ввести слово и его часть речи")
        await user.log("Command /add_word: пользователь не передал аргументов")
        return None
    leest = command.args.split(' ')
    if len(leest) != 2:
        await msg.reply("Нужно ввести только одно слово и его часть речи")
        await user.log("Command /add_word: пользователь передал некорректные аргументы:", command.args)
        return None
    
    result = adding(*leest)
    await msg.reply(result)
    await user.log(f"Command /add_word: запрос: {command.args} - {result}")


@router_lolgen.message(Command("get_words"))
async def getting_word(msg: Message, bot: Bot):  # Получить все слова из базы данных
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    words = getting()
    speech = {"сущ": "Существительные", "прил": "Прилагательные", "глаг": "Глаголы"}
    for part in words.keys():
        text = speech[part] + ":\n" + ", ".join(sorted(words[part]))
        await msg.answer(text)
    await user.log("Command /get_words")