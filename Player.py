from PictureDescriber import PictureDescriber
from Generator import PictureGenerator

class Player:
    def __init__(self):
        self.generator = PictureGenerator()
        self.describer = PictureDescriber()

    def draw_pictures(self, prompt):
        pictures = self.generator.generate_pictures(prompt) # пока только один промпт и 1 картинка в генерации
        return pictures[0]

    def describe(self, images):
        return self.describer.describe(images)


def test_drawing(client, prompt):
    res = client.draw_pictures(prompt)
    # в res 1 картинка
    res.save(f"{prompt}.jpg")


player = Player()
test_drawing(player, "cat in <cute-game-style>")

