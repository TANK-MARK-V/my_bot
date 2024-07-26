import random as rn
import pymorphy3
import sqlite3


# Импортируем нужные библиотеки

morph = pymorphy3.MorphAnalyzer()  # Создаём представитель класса pymorthy для анализа и склонения слов


def getting():  # Функция для считывания слов из БД
    con = sqlite3.connect("DataBase.sqlite")
    cur = con.cursor()
    pril = cur.execute('''SELECT word FROM Massive
                                  WHERE part in (
                                      SELECT id FROM Part
                                          WHERE speech = 'прил') AND standart in (
                                              SELECT num FROM test)''').fetchall()
    sus = cur.execute('''SELECT word FROM Massive
                                 WHERE part in (
                                     SELECT id FROM Part
                                         WHERE speech = 'сущ') AND standart in (
                                             SELECT num FROM test)''').fetchall()
    glag = cur.execute('''SELECT word FROM Massive
                                  WHERE part in (
                                      SELECT id FROM Part
                                          WHERE speech = 'глаг') AND standart in (
                                              SELECT num FROM test)''').fetchall()
    con.commit()
    con.close()
    commands = {
        'сущ': [i[0] for i in sus],
        'прил': [i[0] for i in pril],
        'глаг': [i[0] for i in glag]
    }
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
        con = sqlite3.connect("DataBase.sqlite")
        cur = con.cursor()
        dct = {"прил": (1, commands['прил'], 'ADJF'), "сущ": (2, commands['сущ'], 'NOUN'), "глаг": (3, commands['глаг'], 'VERB')}
        
        if word.lower() in dct[speech][1]:  # Критерии добавления слов
            return 'Слово уже есть в базе данных'
        if dct[speech][2] not in morph.parse(word)[0].tag.POS:
            return 'Неккоректно указана часть речи'
        if trying(word, dct[speech][2]):
            return 'Слово не подходит по критериям'
        
        cur.execute("INSERT INTO Massive(word, part, standart) VALUES(?, ?, 1)",
                    (word.lower(), dct[speech][0])).fetchall()
        con.commit()
        con.close()
        return 'Слово было успешно добавлено'