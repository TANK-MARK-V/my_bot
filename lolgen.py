import random as rn
import pymorphy3
import sqlite3

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from logs import do_log as log
from users import get_users
from config import last_massage

morph = pymorphy3.MorphAnalyzer()
router_lolgen = Router()
last_command = {}

def getting():  # Функция для считывания слов из БД
    con = sqlite3.connect("DataBase.sqlite")
    cur = con.cursor()
    pril = cur.execute("""SELECT word FROM words
                                  WHERE part = 'прил'""").fetchall()
    sus = cur.execute("""SELECT word FROM words
                                  WHERE part = 'сущ'""").fetchall()
    glag = cur.execute("""SELECT word FROM words
                                  WHERE part = 'глаг'""").fetchall()
    commands = {
        'сущ': [i[0] for i in sus],
        'прил': [i[0] for i in pril],
        'глаг': [i[0] for i in glag]
    }
    con.commit()
    con.close()
    return commands


def taking(order):  # Выбор случайных слов
    commands = getting()
    return [rn.choice(commands[slovo]) if slovo in commands else slovo for slovo in order.split()]


def changing(word, padej='nomn', pol='masc', odu='inan', dont=0):  # Функция для склонения слов
    commands = getting()
    prs = morph.parse(word)[0]
    if word in commands['сущ']:
        return prs.inflect({'sing', padej}).word
    elif word in commands['прил']:
        if pol == 'masc':
            if prs.inflect({pol, 'sing', padej}).tag.animacy is not None:
                return prs.inflect({odu, pol, 'sing', padej}).word
            else:
                return prs.inflect({pol, 'sing', padej}).word
        else:
            return prs.inflect({pol, 'sing', padej}).word
    elif word == 'который' or (word in commands['глаг'] and dont == 1):
        return prs.inflect({'sing', pol}).word
    elif word in commands['глаг']:
        if '1per' in prs.tag or '2per' in prs.tag or '3per' in prs.tag:
            return prs.inflect({'sing', pol, '3per'}).word
        return prs.inflect({'sing', pol}).word


def brain(order):  # Изначально lolgen был этой функцией. Если в кратце, то это главный алгоритм склонения
    pol = 'masc'
    padej = 'nomn'
    odu = 'inan'
    flag_s = 0
    commands = getting()
    sus = commands['сущ']
    pril = commands['прил']
    glag = commands['глаг']

    ad = taking(order)

    for i in range(len(ad)):  # Цикл, проходящий по всем словам, и склоняющий их
        if ad[i] in glag:
            if flag_s == 1:
                ad[i] = changing('который', pol=pol, dont=1) + ' ' + changing(ad[i], pol=pol)
                ad[i - 1] += ','  # Добавление слова "который" если до этого идёт существительное
            padej = 'accs'
        elif ad[i] in sus:
            ad[i] = changing(ad[i], padej)
            pol = morph.parse(ad[i])[0].tag.gender
            odu = morph.parse(ad[i])[0].tag.animacy  # Следующие слова будут зависимы от этого
            flag_s = 1
        elif ad[i] in pril:
            for j in range(i + 1, len(ad)):
                if ad[j] in sus:
                    pol = morph.parse(ad[j])[0].tag.gender
                    odu = morph.parse(ad[j])[0].tag.animacy
                    break
                    # Получение признаков существительного для склонения прилагательного, которое стоит до
            ad[i] = changing(ad[i], padej, pol, odu)
    return ' '.join(ad).capitalize()


def trying(word, speech):  # Проверка на то, подхордит ли новое слово под критерии
    pol = 'masc'
    padej = 'accs'
    odu = 'inan'
    prs = morph.parse(word)[0]
    if speech == 'VERB':
        if '1per' in prs.tag or '2per' in prs.tag or '3per' in prs.tag:
            word = prs.inflect({'sing', pol, '3per'}).word
        else:
            try:
                word = prs.inflect({'sing', pol}).word
            except Exception:
                return True
    elif speech == 'NOUN':
        try:
            word = prs.inflect({'sing', padej}).word
        except Exception:
            return True
    elif speech == 'ADJF':
        if prs.inflect({pol, 'sing', padej}).tag.animacy is not None:
            try:
                word = prs.inflect({odu, pol, 'sing', padej}).word
            except Exception:
                return True
        else:
            try:
                word = prs.inflect({pol, 'sing', padej}).word
            except Exception:
                return True
    return False


def adding(word, speech):
        commands = getting()
        dct = {"прил": (1, commands['прил'], 'ADJF', "прил"), "сущ": (2, commands['сущ'], 'NOUN', "сущ"), "глаг": (3, commands['глаг'], 'VERB', "глаг")}
        pos = morph.parse(word)[0].tag.POS
        if not pos:
            return 'Введено неккоректное слово'
        if speech not in dct.keys() or dct[speech][2] != pos:
            return 'Неккоректно указана часть речи'
        if word.lower() in dct[speech][1]:
            return 'Слово уже есть в базе данных'
        if trying(word, dct[speech][2]):
            return 'Слово не подходит по критериям'
        
        con = sqlite3.connect("DataBase.sqlite")
        cur = con.cursor()
        cur.execute("INSERT INTO words(word, part) VALUES(?, ?)",
                    (word.lower(), dct[speech][3])).fetchall()
        con.commit()
        con.close()
        return 'Слово было успешно добавлено'


@router_lolgen.message(Command("lolgen"))
async def do_lol(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    args = command.args if command.args else ''
    if '<' in args:
        args = args.replace('<', '')
    if '>' in args:
        args = args.replace('>', '')
    if not args:
        try:
            args = last_command[msg.from_user.id]
        except Exception as e:
            last_massage[msg.from_user.id] = ("lolgen", )
            log(msg, ('Команда /lolgen не получила схему',))
            await msg.reply("Необходимо передать схему предложения хотя бы раз")
            return None
    else:
        last_command[msg.from_user.id] = args
    try:
        text = brain(order=args)
    except Exception as e:
        last_massage[msg.from_user.id] = ("lolgen", )
        log(msg, ('Команда /lolgen:', f'ОШИБКА - {e}, запрос - {args}'), error=True)
        await msg.reply("Что-то пошло не так")
        return None
    last_massage[msg.from_user.id] = ("lolgen", )
    log(msg, ('Команда /lolgen выполнила свою работу:', text))
    await msg.reply(text)



@router_lolgen.message(Command("word"))
async def adding_word(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)

    if not command.args:
        last_massage[msg.from_user.id] = ("word", )
        log(msg, ('Команда /word не получила аргументов',))
        await msg.reply("Нужно ввести слово и его часть речи")
        return None
    leest = command.args.split(' ')
    if len(leest) != 2:
        last_massage[msg.from_user.id] = ("word", )
        log(msg, ('Команда /word получила не 2 аргумента:', command.args))
        await msg.reply('Нужно ввести только одно слово и его часть речи')
        return None
    result = adding(leest[0], leest[1])
    last_massage[msg.from_user.id] = ("word", )
    log(msg, ('Команда /word выполнила свою работу с результатом:', result, command.args))
    await msg.reply(result)