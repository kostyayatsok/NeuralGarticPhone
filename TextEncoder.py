from transformers import CLIPTextModel, CLIPTokenizer
import torch


class TextEncoder:
    # TextEncoder. It can capture prompts and convert them to vectors.
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu", batch_size=1):
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
        self.text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-large-patch14")
        self.device = device
        self.text_encoder = self.text_encoder.to(device)
        self.batch_size = batch_size

    def encode(self, prompt):
        text_input = self.tokenizer(prompt, padding="max_length", max_length=self.tokenizer.model_max_length, truncation=True, return_tensors="pt")

        with torch.no_grad():
            text_embeddings = self.text_encoder(text_input.input_ids.to(self.device))[0]
            max_length = text_input.input_ids.shape[-1]

        uncond_input = self.tokenizer(
            [""] * self.batch_size, padding="max_length", max_length=max_length, return_tensors="pt"
        )
        with torch.no_grad():
            uncond_embeddings = self.text_encoder(uncond_input.input_ids.to(self.device))[0]

        text_embeddings = torch.cat([uncond_embeddings, text_embeddings])

        return text_embeddings


