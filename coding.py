from aiogram import Router
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
async def encoding(msg: Message, command: CommandObject):

    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    if msg.from_user.id not in last_massage.keys() or last_massage[msg.from_user.id] != ("encode", True):
        last_massage[msg.from_user.id] = ("encode", True)
        log(msg, ('Команда /encode начала свою работу', ))
        await msg.reply("Вводите сообщения, которые хотите зашифровать. Чтобы закончить зашифровку сообщений, введите команду ещё раз")
        return None
    last_massage[msg.from_user.id] = ("encode", )
    log(msg, ('Команда /encode закончила свою работу:', ))
    await msg.reply("Зашифровка сообщений закончена")


@router_coding.message(Command("decode"))
async def encoding(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    if msg.from_user.id not in last_massage.keys() or last_massage[msg.from_user.id] != ("decode", True):
        last_massage[msg.from_user.id] = ("decode", True)
        log(msg, ('Команда /decode начала свою работу', ))
        await msg.reply("Вводите сообщения, которые хотите расшифровать. Чтобы закончить расшифровку сообщений, введите команду ещё раз")
        return None
    last_massage[msg.from_user.id] = ("encode", )
    log(msg, ('Команда /decode закончила свою работу:', ))
    await msg.reply("Расшифровка сообщений закончена")