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

    def __encode_batch(self, tokens):
        sz = len(tokens)
        with torch.no_grad():
            text_embeddings = self.text_encoder(tokens.input_ids.to(self.device))[0]
            max_length = tokens.input_ids.shape[-1]
        uncond_input = self.tokenizer(
            [""] * sz, padding="max_length", max_length=max_length, return_tensors="pt"
        )
        with torch.no_grad():
            uncond_embeddings = self.text_encoder(uncond_input.input_ids.to(self.device))[0]
        return [uncond_embeddings, text_embeddings]

    def encode(self, prompt):

        result = []
        for batch_beg in range(0, len(prompt), self.batch_size):
            batch_end = min(len(prompt), batch_beg + self.batch_size)
            cut = prompt[batch_beg:batch_end]
            text_input = self.tokenizer(cut, padding="max_length", max_length=self.tokenizer.model_max_length, truncation=True, return_tensors="pt")
            result += self.__encode_batch(text_input)
        # print(text_input)

        return torch.cat(result)


