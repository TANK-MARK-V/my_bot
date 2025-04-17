import sqlite3


def get_users(msg=None, info=False):
    """
    msg: Обновить информацию о пользователе в базе данных\n
    info: Получить данные о пользователе из базы дааных. Необходмо передать ID или username
    """
    con = sqlite3.connect("data/DataBase.sqlite")
    cur = con.cursor()
    all_user = tuple(cur.execute('''SELECT id, username, admin FROM users''').fetchall())  # Получение информации о пользователях
    ids, usernames, admins = tuple(map(lambda x: x[0], all_user)), tuple(map(lambda x: x[1], all_user)), tuple(map(lambda x: x[2], all_user))
    if msg:
        result = False
        if str(msg.from_user.id) not in ids:  # Пользователя нет в базе данных
            cur.execute(f"""INSERT INTO users (id, username, admin) VALUES ('{msg.from_user.id}', '{msg.from_user.username}', 0)""").fetchall()
            result = ('Добавлен новый пользователь:', f'{msg.from_user.id}, {msg.from_user.username}')

        elif msg.from_user.username not in usernames and (str(msg.from_user.id) not in usernames or msg.from_user.username != None):  # Пользователь изменил свой username
            name = str(msg.from_user.id) if msg.from_user.username == None else msg.from_user.username  # Если у пользователя нет username, то будет использоваться id
            cur.execute(f"""UPDATE users SET username = '{name}' WHERE id = '{msg.from_user.id}'""").fetchall()
            result = ('Информация о пользователе была обновлена:', f'{msg.from_user.id}, {name}')

        elif msg.from_user.username in usernames and usernames.index(msg.from_user.username) != ids.index(str(msg.from_user.id)):  # username уже есть в таблице, но не принадлежит пользователю
            cur.execute(f"""UPDATE users SET username = '{ids[usernames.index(msg.from_user.username)]}'
                            WHERE id = '{ids[usernames.index(msg.from_user.username)]}'""").fetchall()  # Поменять существующий username на id пользователя
            cur.execute(f"""UPDATE users SET username = '{msg.from_user.username}' WHERE id = '{msg.from_user.id}'""").fetchall()
            result = ('Информация о пользователях обновлена:', f"{msg.from_user.id}, {msg.from_user.username}; " +
                      f"{ids[usernames.index(msg.from_user.username)]}, {ids[usernames.index(msg.from_user.username)]}")

        all_user = tuple(cur.execute('''SELECT id, username, admin FROM users''').fetchall())  # Обновление информации о пользователях
        ids, usernames, admins = tuple(map(lambda x: x[0], all_user)), tuple(map(lambda x: x[1], all_user)), tuple(map(lambda x: x[2], all_user))
        con.commit()
        con.close()        
        if not info:
            return result
    if info[0] == '@':
        info = info[1:]
    if ''.join(usernames).count(info) == 1:
        for i in range(len(usernames)):
            if info in usernames[i]:
                return (ids[i], usernames[i], admins[i])
    elif ''.join(ids).count(info) == 1:
        for i in range(len(ids)):
            if info in ids[i]:
                return (ids[i], usernames[i], admins[i])
    return False
        

def get_user_list():
    con = sqlite3.connect("data/DataBase.sqlite")
    cur = con.cursor()
    users = tuple(cur.execute('''SELECT id, username, admin FROM users''').fetchall())
    con.close()
    return users


def set_score(where, username, score):
    con = sqlite3.connect("data/DataBase.sqlite")
    cur = con.cursor()
    past = cur.execute(f'''SELECT {where}_score FROM users WHERE username = "{username}"''').fetchall()[0][0]
    if score >= past:
        cur.execute(f"""UPDATE users SET {where}_score = {score} WHERE username = '{username}'""").fetchall()
        con.commit()
        scores = sorted(list(set(map(lambda x: x[0], cur.execute(f'''SELECT {where}_score FROM users''').fetchall()))))[::-1]
        con.close()
        return (f'{scores.index(score) + 1} место', True)
    return ('Результат не пошёл в таблицу', False)


def get_score(where):
    con = sqlite3.connect("data/DataBase.sqlite")
    cur = con.cursor()
    results = cur.execute(f'''SELECT username, {where}_score FROM users''').fetchall()
    table = dict()
    for user in results:
        if user[1] == -1:
            continue
        if user[1] not in table.keys():
            table[user[1]] = [user[0], ]
        else:
            table[user[1]].append(user[0])
    con.close()
    return table