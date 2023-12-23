import torch
from transformers import CLIPFeatureExtractor, CLIPTextModel, CLIPTokenizer
from diffusers import AutoencoderKL, UNet2DConditionModel, PNDMScheduler
from diffusers import LMSDiscreteScheduler
import copy
from tqdm.auto import tqdm
from torch import autocast
from PIL import Image
from diffusers import StableDiffusionPipeline
import numpy as np
from optimum.intel import OVStableDiffusionPipeline

sdpath = "stabilityai/stable-diffusion-2"
# sdpath = "OFA-Sys/small-stable-diffusion-v0"

class PictureGenerator:
    inited = False
    pipe = None

    def __init__(
        self,
        device="cuda" if torch.cuda.is_available() else "cpu",
        steps=50,
        guidance_scale=7.5,
        # path="sd-concepts-library/gphone_small",
        path="sd-concepts-library/gphone03"
    ):
        # Define the shapes related to the inputs and desired outputs
        self.num_images_per_prompt = 1
        self.height = 256
        self.width = 256

        if not PictureGenerator.inited:
            if device == "cpu":
                PictureGenerator.pipe = OVStableDiffusionPipeline.from_pretrained(
                    sdpath, compile=False, export=True
                ).to(device)
                PictureGenerator.pipe.load_textual_inversion(path, "<gp>")
                PictureGenerator.pipe.reshape(batch_size=1, height=self.height, width=self.width, num_images_per_prompt=self.num_images_per_prompt)
                PictureGenerator.pipe.compile()
            else:
                PictureGenerator.pipe = StableDiffusionPipeline.from_pretrained(
                    sdpath
                ).to(device)
                PictureGenerator.pipe.load_textual_inversion(path)
            
            PictureGenerator.inited = True
        self.device = device
        self.steps = steps
        self.scale = guidance_scale

    def make_bw(self, images):
        _ = []
        for x in images:
            img = np.array(x).mean(-1)
            img[img > 30] = 255
            w, h = img.shape
            print(img)
            print(w, h)
            res = []
            for i in range(w):
                for j in range(h):
                    res.append((int(img[i][j]), int(img[i][j]), int(img[i][j])))
            sus = Image.new("RGB", (w, h))
            sus.putdata(res)
            _.append(sus)
        return _

    def generate_pictures(self, prompt):
        images = self.pipe(
            prompt,
            num_images_per_prompt=self.num_images_per_prompt,
            num_inference_steps=self.steps,
            guidance_scale=self.scale,
            height=self.height,
            width=self.width,
        ).images
        return images
