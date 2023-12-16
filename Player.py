from TextEncoder import TextEncoder
from Generator import PictureGenerator

class Player:
    def __init__(self, ):
        self.encoder = TextEncoder()
        self.generator = PictureGenerator()

    def draw_pictures(self, prompt: list[str] | str):
        if type(prompt) != list:
            prompt = [prompt]
        text_embeddings = self.encoder.encode(prompt)
        pictures = self.generator.generate_pictures(text_embeddings)
        return pictures
