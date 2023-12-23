from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from PIL import Image


class PictureDescriber:
    inited = False
    model = None
    feature_extractor = None
    tokenizer = None
    device = None
    def __init__(self):
        if not PictureDescriber.inited:
          inited = True
          PictureDescriber.device = "cuda" if torch.cuda.is_available() else "cpu"
          PictureDescriber.model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
          PictureDescriber.model = PictureDescriber.model.to(PictureDescriber.device)
          PictureDescriber.tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
          PictureDescriber.feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        self.max_length = 16
        self.num_beams = 4
        self.gen_kwargs = {"max_length": self.max_length, "num_beams": self.num_beams}

    def describe(self, i_images):
        images = [i.convert(mode="RGB") for i in i_images]

        pixel_values = self.feature_extractor(images=images, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(PictureDescriber.device)
        output_ids = self.model.generate(pixel_values, **self.gen_kwargs)
        preds = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        preds = [pred.strip() for pred in preds]
        return preds


# desc = PictureDescriber()
# with Image.open("cat.jpg") as img:
#     res = desc.describe([img])
#     print(res)
# ['a gray and white cat is looking at the camera']


