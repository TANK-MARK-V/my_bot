from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lolgen import brain, adding
from STI import sti
from config import COMMANDS, info

router = Router()
last_message = {}

#                                                                                   Старт
@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer('Чтобы узнать, что я умею используй "/info"')

#                                                                           Информация о коммандах
@router.message(Command("info"))
async def information(msg: Message, command: CommandObject):
    if command.args and command.args.replace(' ', '') in COMMANDS['_names_']:
        await msg.reply(info(command=command.args))
        return None
    builder = InlineKeyboardBuilder()
    for command in COMMANDS["_names_"]:
        builder.add(types.InlineKeyboardButton(
            text=f'/{command}',
            callback_data=f'command_{command}'))
        
    await msg.reply("Выберете нужную комманду", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("command_"))
async def send_info(callback: types.CallbackQuery):
    await callback.message.answer(info(callback.data.replace("command_", '')))
    await callback.answer()

#                                                                                   Лолген
@router.message(Command("lolgen"))
async def lolgening(msg: Message, command: CommandObject):
    if command.args:
        order = command.args
        last_message[msg.from_user.id] = order
    else:
        try:
            order = last_message[msg.from_user.id]
        except Exception as e:
            await msg.reply("Необходимо передать схему предложения хотя бы раз")
            return None
    try:
        text = brain(order=order)
    except Exception as e:
        print('ОШИБКА -', e)
        await msg.reply("Что-то пошло не так")
        return None
    if len(last_message) == 2:
        with open('two.txt', 'w') as file:
            file.write('Не менее двух')
    await msg.reply(text)

#                                                                               Добавление слов
@router.message(Command("word"))
async def adding_word(msg: Message, command: CommandObject):
    if not command.args:
        await msg.reply("Нужно ввести слово и его часть речи")
        return None
    leest = command.args.split(' ')
    if len(leest) != 2:
        await msg.reply('Нужно ввести только одно слово и его часть речи')
        return None
    await msg.reply(adding(leest[0], leest[1]))

#                                                                           Счётчик таблиц истинности
@router.message(Command("sti"))
async def adding_word(msg: Message, command: CommandObject):
    if not command.args:
        await msg.reply("Нужно ввести логическое выражение в скобках")
        return None
    leest = command.args.split('_')
    if leest[0][0] + leest[0][-1] != "()":
        await msg.reply("Логическое выражение должно быть в скобках")
        return None
    try:
        out = sti(*leest)
    except Exception as e:
        print('ОШИБКА -', e)
        await msg.reply("Что-то пошло не так")
        return None
    await msg.reply(out)

#                                                                               Всё остальное
@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")