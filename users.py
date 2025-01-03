import sqlite3


def get_users(msg=None, info=False):
    con = sqlite3.connect("DataBase.sqlite")
    cur = con.cursor()
    all_user = tuple(cur.execute('''SELECT * FROM users''').fetchall())  # Получение информации о пользователях
    ids, usernames, admins = tuple(map(lambda x: x[0], all_user)), tuple(map(lambda x: x[1], all_user)), tuple(map(lambda x: x[2], all_user))
    if msg:
        result = False
        if str(msg.from_user.id) not in ids:
            cur.execute(f"""INSERT INTO users (id, username, admin) VALUES ('{msg.from_user.id}', '{msg.from_user.username}', 0)""").fetchall()
            result = ('Добавлен новый пользователь:', f'{msg.from_user.id}, {msg.from_user.username}')

        elif msg.from_user.username not in usernames:
            cur.execute(f"""UPDATE users SET username = '{msg.from_user.username}' WHERE id = '{msg.from_user.id}'""").fetchall()
            result = ('Информация о пользователе была обновлена:', f'{msg.from_user.id}, {msg.from_user.username}')

        elif usernames.index(msg.from_user.username) != ids.index(str(msg.from_user.id)):  # username уже есть в таблице, но не принадлежит пользователю

            if msg.from_user.username == 'None' and usernames[ids.index(str(msg.from_user.id))] != msg.from_user.username:  # Пользователь удалил свой username
                cur.execute(f"""UPDATE users SET username = 'None' WHERE id = '{msg.from_user.id}'""").fetchall()
                result = ('Информация о пользователе была обновлена:', f'{msg.from_user.id}, {msg.from_user.username}')
            else:  # Если username уже принадлежит другому
                cur.execute(f"""UPDATE users SET username = 'None'
                                WHERE id = '{ids[usernames.index(msg.from_user.username)]}'""").fetchall()  # Поменять существующий username на 'None'
                cur.execute(f"""UPDATE users SET username = '{msg.from_user.username}' WHERE id = '{msg.from_user.id}'""").fetchall()
                result = ('Информация о пользователях обновлена:', f"{msg.from_user.id}, {msg.from_user.username}; {ids[usernames.index(msg.from_user.username)]}, 'None'")
        all_user = tuple(cur.execute('''SELECT * FROM users''').fetchall())  # Обновление информации о польхователях
        ids, usernames, admins = tuple(map(lambda x: x[0], all_user)), tuple(map(lambda x: x[1], all_user)), tuple(map(lambda x: x[2], all_user))
        con.commit()
        con.close()        
        if not info:
            return result
    if info in usernames:
        ind = usernames.index(info)
        return (ids[ind], usernames[ind], admins[ind])
    if info in ids:
        ind = ids.index(info)
        return (ids[ind], usernames[ind], admins[ind])
    return False
        

def get_user_list():
    con = sqlite3.connect("DataBase.sqlite")
    cur = con.cursor()
    users = tuple(cur.execute('''SELECT * FROM users''').fetchall())
    con.close()
    return users