from aiogram import Router, Bot
# Работа с сообщениями
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
# Работа с FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from scripts.Logs import autorisation
from scripts.Coding import encode, decode


router_coding = Router()  # Роутер для кодировки сообщений


class RequestCoding(StatesGroup):  # Обработка сообщений для шифровки
    code = State()


@router_coding.message(Command("encode"))
@router_coding.message(Command("decode"))
async def get_mode(msg: Message, bot: Bot, state: FSMContext):  # Запуск шифрования
    user = await autorisation(info=msg, bot=bot, need=2)  # Авторизация пользователя
    if not user:
        return None
    
    mode = msg.text.split()[0][1:]  # Введённая команда (т.е. нужный метод шифрования)
    prefix = "за" if mode == "encode" else "рас"  # Приставка для метода шифрования

    # Повторный запуск команды должен отключать шифрование
    last = await state.get_data()
    if "code" in last.keys() and last["code"] == mode:
        await state.clear()
        await msg.reply(prefix.capitalize() + "шифровка сообщений завершена")
        await user.log(f"Command /{mode}: конец работы программы")
        return None
    
    # Нужно запустить шифрование
    await state.update_data(code=mode)
    await state.set_state(RequestCoding.code)
    await msg.reply("Вводите сообщения, которые хотите " + prefix + "шифровать")
    await user.log(f"Command /{mode}: начало работы")


@router_coding.message(RequestCoding.code)
async def coding(msg: Message, bot: Bot, state: FSMContext):  # Обработка сообщений для кодирования
    user = await autorisation(info=msg, bot=bot, need=2)  # Авторизация пользователя
    if not user:
        return None

    mode = (await state.get_data())["code"]  # Нужный метод шифрования

    text = msg.text.replace('<', '').replace('>', '')
    if not text:
        await msg.reply("Нужно ввести текст без символов \"меньше\" и \"больше\"")
        await user.log(f"Command /{mode}: пользователь не ввёл текста")
        return None
    
    if mode == "encode":  # Сообщения нужно зашифровать
        try:
            out = encode(text)
        except Exception as e:
            await msg.reply("Что-то пошло не так")
            await user.log(text=("Script /encode: произошла ошибка:", *repr(e).split("\n"),
                                 "Запрос: " + msg.text), folder="errors")
            return None
        
    elif mode == "decode":  # Сообщения нужно расшифровать
        try:
            out = decode(msg.text).replace('<', '').replace('>', '')
            if not out:
                await user.log("Script /decode: получилось пустое сообщение")
                await msg.reply("Сообщение оказалось пустым")
                return None
        except Exception as e:
            await msg.reply("Что-то пошло не так")
            await user.log(text=("Script /decode: произошла ошибка:", *repr(e).split("\n"),
                                 "Запрос: " + msg.text), folder="errors")
            return None
    
    await msg.reply(out)
    await user.log(f"Command /{mode}: шифрование прошло успешно")


@router_coding.message(Command("change"))
async def start_handler(msg: Message, command: CommandObject, bot: Bot):  # Замена раскладки сообщения
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    if not command.args:
        await msg.reply("Некорректные данные")
        await user.log("Command /change: пользователь не передал данные")
        return None
    
    coded = encode(command.args).split(':')  # Зашифровываем всё сообщение
    for i in range(len(coded)):  # Теперь пройдёмся по каждому символу
        cymbol = coded[i]
        if len(cymbol) != 3:  # Каждый символ имеет вид hex:hex, поэтому имеет длину 3
            continue  # Если длина не равна 3, то этот символ вовсе не кодируется
        
        # Теперь меняем раскладку у каждого символа
        left = bin(int(cymbol[0], 16))[2:].rjust(4, '0')
        left = str(int(not int(left[0]))) + left[1:]
        coded[i] = hex(int(left, 2))[2:] + cymbol[1:]
    
    decoded = decode(':'.join(coded))  # Расшифровываем всё сообщение обратно
    await msg.reply(decoded)
    await user.log("Command /change: успешная замена раскладки")