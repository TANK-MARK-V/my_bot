from os import path, mkdir
import datetime
from users import get_user_list, find_user


def make_way(msg, folder):
    date = datetime.datetime.now().strftime("%y-%m.%d")
    way_to_user = path.join(folder, str(msg.from_user.id))
    if not path.isdir(folder):
        mkdir(folder)
    if not path.isdir(way_to_user):
        mkdir(path.join(folder, str(msg.from_user.id)))
    return path.join(way_to_user, date) + '.txt', path.join("daily_logs", date) + '.txt'


async def do_log(msg, text, bot, error=False):
    if find_user(msg.from_user.id)["access"] == 6:
        return None
    folder = 'errors' if error else 'logs'
    time = datetime.datetime.now().strftime("%H.%M.%S")
    way_to_user, way_to_daily = make_way(msg=msg, folder=folder)

    if path.isfile(way_to_daily):
        daily_log = open(way_to_daily, 'a', encoding='UTF-8')
    else:
        daily_log = open(way_to_daily, 'w', encoding='UTF-8')
    if path.isfile(way_to_user):
        user_log = open(way_to_user, 'a', encoding='UTF-8')
    else:
        user_log = open(way_to_user, 'w', encoding='UTF-8')

    info = f'______{time}____________{folder}____________{msg.from_user.id}____________{msg.from_user.username}__________{msg.from_user.full_name}_______'

    print(info)
    daily_log.write(info + '\n')
    user_log.write(time)

    for line in text:
        print("\t" + line)
        daily_log.write("\t" + line)
        user_log.write("\t" + line)
    
    print()
    daily_log.write('\n' * 2)
    user_log.write('\n')

    daily_log.close()
    user_log.close()

    for user in get_user_list():
        if user[2] >= 5:
            if str(msg.from_user.id) != user[0]:
                await bot.send_message(user[0], f'{msg.from_user.id}{(" ~~~ @" + str(msg.from_user.username)) if msg.from_user.username else ""}\n' + '\n'.join(text))
    return True