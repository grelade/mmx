import requests
import argparse

from mmx.const import *

parser = argparse.ArgumentParser(description='image embedding check',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-f', '--image_filename', type=str, default='test.jpg',
                    help='''image filename to send to embed''')
parser.add_argument('-s', '--embedding_server', type=str, default=EMBEDDING_API_URL,
                    help='''embedding server''')

args = parser.parse_args()

filename = args.image_filename
emb_server = args.embedding_server

with open(filename, "rb") as f:
    data = f.read()

headers = {}
response = requests.post(emb_server,
                         headers=headers,
                         files={'file':data})

print(response.json())
