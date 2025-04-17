from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from logs import do_log as log
from users import get_users
from config import last_massage

router_coding = Router()


def encode(text):
    letters = (("ё1234567890-= йцукенгшщзхъ фывапролджэ\ ячсмитьбю.", 'Ё!"№;%:?*()_+ ЙЦУКЕНГШЩЗХЪ ФЫВАПРОЛДЖЭ/ ЯЧСМИТЬБЮ,'),  # Русские буквы
            ("`1234567890-= qwertyuiop[] asdfghjkl;'\ zxcvbnm,./", '~!@#$%^&*()_+ QWERTYUIOP{} ASDFGHJKL:"| ZXCVBNM<>?'))  # Английские буквы

    encoded = ""

    for i in text:
        if i not in ''.join(letters[0][0].split(' ')) + ''.join(letters[0][1].split(' ')) + ''.join(letters[1][0].split(' ')) + ''.join(letters[1][1].split(' ')):
            encoded += i
        else:
            lang = int(i in letters[1][0] + letters[1][1])
            shift = int(i in letters[lang][1])
            line = 0
            lines = letters[lang][shift].split(' ')
            for j in lines:
                if i in j:
                    line = lines.index(j)
            symb = letters[lang][shift].split(' ')[line].index(i)
            encoded += hex(int(str(lang) + str(shift) + bin(line)[2:].rjust(2, '0'), base=2))[2:] + '.' + hex(symb)[2:]
        
        encoded += ':'
    
    return encoded[:-1]


def decode(text):
    letters = (("ё1234567890-= йцукенгшщзхъ фывапролджэ\ ячсмитьбю.", 'Ё!"№;%:?*()_+ ЙЦУКЕНГШЩЗХЪ ФЫВАПРОЛДЖЭ/ ЯЧСМИТЬБЮ,'),  # Русские буквы
            ("`1234567890-= qwertyuiop[] asdfghjkl;'\ zxcvbnm,./", '~!@#$%^&*()_+ QWERTYUIOP{} ASDFGHJKL:"| ZXCVBNM<>?'))  # Английские буквы

    decoded = ""
    
    for i in text.split(':'):
        if '.' not in i:
            decoded += i
        else:
            other, symb = i.split('.')
            symb = int(symb, base=16)
            other = bin(int(other, base=16))[2:].rjust(4, '0')
            lang, shift, line = int(other[0], base=2), int(other[1], base=2), int(other[2:], base=2)
            decoded += letters[lang][shift].split(' ')[line][symb]
        
    return decoded


@router_coding.message(Command("encode"))
async def encoding(msg: Message, command: CommandObject, bot: Bot):

    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if msg.from_user.id not in last_massage.keys() or last_massage[msg.from_user.id] != ("encode", True):
        last_massage[msg.from_user.id] = ("encode", True)
        await log(msg, ('Команда /encode начала свою работу', ), bot)
        await msg.reply("Вводите сообщения, которые хотите зашифровать. Чтобы закончить зашифровку сообщений, введите команду ещё раз")
        return None
    last_massage[msg.from_user.id] = ("encode", )
    await log(msg, ('Команда /encode закончила свою работу:', ), bot)
    await msg.reply("Зашифровка сообщений закончена")
    return None


@router_coding.message(Command("decode"))
async def encoding(msg: Message, command: CommandObject, bot: Bot):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        await log(msg, user, bot)

    if msg.from_user.id not in last_massage.keys() or last_massage[msg.from_user.id] != ("decode", True):
        last_massage[msg.from_user.id] = ("decode", True)
        await log(msg, ('Команда /decode начала свою работу', ), bot)
        await msg.reply("Вводите сообщения, которые хотите расшифровать. Чтобы закончить расшифровку сообщений, введите команду ещё раз")
        return None
    last_massage[msg.from_user.id] = ("encode", )
    await log(msg, ('Команда /decode закончила свою работу:', ), bot)
    await msg.reply("Расшифровка сообщений закончена")
    return None


async def encode_words(msg, bot):
    text = msg.text.replace('<', '').replace('>', '')
    if not text:
        await log(msg, ('Команда /encode не получила текста',), bot)
        await msg.reply("Нужно ввести текст для зашифровки")
        return None
    try:
        out = encode(text)
    except Exception as e:
        await log(msg, ('Команда /encode:', f'ОШИБКА - {e}, запрос - {msg.text}'), bot, error=True)
        await msg.reply("Что-то пошло не так")
        return None
    await log(msg, ('Команда /encode выполнила свою работу:', text), bot)
    await msg.reply(out)
    return None


async def decode_words(msg, bot):
    if not msg.text:
            await log(msg, ('Команда /decode не получила текста',), bot)
            await msg.reply("Нужно ввести текст для расшифровки")
            return None
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
    await log(msg, ('Команда /decode выполнила свою работу:', msg.text), bot)
    await msg.reply(out)
    return None