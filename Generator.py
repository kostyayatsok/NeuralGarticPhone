import torch
from transformers import CLIPFeatureExtractor, CLIPTextModel, CLIPTokenizer
from diffusers import AutoencoderKL, UNet2DConditionModel, PNDMScheduler
from diffusers import LMSDiscreteScheduler
import copy
from tqdm.auto import tqdm
from torch import autocast
from PIL import Image
from diffusers import StableDiffusionPipeline
from diffusers import StableDiffusionPipeline


sdpath = "stabilityai/stable-diffusion-2"


class PictureGenerator:
    inited = False
    pipe = None
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu", steps=25, guidance_scale=7.5, path="sd-concepts-library/gphone01"):
        if not PictureGenerator.inited:
          PictureGenerator.pipe = StableDiffusionPipeline.from_pretrained(sdpath, torch_dtype=torch.float16).to(device)
          PictureGenerator.pipe.load_textual_inversion(path)
          inited = True
        self.device = device
        self.steps = steps
        self.scale = guidance_scale

    def generate_pictures(self, prompt):
        images = self.pipe(prompt, num_images_per_prompt=1, num_inference_steps=self.steps, guidance_scale=self.scale).images
        return images
