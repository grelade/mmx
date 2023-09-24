import requests

filename = 'test.jpg'

with open(filename, "rb") as f:
    data = f.read()

headers = {}
response = requests.post('http://localhost:8001/embedding',
                         headers=headers,
                         files={'file':data})

print(response.json())
