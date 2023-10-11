import requests
import argparse

from mmx.const import *

parser = argparse.ArgumentParser(description='image feature extraction check',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-f', '--image_filename', type=str, default='test.jpg',
                    help='''image filename to send to feature extraction''')
parser.add_argument('-s', '--feat_extract_server', type=str, default=FEAT_EXTRACT_API_URL,
                    help='''feature extraction server''')

args = parser.parse_args()

filename = args.image_filename
fe_server = args.feat_extract_server

with open(filename, "rb") as f:
    data = f.read()

headers = {}
response = requests.post(fe_server,
                         headers=headers,
                         files={'file':data})

print(response.json())
