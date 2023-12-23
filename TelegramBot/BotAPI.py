from aiogram import Bot, types
from aiogram.utils import executor
from PIL import Image

botInternal = None
message_pool = {}


async def delete_messages(room_id):
    for message in message_pool[room_id]:
        await message.delete()


async def send_plain_text(room_id, user, message):
    if user >= 100000000000:
        return
    try:
        message = await botInternal.send_message(user, message)
        if room_id not in message_pool.keys():
            message_pool[room_id] = []
        message_pool[room_id].append(message)
    except BaseException:
        return -1
    return 0


async def send_photo_with_text(room_id, user, img_path, message):
    if user >= 100000000000:
        return
    try:
        message = await botInternal.send_photo(photo=open(img_path, 'rb'), caption=message, chat_id=user)
        if room_id not in message_pool.keys():
            message_pool[room_id] = []
        message_pool[room_id].append(message)
    except BaseException:
        return -1
    return 0


async def send_gif_with_text(room_id, user, img_path, message):
    if user >= 100000000000:
        return
    try:
        message = await botInternal.send_animation(animation=open(img_path, 'rb'), caption=message, chat_id=user)
        if room_id not in message_pool.keys():
            message_pool[room_id] = []
        message_pool[room_id].append(message)
    except BaseException:
        return -1
    return 0


async def download_image_by_id(file_id, path):
    await botInternal.download_file_by_id(file_id=file_id, destination=path)


async def get_profile_photo(user_id, destiny):
    if user_id >= 100000000000:
        return Image.open('resources/missing.png')
    try:
        photos = await botInternal.get_user_profile_photos(user_id)
        if photos.total_count == 0:
            image = Image.open('resources/missing.png')
            return image
        else:
            file_id = photos.photos[0][-1].file_id
            await botInternal.download_file_by_id(file_id=file_id, destination=destiny)
            image = Image.open(destiny)
            return image
    except Exception:
        return Image.open('resources/missing.png')


def init_bot(bot_in):
    global botInternal
    botInternal = bot_in
