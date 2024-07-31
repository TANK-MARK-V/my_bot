import sqlite3


def get_users(msg=None, info=False):
    con = sqlite3.connect("DataBase.sqlite")
    cur = con.cursor()
    user = tuple(cur.execute('''SELECT * FROM users''').fetchall())
    ids, usernames, admins = tuple(map(lambda x: x[0], user)), tuple(map(lambda x: x[1], user)), tuple(map(lambda x: x[2], user))
    if msg:
        if str(msg.from_user.id) not in ids:
            result = make_user(str(msg.from_user.id), msg.from_user.username, cur, update=False)
            if info:
                user = tuple(cur.execute('''SELECT * FROM users''').fetchall())
                ids, usernames, admins = tuple(map(lambda x: x[0], user)), tuple(map(lambda x: x[1], user)), tuple(map(lambda x: x[2], user))
            con.commit()
            con.close()
            if not info:
                return result
        if msg.from_user.username not in usernames:
            result = make_user(str(msg.from_user.id), msg.from_user.username, cur, update=True)
            if info:
                user = tuple(cur.execute('''SELECT * FROM users''').fetchall())
                ids, usernames, admins = tuple(map(lambda x: x[0], user)), tuple(map(lambda x: x[1], user)), tuple(map(lambda x: x[2], user))
            con.commit()
            con.close()
            if not info:
                return result
        if not info:
            return False
    if info in usernames:
        ind = usernames.index(info)
        return (ids[ind], usernames[ind], admins[ind])
    if info in ids:
        ind = ids.index(info)
        return (ids[ind], usernames[ind], admins[ind])
    return False
        



def make_user(id, username, cur, update):
    if update:
        cur.execute(f"""UPDATE users SET username = '{username}' WHERE id = {id}""").fetchall()
        return ('Информация о пользователе была обновлена:', f'{id}, {username}')
    cur.execute(f"""INSERT INTO users (id, username, admin) VALUES ('{id}', '{username}', 0)""").fetchall()
    return ('Добавлен новый пользователь:', f'{id}, {username}')