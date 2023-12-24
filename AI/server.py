from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi import File, UploadFile
from uuid import uuid4

from fastapi.middleware.cors import CORSMiddleware
from Player import Player
from io import BytesIO
from PIL import Image
import shutil
import os
import nest_asyncio
import uvicorn


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

def generate_img(texts):
   image = player.draw_pictures(texts)
   return image

def generate_txt(image_paths):
   print(image_paths)
   images = []
   for image_path in image_paths:
      images.append(Image.open(image_path))
   texts = player.describe(images)
   return texts

def send(img_byte_arr):
    return Response(content=img_byte_arr, media_type="image/jpeg")

queue_image_gen = []
queue_text_gen = []
text_results = {}

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
    if os.path.exists(f"{id}.jpg"):
      image=Image.open(f"{id}.jpg")
      img_byte_arr = BytesIO()
      image.save(img_byte_arr, format='JPEG')
      img_byte_arr = img_byte_arr.getvalue()
      return Response(content=img_byte_arr, media_type="image/jpeg")
    return None

@app.post(
  "/get_text",
  responses = {
     200: {
         "content": {"text/plain": {}}
     }
  },
  response_class=Response
)
async def get_text(id):
    if id in text_results.keys():
      print('heays')
      return Response(content=text_results[id], media_type="text/plain")
    return None

@app.post('/add_text')
async def add_text(text):
    id = uuid4()
    queue_image_gen.append((text, id))
    return id


@app.post('/add_image')
async def add_image(file: UploadFile):
    id = uuid4()
    try:
        with open(str(id)+'.jpg', 'wb') as f:
            shutil.copyfileobj(file.file, f)
        queue_text_gen.append((str(id)+'.jpg', id))
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return id


BATCH_SIZE = 16
def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func


@background
def generate_image():
  while True:
    global queue_image_gen
    if len(queue_image_gen)>0:
        idx = min(BATCH_SIZE, len(queue_image_gen))
        cur = queue_image_gen[:idx]
        texts = list(map(lambda x : x[0], cur))
        ids = list(map(lambda x : x[1], cur))
        for img, id in zip(generate_img(texts), ids):
            img.save(f"{id}.jpg")
        queue_image_gen = queue_image_gen[idx:]


@background
def generate_text():
  while True:
    global queue_text_gen
    if len(queue_text_gen)>0:
        idx = min(BATCH_SIZE, len(queue_text_gen))
        cur = queue_text_gen[:idx]
        img_paths = list(map(lambda x : x[0], cur))
        ids = list(map(lambda x : x[1], cur))
        for img, id in zip(generate_txt(img_paths), ids):
            print(img)
            text_results[str(id)] = img
        queue_text_gen = queue_text_gen[idx:]

generate_text()
generate_image()

import nest_asyncio
from pyngrok import ngrok
import uvicorn
ngrok.set_auth_token("2ZnWHYpmwKHi5dtObtpx6VzftVS_2ChLCkbxdpG8na2BqGPg5")

generate_text()
generate_image()

ngrok_tunnel = ngrok.connect(8000)
print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000)