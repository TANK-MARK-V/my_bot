from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import COMMANDS, info

router = Router()

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


#                                                                               Всё остальное
@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")