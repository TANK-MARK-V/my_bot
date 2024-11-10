from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from logs import do_log as log
from users import get_users

router_coding = Router()


def encode(text):
    letters = (("ё1234567890-= йцукенгшщзхъ фывапролджэ\ ячсмитьбю.", 'Ё!"№;%:?*()_+ ЙЦУКЕНГШЩЗХЪ ФЫВАПРОЛДЖЭ/ ЯЧСМИТЬБЮ,'),  # Русские буквы
            ("`1234567890-= qwertyuiop[] asdfghjkl;'\ zxcvbnm,./", '~!@#$%^&*()_+ QWERTYUIOP{} ASDFGHJKL:"| ZXCVBNM<>?'))  # Английские буквы

    encoded = ""

    for i in text:
        if i in (' ', '\n'):
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
async def encoding(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    if not command.args:
        log(msg, ('Команда /encode не получила аргументов',))
        await msg.reply("Нужно ввести текст для шифрования")
        return None
    text = command.args
    if '<' in text:
        text.replace('<', '')
    if '>' in text:
        text.replace('>', '')
    try:
        out = encode(text)
    except Exception as e:
        log(msg, ('Команда /encode:', f'ОШИБКА - {e}, запрос - {text}'), error=True)
        await msg.reply("Что-то пошло не так")
        return None
    log(msg, ('Команда /encode выполнила свою работу:', command.args))
    await msg.reply(out)


@router_coding.message(Command("decode"))
async def encoding(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    if not command.args:
        log(msg, ('Команда /decode не получила аргументов',))
        await msg.reply("Нужно ввести текст для шифрования")
        return None
    text = command.args
    try:
        out = decode(text)
    except Exception as e:
        log(msg, ('Команда /decode:', f'ОШИБКА - {e}, запрос - {text}'), error=True)
        await msg.reply("Что-то пошло не так")
        return None
    log(msg, ('Команда /decode выполнила свою работу:', command.args))
    await msg.reply(out)