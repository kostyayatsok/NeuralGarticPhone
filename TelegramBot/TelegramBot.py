from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
import BotAPI
import CommandResolver
import asyncio
import RoomMaster

# TODO: потокобезопасность
# TODO: настройки комнаты
# TODO: локализация?
# TODO: и т.п.


# Инитаем бота
BOT_TOKEN = 'Вставьте свой токен'
botik = Bot(token=BOT_TOKEN)
disp = Dispatcher(botik)
BotAPI.init_bot(botik)


@disp.message_handler(commands=['create_room'])
async def create_command_callback(message: types.Message):
    await CommandResolver.create_command(message.from_user)


@disp.message_handler(commands=['join'])
async def join_command_callback(message: types.Message):
    await CommandResolver.join_command(message.from_user, message.text.replace('/join ', '', 1))


@disp.message_handler(commands=['leave'])
async def leave_command_callback(message: types.Message):
    await CommandResolver.leave_command(message.from_user)


@disp.message_handler(commands=['start'])
async def start_command_callback(message: types.Message):
    await CommandResolver.start_command(message.from_user)


@disp.message_handler(commands=['stop'])
async def stop_command_callback(message: types.Message):
    await CommandResolver.stop_command(message.from_user)


@disp.message_handler(commands=['history'])
async def history_command_callback(message: types.Message):
    await CommandResolver.history_command(message.from_user)


@disp.message_handler(commands=['list'])
async def list_command_callback(message: types.Message):
    await CommandResolver.list_command(message.from_user)


@disp.message_handler(commands=['time'])
async def time_command_callback(message: types.Message):
    await CommandResolver.time_command(message.from_user, message.text.replace('/time ', '', 1))


@disp.message_handler()
async def empty_command_callback(message: types.Message):
    await CommandResolver.apply_command(message.from_user, message.text)


@disp.message_handler(commands=['help'])
async def start_command_callback(message: types.Message):
    result = ''
    result += '/help - помощь \n'
    result += '/create_room - создать комнату \n'
    result += '/list - список игроков \n'
    result += '/join - войти в комнату \n'
    result += '/leave - покинуть комнату \n'
    result += '/start - начать игру \n'
    result += '/stop - остановить игру \n'
    result += '/history - вывести альбомы \n'
    result += '/aply - ввести текст/подпись к картинке \n'
    await BotAPI.send_plain_text(message.from_user.id, result)


# Нам нужно, чтобы во время работы таймера бот не уходил в АФК
# Поэтому мы добавим таск в asyncio на глобальный апдейт с периодичностью 500 мс
async def on_startup_launch(dispatcher):
    asyncio.create_task(RoomMaster.global_update())


executor.start_polling(disp, skip_updates=True, on_startup=on_startup_launch)