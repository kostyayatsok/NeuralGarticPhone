import requests
from PIL import Image
from time import sleep
from io import BytesIO

txt = "Кошка"
resp = requests.post("http://127.0.0.1:8000/add_text?text=" + txt)
id = resp.text

while True:
    good_image_id = id[1:-1]
    URL_second = "http://127.0.0.1:8000/get_image" + "?id=" + good_image_id
    resp = requests.post(URL_second)
    if resp.text == "":
        sleep(10)
        continue
    img = Image.open(BytesIO(resp.content))
    img.save("test.png")
    break