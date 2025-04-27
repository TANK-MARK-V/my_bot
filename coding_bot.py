from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
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
async def coding(msg: Message, bot: Bot, state: FSMContext):

    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
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

    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
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