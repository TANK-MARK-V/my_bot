import sqlite3


def get_user_list():
    con = sqlite3.connect("data/DataBase.sqlite")
    cur = con.cursor()
    users = tuple(cur.execute('''SELECT id, username, access, ban FROM users''').fetchall())
    con.close()
    return users


def make_user(msg):
    con = sqlite3.connect("data/DataBase.sqlite")
    cur = con.cursor()
    all_user = tuple(cur.execute('''SELECT id, username FROM users''').fetchall())  # Получение информации о пользователях
    ids, usernames = tuple(map(lambda x: x[0], all_user)), tuple(map(lambda x: x[1], all_user))
    result = False
    if str(msg.from_user.id) not in ids:  # Пользователя нет в базе данных
        cur.execute(f"INSERT INTO users (id, username)" +
                    f"VALUES ('{msg.from_user.id}', '{msg.from_user.username if msg.from_user.username != 'None' else msg.from_user.id}')").fetchall()
        result = ('Добавлен новый пользователь:', f'{msg.from_user.id}, {msg.from_user.username}, {msg.from_user.full_name.replace("<", "").replace(">", "")}')

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
    con.commit()
    con.close()
    return result


def update_user(id, changes):
    con = sqlite3.connect("data/DataBase.sqlite")
    cur = con.cursor()
    columns = ', '.join(tuple(f"{i} = '{changes[i]}'" for i in changes))
    cur.execute(f"UPDATE users SET {columns} WHERE id = '{id}'").fetchall()
    con.commit()
    con.close()


def find_user(info):
    con = sqlite3.connect("data/DataBase.sqlite")
    cur = con.cursor()
    users = tuple(cur.execute('''SELECT id, username, access, ban FROM users''').fetchall())
    ids, usernames = tuple(map(lambda x: str(x[0]), users)), tuple(map(lambda x: x[1], users))
    info = str(info).replace('@', '')
    if ''.join(ids).count(info) == 1:
        for i in range(len(ids)):
            if info in ids[i]:
                info = ids[i]
                user = tuple(cur.execute(f"""SELECT id, username, access, ban FROM users WHERE id = '{info}'""").fetchall())[0]
    elif ''.join(usernames).count(info) == 1:
        for i in range(len(usernames)):
            if info in usernames[i]:
                info = usernames[i]
                user = tuple(cur.execute(f"""SELECT id, username, access, ban FROM users WHERE username = '{info}'""").fetchall())[0]
    else:
        user = False
    con.commit()
    con.close()
    return {"id": user[0], "username": user[1], "access": user[2], "ban": user[3]} if user else False


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