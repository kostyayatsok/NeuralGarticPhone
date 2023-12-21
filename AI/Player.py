import copy
from PictureDescriber import PictureDescriber
from Generator import PictureGenerator
from PIL import Image
from AI.Translator import Translator


class Player:
    def __init__(self):
        self.translator = Translator("config2.ini")
        self.generator = PictureGenerator(steps=25)
        self.describer = PictureDescriber()

    def draw_pictures(self, prompt):
        prompt = self.translator.translate(prompt, "en")
        for j in range(len(prompt)):
            prompt[j] = (
                "drawing of a "
                + prompt[j]
                + " in the style of <gp> on white background"
            )
        pictures = self.generator.generate_pictures(prompt)
        return pictures

    def describe(self, images):
        return self.translator.translate(
            self.describer.describe(images), target_lang="ru"
        )


def image_grid(imgs, rows, cols):
    assert len(imgs) == rows * cols

    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))
    grid_w, grid_h = grid.size

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid


def test_drawing(client, prompt: list):
    initial = copy.copy(prompt)
    res = client.draw_pictures(prompt)
    grid = image_grid(res, 1, len(res))
    for i in range(len(res)):
        res[i].save(f"{initial[i]}.jpg")
    grid.save("all.jpg")


player = Player()
test_drawing(player, ["кот", "собака"])
