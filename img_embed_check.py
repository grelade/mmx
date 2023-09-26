import requests

from mmx.const import *

filename = 'test.jpg'

with open(filename, "rb") as f:
    data = f.read()

headers = {}
response = requests.post(FEAT_EXTRACT_API_URL,
                         headers=headers,
                         files={'file':data})

print(response.json())
