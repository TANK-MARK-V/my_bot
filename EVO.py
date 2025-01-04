from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from logs import do_log as log
from users import get_users
from config import last_massage

router_evo = Router()


class EVO:
    def __init__(self, commands, through=None, escape=None, inverse=False, double=0) -> None:
        self.commands = commands
        self.through = through
        self.escape = escape
        self.inverse = inverse
        self.double = double

        # self.history = {}


    def alg(self, number, end, last=0):
        # n_truth = truth
        # n_truth += 1 if self.through and number in self.through else 0
        # Этот код отвечал за "обязательные" числа
        if number == end:
            return 1
        if not self.inverse and number > end or self.inverse and number < end:  # Число уже ушло за нужное
            if not self.double or\
                    self.double and last == self.double or\
                    last != self.double and eval(str(number) + self.commands[self.double - 1]) != end:  # Последняя возможность получить нужное число
                return 0
        if type(self.escape) is set and len(set(str(number)) & self.escape) or\
                type(self.escape) is tuple and number in self.escape:  # Запрещённая цифра в числе или число среди запрещённых
            return 0
        # if number == end:
        #     return int(type(self.through) is tuple and n_truth == len(self.through) or\
        #             type(self.through) is set and n_truth > 0 or\
        #                 self.through is None)
        # Прошёл ли код через все "обязательные" числа
        variants = 0
        for command in self.commands:
            if not (self.double and last == self.double == self.commands.index(command) + 1) and\
                    not (self.inverse and " / " in command and eval(str(number) + command.replace("/", "%"))):
                n_number = int(eval(str(number) + command))
                alged = self.alg(n_number, end, self.commands.index(command) + 1)
                variants += alged
                # if alged != 0:
                #     self.history[number].append((n_number, alged))
                # Добавление в историю
        return variants
    
    
    def evo(self, start, end):
        if self.through:
            all = (start, ) + self.through + (end, )
            result = 1
            for i in range(len(all) - 1):
                result *= self.alg(all[i], all[i + 1])

            return result
        return self.alg(start, end)
    
        
    # def get_history(self):
    #     dct = {}
    #     for key in sorted(self.history.keys()):
    #         if self.history[key]:
    #             dct[key] = self.history[key]
    #     return str(dct)

@router_evo.message(Command("evo"))
async def solving(msg: Message, command: CommandObject):
    
    user = get_users(msg=msg)  # Проверка на наличие пользователя в базе данных
    if user:
        log(msg, user)
    last_massage[msg.from_user.id] = ("evo", 1)
    log(msg, ('Команда /evo начала свою работу', ))
    await msg.reply("Введите команды")


async def step(last, msg):
    if last[1] == 1:
        options = msg.text.split('\n')
        if len(options) < 2:
            log(msg, ('Команда /evo получила меньше двух команд', msg.text))
            await msg.reply("Нужно ввести не меньше двух команд")
            return None
        options = tuple(map(lambda x: ' ' + x if x[0] != ' ' else x, options))
        last_massage[msg.from_user.id] = ("evo", 2, options)
        log(msg, ('Команда /evo получила команды', msg.text))
        await msg.reply("Введите начальное и конечное число")
        return None
    if last[1] == 2:
        options = last_massage[msg.from_user.id][2]
        numbers = msg.text.split(' ')
        if len(numbers) != 2:
            log(msg, ('Команда /evo получила не два числа', msg.text))
            await msg.reply("Нужно ввести только два числа: начальное и конечное")
            return None
        try:
            numbers = tuple(map(lambda x: int(x), numbers))
        except Exception:
            log(msg, ('Команда /evo получила не числа', msg.text))
            await msg.reply("Нужно ввести только два числа: начальное и конечное")
            return None
        last_massage[msg.from_user.id] = ("evo", 3, options, numbers)
        log(msg, ('Команда /evo получила числа', msg.text))
        await msg.reply('Введите числа, которые должна содержать траектория программы. Если таких чисел нет, введите "-"')
        return None
    if last[1] == 3:
        options, numbers = last_massage[msg.from_user.id][2], last_massage[msg.from_user.id][3]
        throughs = None if msg.text == '-' else msg.text.split(' ')
        if throughs:
            try:
                throughs = tuple(map(lambda x: int(x), throughs))
            except Exception:
                log(msg, ('Команда /evo получила не "обязательные" числа', msg.text))
                await msg.reply('Введите числа, которые должна содержать траектория программы. Если таких чисел нет, введите "-"')
                return None
        last_massage[msg.from_user.id] = ("evo", 4, options, numbers, throughs)
        log(msg, ('Команда /evo получила "обязательные" числа', msg.text))
        await msg.reply('Введите числа, которые должна избегать траектория программы. '
        + 'Если траектория программы не должна содержать цифру, начните сообщение с "+". '
        + 'Если таких чисел нет, введите "-"')
        return None
    if last[1] == 4:
        options, numbers, throughs = last_massage[msg.from_user.id][2], last_massage[msg.from_user.id][3], last_massage[msg.from_user.id][4]
        if msg.text[0] == '+':
            escapes = set(msg.text[1:])
            if len(escapes - set('0123456789')):
                log(msg, ('Команда /evo получила не "избегаемые" цифры', msg.text))
                await msg.reply('Введите числа или цифры, которые должна избегать траектория программы. Если таких чисел нет, введите "-"')
                return None
        else:
            escapes = None if msg.text == '-' else msg.text.split(' ')
            if escapes:
                try:
                    escapes = tuple(map(lambda x: int(x), escapes))
                except Exception:
                    log(msg, ('Команда /evo получила не "избегаемые" числа', msg.text))
                    await msg.reply('Введите числа или цифры, которые должна избегать траектория программы. Если таких чисел нет, введите "-"')
                    return None
        last_massage[msg.from_user.id] = ("evo", 5, options, numbers, throughs, escapes)
        log(msg, ('Команда /evo получила "избегаемые" числа или цифры', msg.text))
        await msg.reply('Введите номер команды, которая не должна повторяться. Если такого условия нет, введите "-"')
        return None
    if last[1] == 5:
        options, numbers = last_massage[msg.from_user.id][2], last_massage[msg.from_user.id][3]
        throughs, escapes = last_massage[msg.from_user.id][4], last_massage[msg.from_user.id][5]
        double = 0 if msg.text == '-' else msg.text
        try:
            double = int(double)
        except Exception:
            log(msg, ('Команда /evo получила не номер команды', msg.text))
            await msg.reply('Введите номер команды, которая не должна повторяться. Если такого условия нет, введите "-"')
            return None
        if double > len(options) or double < 0:
            log(msg, ('Команда /evo получила номер несуществующей команды', msg.text))
            await msg.reply('Введите номер команды, которая не должна повторяться. Если такого условия нет, введите "-"')
            return None
        log(msg, ('Команда /evo получила номер команды', msg.text))
        try:
            out = str(EVO(options, through=throughs, escape=escapes, inverse=numbers[0] > numbers[1], double=double).evo(numbers[0], numbers[1]))
        except Exception as e:
            last_massage[msg.from_user.id] = ("evo", )
            log(msg, ('Команда /evo:', f'ОШИБКА - {e}'), error=True)
            await msg.reply("Что-то пошло не так")
            return None
        last_massage[msg.from_user.id] = ("evo", )
        log(msg, ('Команда /evo выполнила свою работу', ))
        await msg.reply(out)
        return None