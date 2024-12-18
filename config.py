with open("token.txt", 'r', encoding="UTF-8") as file:
    BOT_TOKEN = file.readline()  # Токен бота
COMMANDS = {
    "__names__": ["lolgen", "word", "sti", "encode", "decode"],
    
    "lolgen": ['Предложение из случайных слов по заданной схеме',
               'Схема задаётся после команды через пробел:',
               '    "lolgen *схема*"', 
               'Ключевые слова:',
               '    "сущ" - использовать в схеме имя существительное;',
               '    "прил" - использовать в схеме имя прилагательное;',
               '    "глаг" - использовать в схеме глагол;',
               'Слова помимо ключевых изменяться не будут',
               'Указав схему хоть раз, можно использовать команду неограниченное количество раз, создавая предложение по той же схеме',
               'Символы "меньше" и "больше" удаляются из схемы (из-за правил вывода сообщений в чат телеграма)'],
    "word": ['Добавить слово, указав его часть речи',
             'Слово и часть речи задаются после команды через пробел, разделяются пробелом:',
             '  "word *слово* *часть речи*"',
             'Чтобы часть речи нужно написать укороченный вариант ("сущ", "прил" и "глаг" соответственно для имени существительного, имени прилагательного и глагола)'],
    "sti": ['Заполнить таблицу истинности',
            'Логическое и нужный ответ задаётся после команды через пробел, разделяются нижним подчёркиванием ("_"):',
            '   "sti *логическое выражение*_*нужный ответ*"',
            'Указав нужный ответ, в таблице будут только те варианты, которые приводят к указанному значению в конце вычислений',
            'Чтобы вывести таблицу полностью, нужно указать только логическое выражение:',
            '   "sti *логическое выражение*"',
            'Логическое выражение может включать до 4 переменных - "x", "y", "z", "w" в строгом порядке использования (нельзя добавлять переменную, не используя предыдущую)'],
    "encode": ['Закодировать текст',
               'Текст задаётся после команды через пробел:',
               '    "encode *текст*"',
               'Символы "меньше" и "больше" удаляются из схемы (из-за правил вывода сообщений в чат телеграма)'],
    "decode": ['Раскодировать текст',
               'Текст задаётся после команды через пробел:',
               '    "decode *текст*"',
               'Символы "меньше" и "больше" удаляются из схемы (из-за правил вывода сообщений в чат телеграма)'],

    "__admin_names__": ["admin_logs", "admin_errors", "admin_users", "admin_chat"],

    "admin_logs": ['Посмотреть сегодняшние логи указанного пользователя',
                   'username или Id пользователя указывается после команды:',
                   '    "admin_logs *username или Id пользователя*"',
                   'Можно получить логи по дате, указанной по формату "гг-мм.дд" через пробел от username-а или Id пользователя:',
                   '    "admin_logs *username или Id пользователя* *дата*"'],
    "admin_errors": ['Посмотреть сегодняшние ошибки указанного пользователя',
                   'username или Id пользователя указывается после команды:',
                   '    "admin_errors *username или Id пользователя*"',
                   'Можно получить ошибки по дате, указанной по формату "гг-мм.дд" через пробел от username-а или Id пользователя:',
                   '    "admin_errors *username или Id пользователя* *дата*"'],
    "admin_users": ['Получить полный список пользователей',
                    'Список состоит из Id, username-а и уровня прав администратора пользователя, написанными через " ~~~ "'],
    "admin_chat": ['Написать пользователю сообщение',
                   'username или Id пользователя и сообщение задаются после команды через пробел, разделяются пробелом:',
                   '    "admin_chat *username или Id пользователя* *сообщение*"']
    

}


"""
info - Подробное описание всех команд
lolgen - Предложение из случайных слов
word - Добавить слово, указав его часть речи
sti - Заполнить таблицу истинности
"""

def info(command):
    global COMMANDS
    return '\n'.join(COMMANDS[command])