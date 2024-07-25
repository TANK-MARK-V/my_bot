from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from lolgen import brain


router = Router()
last_message = {}

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Привет! Я пока только разрабатываюсь) \nТы можешь попробовать написать /test или /lolgen и порядок слов")


@router.message(Command("test"))
async def test(msg: Message):
    await msg.reply(f'{msg}')


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
    await msg.reply(brain(order=order))


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")