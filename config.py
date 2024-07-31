BOT_TOKEN = "6966599649:AAFvCukCMGCOLc_U1nQ95ksCuqeIJ6yVOCw"
ADMIN = (('5091023477', 'markusha_v3'),)
NOT_ADMIN = (('1303717923', 'pppp132132'),)



COMMANDS = {
    "_names_": ["lolgen", "word", "sti"],
    
    "lolgen": ['Предложение из случайных слов по заданной схеме',
               'Схема задаётся после комманды через пробел:',
               '    "lolgen *схема*"', 
               'Ключевые слова:',
               '    "сущ" - использовать в схеме имя существительное;',
               '    "прил" - использовать в схеме имя прилагательное;',
               '    "глаг" - использовать в схеме глагол;',
               'Слова помимо ключевых изменяться не будут',
               'Указав схему хоть раз, можно использовать комманду неограниченное количество раз, создавая предложение по той же схеме',
               'Символы "меньше" и "больше" удаляются из схемы (из-за правил вывода сообщений в чат телеграма)'],
    "word": ['Добавить слово, указав его часть речи',
             'Слово и часть речи задаются после комманды через пробел, разделяются пробелом:',
             '  "word *слово* *часть речи*"',
             'Чтобы часть речи нужно написать укороченный вариант ("сущ", "прил" и "глаг" соответственно для имени существительного, имени прилагательного и глагола)'],
    "sti": ['Заполнить таблицу истинности',
            'Логическое и нужный ответ задаётся после комманды через пробел, разделяются нижним подчёркиванием ("_"):',
            '   "sti *логическое выражение*_*нужный ответ*"',
            'Указав нужный ответ, в таблице будут только те варианты, которые приводят к указанному значению в конце вычислений',
            'Чтобы вывести таблицу полностью, нужно указать только логическое выражение:',
            '   "sti *логическое выражение*"',
            'Логическое выражение может включать до 4 переменных - "x", "y", "z", "w" в строгом порядке использования (нельзя добавлять переменную, не используя предыдущую)']
}


"""
info - Подробное описание всех комманд
lolgen - Предложение из случайных слов
word - Добавить слово, указав его часть речи
sti - Заполнить таблицу истинности
"""

def info(command):
    global COMMANDS
    return '\n'.join(COMMANDS[command])