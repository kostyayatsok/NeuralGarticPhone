import configparser
from fastapi import FastAPI
from fastapi.responses import Response
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
import os
from Player import Player
import threading
import nest_asyncio
from pyngrok import ngrok
import uvicorn

queue = []
player = Player()
BATCH_SIZE = 16
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def send(img_byte_arr):
    return Response(content=img_byte_arr, media_type="image/jpeg")


@app.post(
    "/get_image",
    responses={200: {"content": {"image/jpeg": {}}}},
    response_class=Response,
)
async def get_image(id):
    print(f"{id}.png")
    if os.path.exists(f"{id}.jpg"):
        image = Image.open(f"{id}.jpg")
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()
        return Response(content=img_byte_arr, media_type="image/jpeg")
    return None


@app.post("/add_text")
async def add_text(text):
    id = uuid4()
    queue.append((text, id))
    return id


def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()

    return backgrnd_func


@background
def generate_text():
    while True:
        global queue
        if len(queue) > 0:
            idx = min(BATCH_SIZE, len(queue))
            cur = queue[:idx]
            texts = list(map(lambda x: x[0], cur))
            ids = list(map(lambda x: x[1], cur))
            for img, id in zip(player.draw_pictures(texts), ids):
                img.save(f"{id}.jpg")
            queue = queue[idx:]


config = configparser.ConfigParser()
config.read("../config.ini")

ngrok.set_auth_token(config["server"]["token"])

generate_text()

uvicorn.run(app, port=8000)