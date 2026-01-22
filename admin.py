from aiogram import F, Router, Bot
# Работа с сообщениями
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandObject
# Работа кнопками
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
# Работа с FSM
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from scripts.Logs import autorisation, can_read_logs
from scripts.UsersBase import get_user_list, find_user, update_user
from scripts.Verbs import write_verbs
from scripts.Lolgen.Lolgen import deleting
from config import LEVELS


router_admin = Router()  # Обработчик команд для админов


class RequestAdmin(StatesGroup):  # Сбор информации для редактирования таблицы
    chat = State()
    verbs = State()
    id = State()
    user = State()
    words = State()


@router_admin.message(Command("admin"))
async def admin(msg: Message, bot: Bot):  # Получить уровень доступа
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    await msg.reply(f"Вы обладаете правами доступа уровня {user.access}")
    await user.log(f"Command /admin: пользователь обладает правами доступа уровня {user.access}")


@router_admin.message(Command("users"))
async def user_list(msg: Message, bot: Bot):  # Получить список пользователей
    user = await autorisation(info=msg, bot=bot, need=LEVELS["users"])  # Авторизация пользователя
    if not user:
        return None
    
    text = []
    for line in sorted(get_user_list(), key=lambda user: user.access, reverse=True):
        text.append(f"{' ~~~ '.join(line.get_info())} ~~~ {line.access}" + (f" ~~~ {line.ban}" if line.ban else ''))
    await msg.reply('\n'.join(text))
    await user.log("Command /users: получена информация о пользователях")


@router_admin.message(Command("chat"))
async def admin_chat(msg: Message, command: CommandObject, bot: Bot, state: FSMContext):  # Написать другому пользователю
    user = await autorisation(info=msg, bot=bot, need=LEVELS["chat"])  # Авторизация пользователя
    if not user:
        return None

    if "chat" in (await state.get_data()).keys():  # Если пользователь уже начал отправку сообщений
        await state.clear()
        await msg.reply("Сообщения больше не отправляются")
        await user.log("Command /chat: пользователь закончил чат") 
        return None
    if not command.args:  # Если пользователь не передал никакой информации
        await msg.reply(f"Нужно указать информацию о пользователе, например\n/chat {user.username}")
        await user.log("Command /chat: нет информации о пользователе")
        return None
    
    wanted = find_user(info=command.args)  # Пробуем найти пользователя по запросу
    if not wanted:
        await msg.reply("Такого пользователя не существует")
        await user.log("Command /chat: искомый пользователь не существует:", command.args)
        return None    
    
    await state.set_state(RequestAdmin.chat)
    await state.update_data(chat=wanted)
    await msg.reply(f'Пользователь {" ~~~ ".join(wanted.get_info())} найден. Напишите сообщение')
    await user.log("Command /chat - пользователь начал чат с другим пользователем:", " ~~~ ".join(wanted.get_info()))


@router_admin.message(RequestAdmin.chat)
async def chat_fsm(msg: Message, bot: Bot, state: FSMContext):  # Чат с другим пользователем
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    try:
        wanted = (await state.get_data())["chat"]
        await bot.send_message(wanted.id, msg.text)
        await msg.reply("Сообщение успешно отправлено")
        await user.log("FSM /chat: пользователь написал другому пользователю:", msg.text)
    except Exception:  # Возможно, символы "<" и ">" мешают отправке
        try:
            await bot.send_message(wanted.id, msg.text.replace('<', '').replace('>', ''))
            await msg.reply("Сообщение успешно отправлено без запрещённых знаков")
            await user.log("FSM /chat: пользователь написал другому пользователю без знаков \"<\" и \">\":", msg.text)
        except Exception as e:  # Отправка невозможна
            await msg.reply("Сообщение не отправилось")
            await user.log(text=("FSM /chat: пользователь не смог написать пользователю:", msg.text, *repr(e).split("\n")), folder="errors")


@router_admin.message(Command("logs"))
async def admin_logs(msg: Message, command: CommandObject, bot: Bot):  # Получить логи
    user = await autorisation(info=msg, bot=bot, need=LEVELS["logs"])  # Авторизация пользователя
    if not user:
        return None
    
    args = command.args
    if not args:  # Если command.args изначально пусто, то делаем вид, будто там были "daily_logs"
        args = "daily_logs"
    
    args = args.split()
    if len(args) == 1:  # Такая длина означает только просмотр daily_logs без даты
        if "daily" not in args[0]:
            await msg.reply("Некорректные аргументы")
            await user.log("Command /logs: пользователь ввёл некорректные аргументы:", command.args)
            return None
        else:
            args[0] = "daily_logs"
            args.append(False)  # False означает, что этот элемент нужно будет заменить текущей датой
    
    elif len(args) == 2:  # Такая длина означает либо daily_logs с датой, либо логи пользователя без даты
        if args[0] in ("logs", "errors"):  # Сюда потом добавлять уровни логирования
            wanted = find_user(args[1])
            if not wanted:
                await msg.reply("Такого пользователя не существует")
                await user.log("Command /logs: искомого пользователя не существует:", command.args)
                return None
            args[1] = str(wanted.id)
            args.append(False)
        elif "daily" not in args[0]:
            await msg.reply("Некорректные аргументы")
            await user.log("Command /logs: пользователь ввёл некорректные аргументы:", command.args)
            return None
        else:
            args[0] = "daily_logs"
    
    elif len(args) == 3:  # Такая длина означает только логи пользователя с датой
        if args[0] not in ("logs", "errors"):  # Сюда потом добавлять уровни логирования
            await msg.reply("Некорректные аргументы")
            await user.log("Command /logs: пользователь ввёл некорректные аргументы:", command.args)
            return None
        wanted = find_user(args[1])
        if not wanted:
            await msg.reply("Такого пользователя не существует")
            await user.log("Command /logs: искомого пользователя не существует:", command.args)
            return None
        args[1] = str(wanted.id)
    
    file_path = can_read_logs(args)
    if not file_path:  # Такого файла не существует
        await msg.reply("Такого файла не существует")
        await user.log("Command /logs: такого файла не существует", f"{command.args} ~ {'/'.join(args)}")
    else:
        await msg.reply_document(FSInputFile(file_path), caption="Файл найден")
        await user.log(f"Command /logs: файл {file_path} найден")


@router_admin.message(Command("ban"))
async def admin_ban(msg: Message, command: CommandObject, bot: Bot):  # Забанить кого-то
    user = await autorisation(info=msg, bot=bot, need=LEVELS["data"])  # Авторизация пользователя
    if not user:
        return None
    
    if not command.args:
        await msg.reply(f"Некорректно введена команда")
        await user.log("Command /ban: пользователь не передал аргументов")
        return None
    args = command.args.split(' ')
    wanted = find_user(args[0])

    if not wanted:
        await msg.reply(f"Такого пользователя не существует")
        await user.log("Command /ban: искомый пользователь не существует:", command.args)
        return None
    
    try:
        if len(args) == 1:
            update_user(id = wanted.id, changes={"access": 0})
        else:
            update_user(id = wanted.id, changes={"access": 0, "ban": " ".join(args[1:])})
    except Exception as e:
        await msg.reply("Что-то пошло не так")
        await user.log(text=("Command /ban: что-то пошло не так", msg.text, *repr(e).split("\n")), folder="errors")
        return None
    
    text = f"Пользователь @{wanted.username} был заблокирован"
    if args[1:]:
        text += " по причине:\n" + ' '.join(args[1:])
    await msg.reply(text)
    await user.log("Command /ban:", *text.split('\n'))


@router_admin.message(Command("data"))
async def data(msg: Message, bot: Bot):  # Редактировать файлы
    user = await autorisation(info=msg, bot=bot, need=LEVELS["data"])  # Авторизация пользователя
    if not user:
        return None
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Неправильные глаголы", callback_data="change_verbs")
    builder.button(text="Пользователи", callback_data="change_users")
    builder.button(text="Слова для lolgen", callback_data="change_words")
    builder.adjust(1, 1, 1)

    await msg.reply("Что нужно редактировать?", reply_markup=builder.as_markup())
    await user.log("Command /data: начало работы")


@router_admin.callback_query(F.data.startswith("change_"))
async def data_callback(callback: CallbackQuery, bot: Bot, state: FSMContext):  # Обработка кнопок /data
    user = await autorisation(info=callback, bot=bot, need=LEVELS["data"])  # Авторизация пользователя
    if not user:
        return None
    
    # Как реагировать на запрос пользователя
    to_do = {
        "change_verbs": ("Введите слова, которые нужно добавить", RequestAdmin.verbs),
        "change_users": ("Введите id или username пользователя", RequestAdmin.id),
        "change_words": ("Введите слово, которое хотите удалить", RequestAdmin.words)
    }

    await state.set_state(to_do[callback.data][1])
    await callback.message.answer(to_do[callback.data][0])
    await callback.answer()
    await user.log(f"Callback /data: выбран вариант {callback.data}")


@router_admin.message(RequestAdmin.verbs)
async def get_verbs(msg: Message, bot: Bot, state: FSMContext):  # Добавление неправильных глаголы
    user = await autorisation(info=msg, bot=bot, need=LEVELS["data"])  # Авторизация пользователя
    if not user:
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
    except Exception as e:
        await msg.reply("Что-то пошло не так")
        await user.log(text=("FSM /data.verbs: произошла ошибка:", *repr(e).split("\n"), "Запрос: " + msg.text), folder="errors")
        return None
    
    await state.clear()
    await msg.reply("Глаголы были успешно добавлены")
    await user.log("FSM /data.verbs: слова были успешно добавлены в таблицу", "Запрос: " + msg.text)


@router_admin.message(RequestAdmin.id)
async def get_id(msg: Message, bot: Bot, state: FSMContext):  # Получение id пользователя, информацию о котором мы хотим изменить
    user = await autorisation(info=msg, bot=bot, need=LEVELS["data"])  # Авторизация пользователя
    if not user:
        return None
    
    wanted = find_user(info=msg.text)
    if not wanted:
        await msg.reply("Некорректно введена информация о пользователе")
        await user.log("FSM /data.id: пользователь некорректно ввёл информацию о пользователе", "Запрос: " + msg.text)
        return None
    
    await state.update_data(id=wanted.id)
    await state.set_state(RequestAdmin.user)
    await msg.reply("Пользователь " + " ~~~ ".join(wanted.get_info()) +
                    " найден.\nВведите изменения: доступны колонки \"id\", \"username\", \"access\", \"ban\"")
    await user.log("FSM /data.id: искомый пользователь найден:", " ~~~ ".join(wanted.get_info()))


@router_admin.message(RequestAdmin.user)
async def get_user(msg: Message, bot: Bot, state: FSMContext):  # Получение информации для изменения информации о пользователе
    user = await autorisation(info=msg, bot=bot, need=LEVELS["data"])  # Авторизация пользователя
    if not user:
        return None
    
    changes = {}
    for column in msg.text.split('\n'):
        key, value = column.split(": ")
        if key in ("id", "username", "access", "ban"):
            changes[key] = value
    id = (await state.get_data())["id"]
    try:
        update_user(id=id, changes=changes)
    except Exception as e:
        await msg.reply("Что-то пошло не так")
        await user.log(text=("FSM /data.user: произошла ошибка:", *repr(e).split("\n"), "Запрос: " + msg.text), folder="errors")
        return None
    
    await state.clear()
    await msg.reply("Данные о пользователе были успешно обновлены")
    await user.log("FSM /data.user: информация о пользователе была изменена, запрос:", *msg.text.split('\n'))


@router_admin.message(RequestAdmin.words)
async def delete_word(msg: Message, bot: Bot, state: FSMContext):  # Удаление слов из БД lolgen
    user = await autorisation(info=msg, bot=bot, need=LEVELS["data"])  # Авторизация пользователя
    if not user:
        return None
    
    words = msg.text.lower().split(' ')
    for word in words:
        result = deleting(word)
        await msg.reply(result)
        await user.log(f"FSM /data.words:", result)
    await state.clear()