from aiogram import Router, Bot
# Работа с сообщениями
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from scripts.Logs import autorisation
from scripts.help import numeral, to_ten, sft, get_RPN


info_router = Router()  # Обработчик для решения информатики


@info_router.message(Command("numeral"))
async def start_handler(msg: Message, command: CommandObject, bot: Bot):  # Перевод в другую СС
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None
    
    args = command.args.split(' ') if command.args else []
    if len(args) < 2:  # Нехватает аргументов
        await msg.reply("Нужно ввести число и его систему счисления")
        await user.log("Command /numeral: пользователь передал меньше двух аргументов")
        return None
    
    elif len(args) == 2:  # Перевод из 10-ой СС
        if args[1] not in ("double", "float"):  # Если нужно перевести в СС с целым основанием
            try:
                result = numeral(int(args[0]), int(args[1]))
            except Exception as e:
                await msg.reply("Нужно ввести число и его систему счисления")
                await user.log("Command /numeral: пользователь передал некорректные аргументы:", *repr(e).split("\n"), "Запрос: " + command.args)
                return None
        
        else:  # Если нужно перевести в машинный код
            try:
                num, use = float(args[0].replace(',', '.')), args[1]
                result = sft(num, use)
                if not result[0]:
                    await msg.reply("Извини, произошла непредвиденная ошибка. Попробуй ввести другое число :(")
                    await user.log(text=("Script /numeral: была допущена ошибка", command.args), folder="errors")
                    return None
                
                line_1, line_2 = result[:4], hex(int(result[:4], 2))[2:].upper()
                for i in range(4, len(result), 4):
                    line_1 += '.' + result[i:i + 4]
                    line_2 += (' ' if i != 0 and (i // 4) % 2 == 0 else '') + hex(int(result[i:i + 4], 2))[2:].upper()
                result = ("bin: " + line_1, "hex: " + line_2)
                await user.log(f"Command /numeral: перевод числа {num} в {use}:", *result)
            except Exception as e:
                await msg.reply("Нужно ввести число и его систему счисления")
                await user.log("Command /numeral: пользователь передал некорректные аргументы:", *repr(e).split("\n"), "Запрос: " + command.args)
                return None
        
    else:  # Перевод из указанной СС в указанную
        try:
            result = str(to_ten(args[0], int(args[1])))
            if args[2] != "10":
                result = numeral(int(result), int(args[2]))
        except Exception as e:
            await msg.reply("Нужно ввести число и его систему счисления")
            await user.log("Command /numeral: пользователь передал некорректные аргументы:", *repr(e).split("\n"), "Запрос: " + command.args)
            return None
        
    await msg.reply(result)
    await user.log("Command /numeral: работа завершена", "Запрос: " + command.args, "Ответ: " + result)


@info_router.message(Command("post"))
async def start_handler(msg: Message, command: CommandObject, bot: Bot):  # Перевод в постфиксный вид
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    if not command.args:
        await msg.reply("Нужно ввести выражение сразу после команды")
        await user.log("Commad /post: пользователь не передал выражение " + command.args)
        return None
    
    try:
        text = command.args.replace("(", '( ').replace(")", ' )').replace("  ", ' ').split(' ')
        result = ' '.join(get_RPN(text))
    except Exception as e:
        await msg.reply("Что-то пошло не так, попробуйте ввести другое выражение")
        await user.log("Command /post: получено некорректное выражение", *repr(e).split("\n"), "Запрос: " + command.args)
        return None
    
    await msg.reply(result)
    await user.log("Command /numeral: работа завершена", "Запрос: " + command.args, "Ответ: " + result)