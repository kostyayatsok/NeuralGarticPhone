from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import BotAPI
import CommandResolver
import asyncio
import RoomMaster

# Инитаем бота
BOT_TOKEN = '6407292093:AAGhgQyUL40aexE9VuXmyc4tjWCK9RrCZxQ'
botik = Bot(token=BOT_TOKEN)
disp = Dispatcher(botik)
BotAPI.init_bot(botik)


async def join_command_internal(message: types.Message | types.CallbackQuery):
    if isinstance(message, types.Message):
        await CommandResolver.join_command(message.from_user, message.text.replace('/join ', '', 1))
    elif isinstance(message, types.CallbackQuery):
        text = message.message.reply_markup.inline_keyboard[0][0].text
        room_id = text.split()[2]
        await CommandResolver.join_command(message.from_user, room_id)


@disp.message_handler(chat_type=[types.ChatType.GROUP, types.ChatType.CHANNEL], commands=['create'])
async def create_chat_callback(message: types.Message):
    room_id = await CommandResolver.create_command(message.from_user.id, message.chat.id, in_chat=True)
    if room_id == '':
        return
    inline_btn_1 = InlineKeyboardButton('Присоединиться к '+room_id, callback_data='button1')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
    await CommandResolver.join_command(message.from_user, message.chat.id, is_admin=True)
    await botik.send_message(message.chat.id, 'Играть:', reply_markup=inline_kb1)


@disp.callback_query_handler(text='button1')
async def join_inline_callback(call: types.CallbackQuery):
    await join_command_internal(call)


@disp.callback_query_handler(text='button21')
async def join_inline_callback(call: types.CallbackQuery):
    await CommandResolver.gamemode_command(call.from_user, 0)


@disp.callback_query_handler(text='button22')
async def join_inline_callback(call: types.CallbackQuery):
    await CommandResolver.gamemode_command(call.from_user, 1)


@disp.callback_query_handler(text='button23')
async def join_inline_callback(call: types.CallbackQuery):
    await CommandResolver.gamemode_command(call.from_user, 2)


@disp.message_handler(commands=['create'])
async def create_command_callback(message: types.Message):
    room_id = await CommandResolver.create_command(message.from_user.id)
    if room_id == '':
        return
    inline_btn_1 = InlineKeyboardButton('Присоединиться к '+room_id, callback_data='button1')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
    await CommandResolver.join_command(message.from_user, room_id, is_admin=True)
    await botik.send_message(message.from_user.id, 'Играть:', reply_markup=inline_kb1)


@disp.message_handler(commands=['join'])
async def join_command_callback(message: types.Message):
    await join_command_internal(message)


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


@disp.message_handler(commands=['gamemode'])
async def gamemode_command_callback(message: types.Message):
    inline_btn_1 = InlineKeyboardButton('Нейро-игрок', callback_data='button21')
    inline_btn_2 = InlineKeyboardButton('Нейро-художник', callback_data='button22')
    inline_btn_3 = InlineKeyboardButton('Нейро-зритель', callback_data='button23')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2, inline_btn_3)
    await botik.send_message(message.from_user.id, 'Режимы: ', reply_markup=inline_kb1)


@disp.message_handler(commands=['help'])
async def start_command_callback(message: types.Message):
    result = ''
    result += '/help - помощь \n'
    result += '/create - создать комнату \n'
    result += '/list - список игроков \n'
    result += '/time - изменить лимит по времени на раунд \n'
    result += '/quality - изменить качество генерации картинок'
    result += '/join - войти в комнату \n'
    result += '/leave - покинуть комнату \n'
    result += '/start - начать игру \n'
    result += '/stop - остановить игру \n'
    result += '/history - вывести альбомы \n'
    await BotAPI.send_plain_text('0', message.from_user.id, result)


@disp.message_handler()
async def empty_command_callback(message: types.Message):
    await CommandResolver.apply_text(message.from_user, message.text)


@disp.message_handler(content_types=[types.ContentType.PHOTO])
async def empty_photo_callback(message: types.Message):
    file_id = message.photo[0].file_id
    await CommandResolver.apply_photo(message.from_user, file_id)


# Нам нужно, чтобы во время работы таймера бот не уходил в АФК
# Поэтому мы добавим таск в asyncio на глобальный апдейт с периодичностью 500 мс
async def on_startup_launch(dispatcher):
    asyncio.create_task(RoomMaster.global_update())


executor.start_polling(disp, skip_updates=True, on_startup=on_startup_launch)
