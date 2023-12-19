import copy
class Player:
    def __init__(self):
        self.generator = PictureGenerator()
        self.describer = PictureDescriber()

    def draw_pictures(self, prompt):
        pictures = self.generator.generate_pictures(prompt) # пока только один промпт и 1 картинка в генерации
        return pictures

    def describe(self, images):
        return self.describer.describe(images)


def test_drawing(client, prompt : list):
    initial = copy.copy(prompt)
    for j in range(len(prompt)):
      prompt[j] += " drawing in <gp> style with white background"
    print(prompt)
    res = client.draw_pictures(prompt)
    # в res 1 картинка
    for i in range(len(res)):
        res[i].save(f"{initial[i]}.jpg")


# player = Player()
# test_drawing(player, ["cat", "dog", "bulldog"])
