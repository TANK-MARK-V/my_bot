from aiogram import F, Router, Bot
# Работа с сообщениями
from aiogram.types import Message
from aiogram.filters import Command, CommandStart, CommandObject
# Работа кнопками
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
# Работа с FSM
from aiogram.fsm.context import FSMContext


from scripts.Logs import autorisation
from config import COMMANDS, SHORTS, LEVELS


base_router = Router()  # Обработчик стандартных команд


@base_router.message(CommandStart())
async def start_handler(msg: Message, bot: Bot):  # Начало работы бота
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    await msg.answer("Привет-привет! Если ты решил затестить новую команду, то, скорее всего, " +
                     "она есть в списке в левом нижнем углу (там где три полосочки нарисованы).\n" +

                     "Если тебе нужен полный перечень команд, используй /info.\n" +

                     "По любым вопросам обращайся к @markusha_v3. Приятного пользования:)")
    await user.log("Command /start")


@base_router.message(Command("cancel"))
@base_router.message(Command("stop"))
async def stop(msg: Message, bot: Bot, state: FSMContext):  # Отмена всех команд
    user = await autorisation(info=msg, bot=bot)  # Авторизация пользователя
    if not user:
        return None

    await state.clear()
    await user.log("Command /cancel")


@base_router.message(Command("info"))
async def information(msg: Message, command: CommandObject, bot: Bot):  # Получить подробную информацию о командах
    need = LEVELS[command.args] if command.args in LEVELS.keys() else 1  # Если искомая команда имеет повышенный уровень доступа, то мы повышаем уровень авторизации
    user = await autorisation(info=msg, bot=bot, need=need)  # Авторизация пользователя
    if not user:
        return None

    if command.args and command.args in (COMMANDS["__names__"] + COMMANDS["__admin_names__"]):  # Если пользователь написал название команды после /info
        await msg.answer('\n'.join(COMMANDS[command.args]))
        await user.log(f"Command /info: {command.args}")
        return None

    builder = InlineKeyboardBuilder()  # Создаём кнопку на каждую команду
    for command in COMMANDS["__names__"] + COMMANDS["__admin_names__"]:
        if command not in LEVELS.keys() or user.access >= LEVELS[command]:
            builder.button(text=f"/{command}", callback_data=f"com_{command}")

    base, admin = 3, 2  # Обычные команды располагаем по 3 на строчке, а админские - по 2
    all_base, all_admin = len(COMMANDS["__names__"]), len(COMMANDS["__admin_names__"])
    grid = [base,] * (all_base // base) + ([all_base % base,] if all_base % base else [])
    grid += [admin,] * (all_admin // admin) + ([all_admin % admin,] if all_admin % admin else [])
    builder.adjust(*grid)

    await msg.reply("Список команд:\n" + SHORTS)
    await msg.answer("Выберете нужную команду, чтобы получить подробную информацию:", reply_markup=builder.as_markup())
    await user.log("Command /info")


@base_router.callback_query(F.data.startswith("com_"))
async def information_callback(callback: CallbackQuery, bot: Bot):  # Обработка кнопок /info
    asked = callback.data.replace("com_", "")  # Какую команду выбрал пользователь
    need = LEVELS[asked] if asked in LEVELS.keys() else 1  # Если искомая команда имеет повышенный уровень доступа, то мы повышаем уровень авторизации
    user = await autorisation(info=callback, bot=bot, need=need)  # Авторизация пользователя
    if not user:
        await callback.answer()
        return None
    
    await callback.message.answer('\n'.join(COMMANDS[asked]))
    await callback.answer()
    await user.log(f"Callback /info: выбран вариант {callback.data}")