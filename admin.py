from aiogram import Router, Bot, types, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from config import autorisation, last_massage, LEVELS
from logs import do_log as log
from users import get_user_list, find_user, update_user
from free_handler import free_handler
from scripts.Verbs import write_verbs
from scripts.Lolgen.Lolgen import deleting

from os import path
import datetime

router_admin = Router()


class RequestData(StatesGroup):
    verbs = State()
    id = State()
    user = State()
    words = State()


#                                                                               Получить уровень доступа
@router_admin.message(Command("admin"))
async def admin(msg: Message, bot: Bot):

    last_massage[msg.from_user.id] = ("admin", )

    result = await autorisation(bot, msg=msg)  # Авторизация пользователя
    if not result:
        return None

    user = find_user(msg.from_user.id)
    await log(msg, (f'Пользователь обладает правами доступа уровня {user["access"]}', ), bot)
    await msg.reply(f'Вы обладаете правами доступа уровня {user["access"]}')
    return None


#                                                                               Получить список пользователей
@router_admin.message(Command("users"))
async def user_list(msg: Message, bot: Bot):

    last_massage[msg.from_user.id] = ("users", )

    result = await autorisation(bot, msg=msg, need=LEVELS["users"])  # Авторизация пользователя
    if not result:
        return None
    
    text = []
    for line in get_user_list():
        text.append(f"{line[0]} ~~~ @{line[1]} ~~~ {line[2]} ~~~ {line[3]}")
    await log(msg, (f'/users - получена информация о пользователях', ), bot)
    await msg.reply('\n'.join(text))
    return None

#                                                                               Написать пользователю
@router_admin.message(Command("chat"))
async def admin_chat(msg: Message, command: CommandObject, bot: Bot):

    result = await autorisation(bot, msg=msg, need=LEVELS["chat"])  # Авторизация пользователя
    if not result:
        return None
    
    if not command.args:
        if msg.from_user.id in last_massage.keys() and last_massage[msg.from_user.id][0] == "chat" and len(last_massage[msg.from_user.id]) > 1:
            await log(msg, (f'/chat - пользователь закончил чат', ), bot)
            await msg.reply(f"Сообщения больше не отправляются")
            return None
        await log(msg, (f'/chat - пользователь не передал информацию о пользователе', ), bot)
        await msg.reply(f"Не была указана информация о пользователе")
        return None
    
    wanted = find_user(info=command.args)
    if not wanted:
        await log(msg, (f'/chat - нужный пользователь не существует:', command.args), bot)
        await msg.reply(f"Такого пользователя не существует")
        return None
    
    last_massage[msg.from_user.id] = ("chat", wanted)
    await log(msg, (f'/chat - пользователь начал чат с другим пользователем:', wanted["id"] + ' ~~~ ' + wanted["username"]), bot)
    await msg.reply(f'Пользователь @{wanted["username"]} найден. Напишите сообщение')
    return None



#                                                                               Получить логи пользователя
@router_admin.message(Command("logs"))
async def admin_logs(msg: Message, command: CommandObject, bot: Bot):
    
    last_massage[msg.from_user.id] = ("logs", )

    result = await autorisation(bot, msg=msg, need=LEVELS["logs"])  # Авторизация пользователя
    if not result:
        return None
    
    if not command.args:
        await log(msg, (f'/logs - пользователь не передал аргументов', ), bot)
        await msg.reply(f"Некорректно введена команда")
        return None
    args = command.args.split(' ')
    wanted = find_user(info=args[0])
    if not wanted:
        await log(msg, (f'/logs - искомый пользователь не существует:', command.args), bot)
        await msg.reply(f"Такого пользователя не существует")
        return None
    args[0] = wanted["id"]
    if len(args) == 1:
        args.append(datetime.datetime.now().strftime("%y-%m.%d"))
    way = f"{path.join('logs', *args)}.txt"
    if not path.isfile(way):
        await log(msg, (f'/logs:', f'файл не найден - {way}'), bot)
        await msg.reply('Файл не найден')
        return None
    await log(msg, (f'/logs:', f'файл найден - {way}'), bot)
    text = FSInputFile(way)
    await msg.reply_document(text)
    return None

#                                                                               Получить ошибки пользователя
@router_admin.message(Command("errors"))
async def admin_errors(msg: Message, command: CommandObject, bot: Bot):
    
    last_massage[msg.from_user.id] = ("errors", )

    result = await autorisation(bot, msg=msg, need=LEVELS["errors"])  # Авторизация пользователя
    if not result:
        return None
    
    if not command.args:
        await log(msg, (f'/errors - пользователь не передал аргументов', ), bot)
        await msg.reply(f"Некорректно введена команда")
        return None
    args = command.args.split(' ')
    wanted = find_user(info=args[0])
    if not wanted:
        await log(msg, (f'/errors - искомый пользователь не существует:', command.args), bot)
        await msg.reply(f"Такого пользователя не существует")
        return None
    args[0] = wanted["id"]
    if len(args) == 1:
        args.append(datetime.datetime.now().strftime("%y-%m.%d"))
    way = f"{path.join('errors', *args)}.txt"
    if not path.isfile(way):
        await log(msg, (f'/errors:', f'файл не найден - {way}'), bot)
        await msg.reply('Файл не найден')
        return None
    await log(msg, (f'/errors:', f'файл найден - {way}'), bot)
    text = FSInputFile(way)
    await msg.reply_document(text)
    return None


@router_admin.message(Command("ban"))
async def data(msg: Message, command: CommandObject, bot: Bot):
    
    last_massage[msg.from_user.id] = ("ban", )

    result = await autorisation(bot, msg=msg, need=LEVELS["data"])  # Авторизация пользователя
    if not result:
        return None
    
    if not command.args:
        await log(msg, (f'/ban - пользователь не передал аргументов', ), bot)
        await msg.reply(f"Некорректно введена команда")
        return None

    args = command.args.split(' ')
    wanted = find_user(args[0])

    if not wanted:
        await log(msg, (f'/logs - искомый пользователь не существует:', command.args), bot)
        await msg.reply(f"Такого пользователя не существует")
        return None
    try:
        if len(args) == 1:
            update_user(id = wanted["id"], changes={"access": 0})
        else:
            update_user(id = wanted["id"], changes={"access": 0, "ban": " ".join(args[1:])})
    except Exception:
        await log(msg, ('Команда /ban', msg.text), bot, error=True)
        await msg.reply("Что-то пошло не так")
        return None
    await log(msg, ('Команда /data - users выполнила свою работу', msg.text), bot)
    await msg.reply(f'Пользователь @{wanted["username"]} был заблокирован по причине {" ".join(args[1:])}')
    return None


#                                                                               Работа с файлами
@router_admin.message(Command("data"))
async def data(msg: Message, bot: Bot):

    last_massage[msg.from_user.id] = ("data", )
    
    result = await autorisation(bot, msg=msg, need=LEVELS["data"])  # Авторизация пользователя
    if not result:
        return None
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text='Неправильные глаголы', callback_data='change_verbs'))
    builder.add(types.InlineKeyboardButton(text='Пользователи', callback_data='change_users'))
    builder.add(types.InlineKeyboardButton(text='Слова для lolgen', callback_data='change_words'))
    builder.adjust(1, 1, 1)
    await msg.reply('Что нужно редактировать', reply_markup=builder.as_markup())
    await log(msg, (f'/data запущена', ), bot)
    return None


@router_admin.callback_query(F.data.startswith("change_"))
async def changer(callback: types.CallbackQuery, bot: Bot, state: FSMContext):

    result = await autorisation(bot, callback=callback, need=LEVELS["data"])  # Авторизация пользователя
    if not result:
        return None

    await log(callback, (f'Выбран вариант {callback.data}',), bot)
    await callback.answer()
    if callback.data == 'change_verbs':
        last_massage[callback.from_user.id] = ("data", "verbs")
        await callback.message.answer(f"Введите слова, которые нужно добавить")
        await state.set_state(RequestData.verbs)
        return None
    if callback.data == 'change_users':
        last_massage[callback.from_user.id] = ("data", "users")
        await callback.message.answer(f"Введите id или username пользователя")
        await state.set_state(RequestData.id)
        return None
    if callback.data == 'change_words':
        last_massage[callback.from_user.id] = ("data", "words")
        await callback.message.answer(f"Введите слово, которое хотите удалить")
        await state.set_state(RequestData.words)
        return None
    

@router_admin.message(RequestData.verbs)
async def get_verbs(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg, need=LEVELS["data"])  # Авторизация пользователя
    if not result:
        return None
    
    if last_massage[msg.from_user.id] != ("data", "verbs"):
        await state.clear()
        await free_handler(msg, bot)
        return None
    
    text = msg.text.split('_')
    try:
        base, past, part = [], [], []
        for verb in text:
            kinds = verb.split('-')
            base.append(kinds[0])
            past.append(kinds[1])
            part.append(kinds[2])
        write_verbs(new_words=(base, past, part))
    except Exception:
        await log(msg, ('Команда /data - verbs', msg.text), bot, error=True)
        await msg.reply("Что-то пошло не так")
        return None
    await log(msg, ('Команда /data - verbs выполнила свою работу', ), bot)
    await msg.reply('Глаголы были успешно добавлены')
    return None


@router_admin.message(RequestData.id)
async def get_id(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg, need=LEVELS["data"])  # Авторизация пользователя
    if not result:
        return None

    if last_massage[msg.from_user.id] != ("data", "users"):
        await state.clear()
        await free_handler(msg, bot)
        return None
    
    print(msg.text)
    wanted = find_user(info=msg.text)
    if not wanted:
        await log(msg, (f'Пользователь некорректно ввёл информацию о пользователе:', msg.text), bot)
        await msg.reply(f"Некорректно введена информация о пользователе")
        return None
    await log(msg, ('Команда /data получила данные о пользователе', msg.text), bot)
    await msg.reply('Введите изменения')
    await state.update_data(id=wanted['id'])
    await state.set_state(RequestData.user)
    return None


@router_admin.message(RequestData.user)
async def get_user(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg, need=LEVELS["data"])  # Авторизация пользователя
    if not result:
        return None

    if last_massage[msg.from_user.id] != ("data", "users"):
        await state.clear()
        await free_handler(msg, bot)
        return None
    
    changes = {}
    for column in msg.text.split('_'):
        key, value = column.split(' = ')
        changes[key] = value
    id = await state.get_data()
    try:
        update_user(id=id["id"], changes=changes)
    except Exception:
        await log(msg, ('Команда /data - users', msg.text), bot, error=True)
        await msg.reply("Что-то пошло не так")
        return None
    await log(msg, ('Команда /data - users выполнила свою работу', msg.text), bot)
    await msg.reply('Данные о пользователе были успешно обновлены')
    return None


@router_admin.message(RequestData.words)
async def delete_word(msg: Message, bot: Bot, state: FSMContext):
    
    result = await autorisation(bot, msg=msg, need=LEVELS["data"])  # Авторизация пользователя
    if not result:
        return None
    
    if last_massage[msg.from_user.id] != ("data", "words"):
        await state.clear()
        await free_handler(msg, bot)
        return None
    
    word = msg.text
    result = deleting(word)
    await log(msg, ('Команда /data - words:', result + ": " + msg), bot)
    await msg.reply(result)
    return None