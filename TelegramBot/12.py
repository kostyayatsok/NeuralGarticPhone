from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from uuid import uuid4

from fastapi.middleware.cors import CORSMiddleware
# import TextEncoder
from io import BytesIO
#import PictureGenerator
#import PictureDescriber
from PIL import Image
import os

from Player import Player
import threading
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
player = Player()
def generate(texts):
   image = player.draw_pictures(texts)
   return image

def send(img_byte_arr):
    return Response(content=img_byte_arr, media_type="image/jpeg")

queue = []

@app.post(
  "/get_image",
  responses = {
     200: {
         "content": {"image/jpeg": {}}
     }
  },
  response_class=Response
)
async def get_image(id):
    print(f"{id}.png")
    if os.path.exists(f"{id}.jpg"):
      image=Image.open(f"{id}.jpg")
      img_byte_arr = BytesIO()
      image.save(img_byte_arr, format='JPEG')
      img_byte_arr = img_byte_arr.getvalue()
      return Response(content=img_byte_arr, media_type="image/jpeg")
    return None
  
@app.post('/add_text')
async def add_text(text):
    id = uuid4()
    queue.append((text, id))
    return id
    """img = Image.open("cat.jpg")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return Response(content=img_byte_arr, media_type="image/png")"""

BATCH_SIZE = 16
def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func


@background
def generate_text():
  while True:
    global queue
    if len(queue)>0:
        idx = min(BATCH_SIZE, len(queue))
        cur = queue[:idx]
        texts = list(map(lambda x : x[0], cur))
        ids = list(map(lambda x : x[1], cur))
        for img, id in zip(generate(texts), ids):
            img.save(f"{id}.jpg")
        queue = queue[idx:]
        # img_byte_arr = BytesIO()
        # img.save(img_byte_arr, format='PNG')
        # img_byte_arr = img_byte_arr.getvalue()
        # send(img_byte_arr)
        # return Response(content=img_byte_arr, media_type="image/png")"""


import nest_asyncio
from pyngrok import ngrok
import uvicorn
ngrok.set_auth_token("2ZnWHYpmwKHi5dtObtpx6VzftVS_2ChLCkbxdpG8na2BqGPg5")

generate_text()

ngrok_tunnel = ngrok.connect(8000)
print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000)