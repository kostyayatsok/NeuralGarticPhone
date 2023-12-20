import requests

url = "https://0670-35-236-139-123.ngrok.io/add_text"

print(requests.post(url, json={"text": "cat", "player": "token"}))