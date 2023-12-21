from aiogram import Bot, types
from aiogram.utils import executor
from PIL import Image

botInternal = None


async def send_plain_text(user, message):
    await botInternal.send_message(user, message)


async def send_photo_with_text(user, img_path, message):
    await botInternal.send_photo(photo=open(img_path, 'rb'), caption=message, chat_id=user)


async def send_gif_with_text(user, img_path, message):
    await botInternal.send_animation(animation=open(img_path, 'rb'), caption=message, chat_id=user)


async def get_profile_photo(user_id, destiny):
    if user_id == 0:
        return Image.open('resources/missing.png')
    photos = await botInternal.get_user_profile_photos(user_id)
    if photos.total_count == 0:
        image = Image.open('resources/missing.png')
        return image
    else:
        file_id = photos.photos[0][-1].file_id
        await botInternal.download_file_by_id(file_id = file_id, destination=destiny)
        image = Image.open(destiny)
        return image


def init_bot(bot_in):
    global botInternal
    botInternal = bot_in
