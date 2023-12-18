from aiogram import Bot, types
from aiogram.utils import executor

botInternal = None


async def send_plain_text(user, message):
    await botInternal.send_message(user, message)


async def send_photo_with_text(user, img_path, message):
    await botInternal.send_photo(photo=open(img_path, 'rb'), caption=message, chat_id=user)


def init_bot(bot_in):
    global botInternal
    botInternal = bot_in
