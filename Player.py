from TextEncoder import TextEncoder
from Generator import PictureGenerator
from PictureDescriber import PictureDescriber
from PIL import Image
class Player:
    def __init__(self, batch_size=1):
        self.batch_size = batch_size
        self.encoder = TextEncoder(batch_size=self.batch_size)
        self.generator = PictureGenerator(batch_size=self.batch_size)
        self.describer = PictureDescriber()

    def draw_pictures(self, prompt):
        if type(prompt) != list:
            prompt = [prompt]
        text_embeddings = self.encoder.encode(prompt)
        pictures = self.generator.generate_pictures(text_embeddings)
        return pictures

    def describe(self, images):
        return self.describer.describe(images)


def test_drawing(client, prompt):
    res = client.draw_pictures(prompt)
    for i in range(len(prompt)):
        res[i].save(f"{prompt[i]}.jpg")


player = Player()
test_drawing(player, ["big shark", "doghouse"])


