import torch
from transformers import CLIPFeatureExtractor, CLIPTextModel, CLIPTokenizer
from diffusers import AutoencoderKL, UNet2DConditionModel, PNDMScheduler
from diffusers import LMSDiscreteScheduler
import copy
from tqdm.auto import tqdm
from torch import autocast
from PIL import Image
from diffusers import StableDiffusionPipeline
# from optimum.intel import OVStableDiffusionPipeline
import numpy as np

sdpath = "stabilityai/stable-diffusion-2"
# sdpath = "OFA-Sys/small-stable-diffusion-v0"


class PictureGenerator:
    inited = False
    pipe = None
    def __init__(
        self,
        device="cpu",
        steps=40,
        guidance_scale=7.5,
        path="sd-concepts-library/gphone03",
        # path="sd-concepts-library/gphone_small"
    ):
        if not PictureGenerator.inited:
            PictureGenerator.pipe = StableDiffusionPipeline.from_pretrained(sdpath).to(device)
            PictureGenerator.pipe.load_textual_inversion(path)
            inited = True
        self.device = device
        self.steps = steps
        self.scale = guidance_scale
    def make_bw(self, images):
        _ = []
        for x in images:
            img = np.array(x).mean(-1)
            img[img > 30] = 255
            w, h = img.shape
            res = []
            for i in range(w):
                for j in range(h):
                    res.append((int(img[i][j]), int(img[i][j]), int(img[i][j])))
            sus = Image.new('RGB', (w, h))
            sus.putdata(res)
            _.append(sus)
        return _
    def generate_pictures(self, prompt):
        images = self.pipe(
            prompt,
            # height=128,
            # width=128,
            num_images_per_prompt=1,
            num_inference_steps=self.steps,
            guidance_scale=self.scale
        ).images
        return images
