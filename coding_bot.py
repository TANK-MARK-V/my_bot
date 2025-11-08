from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from logs import do_log as log
from config import autorisation

from scripts.Coding import encode, decode


router_coding = Router()


class RequestCoding(StatesGroup):
    mode = State()


@router_coding.message(Command("encode"))
@router_coding.message(Command("decode"))
async def get_mode(msg: Message, bot: Bot, state: FSMContext):

    result = await autorisation(bot, msg=msg, need=2)  # Авторизация пользователя
    if not result:
        return None
    
    mode = msg.text.split()[0][1:]
    last = await state.get_data()

    if "mode" in last.keys() and last["mode"] == mode:
        await log(msg, (f'Команда /{mode} закончила свою работу', ), bot)
        await msg.reply(f"{'За' if mode == 'encode' else 'Рас'}шифровка сообщений завершена")
        await state.clear()
        return None
    
    await log(msg, (f'Команда /{mode} начала свою работу', ), bot)
    await msg.reply(f"Вводите сообщения, которые хотите {'за' if mode == 'encode' else 'рас'}шифровать")
    await state.update_data(mode=mode)
    await state.set_state(RequestCoding.mode)
    return None


@router_coding.message(RequestCoding.mode)
async def coding(msg: Message, bot: Bot, state: FSMContext):

    result = await autorisation(bot, msg=msg, need=2)  # Авторизация пользователя
    if not result:
        return None

    mode = (await state.get_data())["mode"]
    text = msg.text.replace('<', '').replace('>', '')
    if not text:
        await log(msg, (f'Команда /{mode} не получила текста',), bot)
        await msg.reply('Нужно ввести текст без символов "меньше" и "больше"')
        return None
    if mode == "encode":
        try:
            out = encode(text)
        except Exception as e:
            await log(msg, ('Команда /encode:', f'ОШИБКА - {e}, запрос - {msg.text}'), bot, error=True)
            await msg.reply("Что-то пошло не так")
            return None
    if mode == "decode":
        try:
            out = decode(msg.text).replace('<', '').replace('>', '')
            if not out:
                await log(msg, ('Команда /decode оставила пустое сообщение',), bot)
                await msg.reply('Сообщение оказалось пустым')
                return None
        except Exception as e:
            await log(msg, ('Команда /decode:', f'ОШИБКА - {e}, запрос - {msg.text}'), bot, error=True)
            await msg.reply("Что-то пошло не так")
            return None
    await log(msg, (f'Команда /{mode} выполнила свою работу:', text), bot)
    await msg.reply(out)
    return None


@router_coding.message(Command('change'))
async def start_handler(msg: Message, command: CommandObject, bot: Bot):
    
    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    if not command.args:
        await log(msg, ('Команда /change не получила данные', ), bot)
        await msg.reply('Некорректные данные')
        return None
    coded = encode(command.args).split(':')
    for i in range(len(coded)):
        cymbol = coded[i]
        if len(cymbol) != 3:
            continue
        left = bin(int(cymbol[0], 16))[2:].rjust(4, '0')
        left = str(int(not int(left[0]))) + left[1:]
        coded[i] = hex(int(left, 2))[2:] + cymbol[1:]
    decoded = decode(':'.join(coded))
    await log(msg, ('Команда /change поменяла раскладку', decoded), bot)
    await msg.reply(decoded)
    return None