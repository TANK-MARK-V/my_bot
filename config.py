with open("data/token.txt", 'r', encoding="UTF-8") as file:
    BOT_TOKEN = file.readline()  # Токен бота
COMMANDS = {
    "__names__": ["lolgen", "word", "sti", "evo", "encode", "decode"],
    
    "lolgen": ['Предложение из случайных слов по заданной схеме',
               'Схема задаётся после команды через пробел:',
               '    "lolgen *схема*"', 
               'Ключевые слова:',
               '    "сущ" - использовать в схеме имя существительное;',
               '    "прил" - использовать в схеме имя прилагательное;',
               '    "глаг" - использовать в схеме глагол;',
               'Слова, помимо ключевых, изменяться не будут',
               'Указав схему хоть раз, можно использовать команду неограниченное количество раз, создавая предложение по той же схеме',
               'Символы "меньше" и "больше" удаляются из схемы (из-за правил вывода сообщений в чат)'],
    "word": ['Добавить слово в базу данных lolgen, указав его часть речи',
             'Слово и часть речи задаются после команды через пробел, разделяются пробелом:',
             '  "word *слово* *часть речи*"',
             'Чтобы указать часть речи, нужно написать укороченный вариант ("сущ", "прил" и "глаг" соответственно для имени существительного, имени прилагательного и глагола)'],
    "sti": ['Заполнить таблицу истинности',
            'Логическое выражение задаётся после команды через пробел:',
            '   "sti *логическое выражение*"',
            'Логическое выражение может включать до 4 переменных - "x", "y", "z", "w" - в строгом порядке использования (нельзя добавлять переменную, не используя предыдущую)',
            'Переменные и действия нужно отделять друг от друга хотя бы одним пробелом'],
    "evo": ['Решить задание с исполнителем (23 задание ЕГЭ по информатике на момент написания кода)',
            'Может решить большинство заданий с обязазательным или/и избегаемым этапом (не важно, избегать нужно цифру, или число)',
            'Поддерживает условие, когда одна команда не может повторяться больше двух раз подряд',
            'Чтобы ввести несколько чисел, нужно разделить их пробелом'],
    "encode": ['Закодировать введённые сообщения',
               'Символы "меньше" и "больше" удаляются из схемы (из-за правил вывода сообщений в чат)',
               'Чтобы начать/закончить зашифровку сообщений, введите команду'],
    "decode": ['Раскодировать введённые сообщения',
               'Символы "меньше" и "больше" удаляются из схемы (из-за правил вывода сообщений в чат)',
               'Чтобы начать/закончить расшифровку сообщений, введите команду'],

    "__admin_names__": ["logs", "errors", "users", "chat"],

    "logs": ['Посмотреть сегодняшние логи указанного пользователя',
             'username или Id пользователя указывается после команды:',
             '    "logs *username или Id пользователя*"',
             'Можно получить логи по дате, указанной по формату "гг-мм.дд" через пробел от username-а или Id пользователя:',
             '    "logs *username или Id пользователя* *дата*"'],
    "errors": ['Посмотреть сегодняшние ошибки указанного пользователя',
               'username или Id пользователя указывается после команды:',
               '    "errors *username или Id пользователя*"',
               'Можно получить ошибки по дате, указанной по формату "гг-мм.дд" через пробел от username-а или Id пользователя:',
               '    "errors *username или Id пользователя* *дата*"'],
    "users": ['Получить полный список пользователей',
              'Список состоит из Id, username-а и уровня прав администратора пользователя, написанными через " ~~~ "'],
    "chat": ['Написать пользователю сообщение',
            'username или Id пользователя и сообщение задаются после команды через пробел, разделяются пробелом:',
            '    "chat *username или Id пользователя* *сообщение*"',
            'Символы "меньше" и "больше" удаляются из схемы (из-за правил вывода сообщений в чат)']
    

}


LEVELS = {
    "logs": 4,
    "errors": 4,
    "users": 4,
    "chat": 4
}


"""
info - Подробное описание всех команд
lolgen - Предложение из случайных слов
word - Добавить слово, указав его часть речи
sti - Заполнить таблицу истинности
evo - Решить задание с исполнителем
encode - Закодировать текст
decode - Раскодировать текст
valentine - Получи валентинку
verbs - Неправильные глаголы
atom - Решение задач по физике
"""

def info(command):
    if command in COMMANDS.keys():
        return '\n'.join(COMMANDS[command])


last_massage = {}