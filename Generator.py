import torch
from diffusers import AutoencoderKL, UNet2DConditionModel, PNDMScheduler
from diffusers import LMSDiscreteScheduler
import copy
from tqdm.auto import tqdm
from torch import autocast
from PIL import Image

class PictureGenerator:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu", batch_size=1, height=512, width=512, num_inference_steps=20, seed=None, guidance_scale=7.5):
        self.vae = AutoencoderKL.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="vae")
        self.unet = UNet2DConditionModel.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="unet")
        self.device = device
        self.batch_size = batch_size
        self.vae = self.vae.to(self.device)
        self.unet = self.unet.to(self.device)
        self.scheduler = LMSDiscreteScheduler.from_pretrained("CompVis/stable-diffusion-v1-4", subfolder="scheduler")
        self.height = height
        self.width = width
        self.steps = num_inference_steps
        self.guidance_scale = guidance_scale
        if seed is not None:
            self.gen = torch.manual_seed(seed)
        else:
            self.gen = torch.Generator()

    def set_height(self, height):
        self.height = height

    def set_width(self, width):
        self.width = width

    def __generate_latents(self, text_embeddings):
        latents = torch.randn(
          (self.batch_size, self.unet.in_channels, self.height // 8, self.width // 8),
          generator=self.gen,
        )
        latents = latents.to(self.device)

        self.scheduler.set_timesteps(self.steps)
        latents = latents * self.scheduler.init_noise_sigma

        for t in tqdm(self.scheduler.timesteps):
            latent_model_input = torch.cat([latents] * 2)

            latent_model_input = self.scheduler.scale_model_input(latent_model_input, t)

            with torch.no_grad():
                noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=text_embeddings).sample

            noise_pred_uncond, noise_pred_text = noise_pred.chunk(2)
            noise_pred = noise_pred_uncond + self.guidance_scale * (noise_pred_text - noise_pred_uncond)

            latents = self.scheduler.step(noise_pred, t, latents).prev_sample
        return latents

    def __decode(self, latents):
        latents = 1 / 0.18215 * latents

        with torch.no_grad():
            image = self.vae.decode(latents).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.detach().cpu().permute(0, 2, 3, 1).numpy()
        images = (image * 255).round().astype("uint8")
        pil_images = [Image.fromarray(image) for image in images]
        return pil_images

    def generate_pictures(self, text_embeddings):
        latents = self.__generate_latents(text_embeddings)
        return self.__decode(latents)
