from aiogram import Bot, types
from aiogram.utils import executor
from PIL import Image

botInternal = None


async def send_plain_text(user, message):
    await botInternal.send_message(user, message)


async def send_photo_with_text(user, img_path, message):
    await botInternal.send_photo(photo=open(img_path, 'rb'), caption=message, chat_id=user)


def get_profile_photo(user_id):
    image = Image.open('resources/missing.png').convert('RGBA')
    return image

    #photos = await botInternal.get_user_profile_photos(user_id)
    #if photos.total_count == 0:
        #image = Image.open('resources/missing.png')
        #return image
    #else:
        #file_id = photos.photos[0]
        #return


def init_bot(bot_in):
    global botInternal
    botInternal = bot_in
