from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from lolgen import brain, adding


router = Router()
last_message = {}

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Привет! Я пока только разрабатываюсь)")


@router.message(Command("lolgen"))
async def lolgening(msg: Message, command: CommandObject):
    if command.args:
        order = command.args
        last_message[msg.from_user.id] = order
    else:
        try:
            order = last_message[msg.from_user.id]
        except Exception:
            await msg.reply("Необходимо передать схему предложения хотя бы раз")
            return None
    try:
        text = brain(order=order)
    except Exception:
        await msg.reply("Что-то пошло не так")
        return None
    await msg.reply(text)

@router.message(Command("word"))
async def adding_word(msg: Message, command: CommandObject):
    if not command.args:
        await msg.reply("Нужно ввести слово и его часть речи через пробел")
        return None
    leest = command.args.split(' ')
    if len(leest) != 2:
        await msg.reply('Нужно ввести только одно слово и его часть речи через пробел, например "/word огурец сущ"')
        return None
    await msg.reply(adding(leest[0], leest[1]))


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")