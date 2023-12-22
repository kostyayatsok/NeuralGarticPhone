from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from GameUtils import PlayerTG
import BotAPI
import textwrap


class Album:

    def __init__(self, player_map, room_id):
        self.player_map = player_map
        self.history = []
        self.room_id = room_id
        self.page = 0

    def make_gif(self, gif_path, duration):
        self.history[0].save(gif_path,
                             save_all=True, append_images=self.history[1:],
                             optimize=True, duration=duration, loop=0)

    async def add_image_page(self, count, image_path, user_id):
        if image_path == '':
            image_path = 'resources/emptyImage.jpg'

        background = Image.open('resources/alubum_background_1.png').convert('RGB')
        user_image = Image.open(image_path).convert('RGB')

        width_back, height_back = background.width, background.height
        width_user, height_user = user_image.width, user_image.height
        width_paste1, height_paste2 = width_back * 19 // 20, height_back * 31 // 40

        box2 = (width_back // 40, height_back // 10)
        user_image = user_image.resize((width_paste1, height_paste2))
        background.paste(user_image, box2)

        await self.assemble_page(background, count, user_id)
        self.history.append(background)
        print('gen image')
        #background.show()

    async def add_text_page(self, count, text, user_id):
        background = Image.open('resources/alubum_background_2.png').convert('RGB')

        width_back, height_back = background.width, background.height
        width_rect, height_rect = width_back * 7 // 10, height_back * 7 // 10
        rect_x, rect_y = width_back // 7, height_back // 7
        lines = textwrap.wrap(text, (width_back // 27))

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype('resources/arial.ttf', size=(width_back // 20))
        text_height = font.getsize('AA')[1] + 5
        for i in range(len(lines)):
            line = lines[i]
            text_width = font.getsize(line)[0]
            text_y = height_back // 2 - text_height * len(lines) // 2
            line_x = width_back // 2 - text_width // 2
            line_y = text_y + i * text_height
            draw.text((line_x, line_y), line, font=font, fill=(200, 50, 200), stroke_width=1,
                      stroke_fill=(200, 50, 200))

        await self.assemble_page(background, count, user_id)
        print('gen text')
        self.history.append(background)
        #background.show()

    async def assemble_page(self, image, count, user_id):
        width, height = image.width, image.height
        gap_width, gap_height = width // 100, height // 50
        rect_width = ((width - gap_width) / count) - gap_width
        avatar_size = min(width, height) // 7
        avatar_x, avatar_y = width * 35 // 40, height * 8 // 10
        current_x, current_y = gap_width, height - 2 * gap_height
        draw = ImageDraw.Draw(image)
        username = self.player_map[user_id].username
        numer = self.page
        self.page += 1

        for i in range(count):
            if i <= numer:
                color = (255, 255, 255)
            else:
                color = (127, 127, 127)
            draw.rectangle((current_x, current_y, current_x + rect_width, current_y + gap_height), fill=color)
            current_x += rect_width + gap_width

        font = ImageFont.truetype('resources/arial.ttf', size=(width // 20))
        text_width, text_height = font.getsize(username)
        text_x, text_y = avatar_x - text_width * 11 // 10, avatar_y + text_height
        draw.text((text_x, text_y), username, font=font, fill=(40, 150, 255), stroke_width=2,
                  stroke_fill="blue")

        avatar_path = self.room_id + '/' + str(user_id) + '.png'
        avatar = await BotAPI.get_profile_photo(user_id, avatar_path)
        avatar = avatar.resize((avatar_size, avatar_size))
        mask = (Image.open('resources/mask.png').convert('L').resize((avatar_size, avatar_size)))
        image.paste(avatar, (avatar_x, avatar_y), mask)
