from os import path, mkdir
import datetime


def make_way(msg, folder):
    date = datetime.datetime.now().strftime("%d.%m-%y")
    way = path.join(folder, str(msg.from_user.id))
    if not path.isdir(folder):
        mkdir(folder)
    if not path.isdir(way):
        mkdir(path.join(folder, str(msg.from_user.id)))
    way = path.join(way, date)
    return way

def do_log(msg, text, error=False):
    folder = 'errors' if error else 'logs'
    time = datetime.datetime.now().strftime("%H.%M.%S")
    print(f'______{time}____________{folder}____________{msg.from_user.id}____________{msg.from_user.username}_______')
    way = make_way(msg=msg, folder=folder) + '.txt'
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