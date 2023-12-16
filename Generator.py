import torch
from diffusers import AutoencoderKL, UNet2DConditionModel, PNDMScheduler
from diffusers import LMSDiscreteScheduler
import copy


class PictureGenerator:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu", batch_size=1, height=512, width=512, num_inference_steps=20, seed=None):
        self.vae = AutoencoderKL.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="vae")
        self.unet = UNet2DConditionModel.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="unet")
        self.device = device
        self.vae = self.vae.to(self.device)
        self.unet = self.unet.to(self.device)
        self.scheduler = LMSDiscreteScheduler.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="scheduler")
        self.height = height
        self.width = width
        self.steps = num_inference_steps

        if seed is not None:
            self.gen = torch.manual_seed(seed)
        else:
            self.gen = torch.Generator()
        self.gen = self.gen.to(device)

    def set_height(self, height):
        self.height = height

    def set_width(self, width):
        self.width = width

    def __generate_latents(self, text_embeddings):
        pass
    def __decode(self, latents):
        pass
    def generate_pictures(self, text_embeddings):
        latents = self.__generate_latents(text_embeddings)
        return self.__decode(latents)
