from io import BytesIO

import requests
from PIL import Image


def post_text(text):
    print('post text: '+text)
    URL_first = URL + "/add_text" + "?text=" + text
    resp = requests.post(URL_first)
    print('id is '+resp.text)
    if resp.status_code < 200 or resp.status_code >= 300:
        raise RuntimeError('ERROR: Server is unavailable')
    return resp.text


def post_image(image_path):
    print('post image: ' + image_path)
    URL_first = URL + "/add_image"
    files = {'file': open(image_path, 'rb')}
    resp = requests.post(URL_first, files=files)
    if resp.status_code < 200 or resp.status_code >= 300:
        raise RuntimeError('ERROR: Server is unavailable')
    print('id is ' + resp.text)
    return resp.text


def get_image(image_id, path):
    URL_second = URL + "/get_image" + "?id=" + image_id
    resp = requests.post(URL_second)
    if resp.status_code < 200 or resp.status_code >= 300:
        raise RuntimeError('ERROR: Server is unavailable')
    if resp.text == "":
        return None
    img = Image.open(BytesIO(resp.content))
    img.save(path)
    return path


def get_text(text_id):
    URL_second = URL + "/get_text" + "?id=" + text_id
    resp = requests.post(URL_second)
    if resp.status_code < 200 or resp.status_code >= 300:
        raise RuntimeError('ERROR: Server is unavailable')
    if resp.text == "":
        return None
    return resp.text


URL = 'https://d1c7-34-105-95-165.ngrok-free.app'
