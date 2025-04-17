from os import path, mkdir
import datetime
from users import get_user_list


def make_way(msg, folder):
    date = datetime.datetime.now().strftime("%y-%m.%d")
    way = path.join(folder, str(msg.from_user.id))
    if not path.isdir(folder):
        mkdir(folder)
    if not path.isdir(way):
        mkdir(path.join(folder, str(msg.from_user.id)))
    way = path.join(way, date)
    return way

async def do_log(msg, text, bot, error=False):
    folder = 'errors' if error else 'logs'
    time = datetime.datetime.now().strftime("%H.%M.%S")
    way = make_way(msg=msg, folder=folder) + '.txt'
    print(f'______{time}____________{folder}____________{msg.from_user.id}____________{msg.from_user.username}_______')
    if path.isfile(way):
        with open(way, 'a', encoding='UTF-8') as file:
            file.write(time)
            for line in text:
                print("\t" + line)
                file.write("\t" + line)
            file.write('\n')
        print()
    else:
        with open(way, 'w', encoding='UTF-8') as file:
            file.write(time)
            for line in text:
                print("\t" + line)
                file.write("\t" + line)
            file.write('\n')
        print()
    for user in get_user_list():
        if user[2] == 5:
            if str(msg.from_user.id) != user[0]:
                await bot.send_message(user[0], f'{msg.from_user.id}{(" ~~~ @" + str(msg.from_user.username)) if msg.from_user.username else ""}\n' + '\n'.join(text))