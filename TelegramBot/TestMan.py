from AlbumGenerator import Album
import requests


url = 'https://803f-34-133-214-198.ngrok-free.app'

files = {'file': open('randomPictures/img1.jpg', 'rb')}
resp = requests.post(url+'/add_image', files=files)
print(resp.json())
id = resp.json()
while True:
    resp = requests.post(url+'/get_text' + "?id=" + id)
    print(resp)
    print(resp.text)