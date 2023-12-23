from transformers import AutoProcessor, AutoModelForCausalLM

import requests
import torch
from PIL import Image

class PictureDescriber:
    inited = False
    model = None
    feature_extractor = None
    tokenizer = None
    def __init__(self):
        if not PictureDescriber.inited:
          inited = True
          PictureDescriber.device="cuda" if torch.cuda.is_available() else "cpu"
          PictureDescriber.processor = AutoProcessor.from_pretrained("microsoft/git-base-coco")
          PictureDescriber.model = AutoModelForCausalLM.from_pretrained("microsoft/git-base-coco")
          PictureDescriber.model = PictureDescriber.model.to(PictureDescriber.device)

    def __describe_one(self, image):
        pixel_values = PictureDescriber.processor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(PictureDescriber.device)
        generated_ids = PictureDescriber.model.generate(pixel_values=pixel_values, max_length=50)
        generated_caption = PictureDescriber.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_caption
    def describe(self, i_images):
        images = [i.convert(mode="RGB") for i in i_images]
        res = []
        for i in images:
            res.append(self.__describe_one(i))
        return res


# desc = PictureDescriber()
# with Image.open("cat.jpg") as img:
#     res = desc.describe(img)
#     print(res)
# ['a gray and white cat is looking at the camera']


