from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import BotAPI
import textwrap


class Album:

    def __init__(self, player_map):
        self.player_map = player_map

    def make_gif(self, image_list, text_list, player_list):
        return

    def make_image_page(self, numer, count, image_path, user_id):
        background = Image.open('resources/alubum_background_1.png').convert('RGBA')
        user_image = Image.open(image_path).convert('RGBA')

        width_back, height_back = background.width, background.height
        width_user, height_user = user_image.width, user_image.height
        width_paste1, height_paste2 = width_back * 19 // 20, height_back * 31 // 40

        box2 = (width_back // 40, height_back // 10)
        user_image = user_image.resize((width_paste1, height_paste2))
        print(background, user_image)
        background.paste(user_image, box2)

        self.assemble_page(background, numer, count, user_id)
        background.show()

    def make_text_page(self, numer, count, text, user_id):
        background = Image.open('resources/alubum_background_2.png').convert('RGBA')

        width_back, height_back = background.width, background.height
        width_rect, height_rect = width_back * 7 // 10, height_back * 7 // 10
        rect_x, rect_y = width_back // 7, height_back // 7
        lines = textwrap.wrap(text, width_rect)
        print(lines)

        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype('resources/arial.ttf', size=(width_back // 20))
        for line in lines:
            print('ff')

        self.assemble_page(background, numer, count, user_id)
        background.show()

    def assemble_page(self, image, numer, count, user_id):
        width, height = image.width, image.height
        gap_width, gap_height = width // 100, height // 50
        rect_width = ((width - gap_width) / count) - gap_width
        avatar_size = min(width, height) // 7
        avatar_x, avatar_y = width * 35 // 40, height * 8 // 10
        current_x, current_y = gap_width, height - 2 * gap_height
        draw = ImageDraw.Draw(image)
        username = 'vlad2509' #self.player_map[user_id].username

        for i in range(count):
            if i <= numer:
                color = (255, 255, 255)
            else:
                color = (127, 127, 127)
            draw.rectangle((current_x, current_y, current_x + rect_width, current_y + gap_height), fill=color)
            current_x += rect_width + gap_width

        font = ImageFont.truetype('resources/arial.ttf', size=(width // 20))
        text_width, text_height = font.getsize(username)
        text_x, text_y = avatar_x - text_width - width // 15, avatar_y - text_height + height * 2 // 15
        draw.text((text_x, text_y), 'Hello World', font=font, fill=(40, 150, 255), stroke_width=2,
                  stroke_fill="blue")

        avatar = BotAPI.get_profile_photo(user_id).resize((avatar_size, avatar_size))
        mask = (Image.open('resources/mask.png').convert('L').resize((avatar_size, avatar_size)))
        image.paste(avatar, (avatar_x, avatar_y), mask)


