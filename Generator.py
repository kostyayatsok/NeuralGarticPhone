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

    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu", steps=25, guidance_scale=7.5, path="sd-concepts-library/cute-game-style-2-1"):
        self.device = device
        self.steps = steps
        self.scale = guidance_scale
        self.pipe = StableDiffusionPipeline.from_pretrained(sdpath, torch_dtype=torch.float16).to(device)
        self.pipe.load_textual_inversion(path)

    def generate_pictures(self, prompt):
        images = self.pipe(prompt, num_images_per_prompt=1, num_inference_steps=self.steps, guidance_scale=self.scale).images
        return images
