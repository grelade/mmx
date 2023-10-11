import hashlib
import os
import wget
from urllib.error import HTTPError, ContentTooShortError
from urllib.parse import urlparse
from bson import json_util
import json
import os

from .const import *

def hash_string(input_string):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the input string encoded as bytes
    sha256_hash.update(input_string.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_string = sha256_hash.hexdigest()

    return hashed_string

def download_url(image_url: str,out_path: str = None) -> str:
    '''
    download image file located at image_url.
    Returns temp file path or None if no file/inappropriate file.
    '''
    TEMP_PATH = 'img.tmp'

    if out_path:
        TEMP_PATH = out_path

    while True:
        path = None
        try:
            if os.path.exists(TEMP_PATH): os.remove(TEMP_PATH)
            url_parsed = urlparse(image_url)

            if url_parsed.netloc == 'v.redd.it':
                # do not download videos
                break
            elif len(url_parsed.path.split('.')) == 2 and (url_parsed.path.split('.')[1] == 'gif' or url_parsed.path.split('.')[1] == 'gifv'):
                # do not download gifs
                break
            else:
                wget.download(image_url, out = TEMP_PATH, bar = None)
                # input('waiting')
                path = TEMP_PATH
                break

        except HTTPError:
            print(f'HTTPError: problem with image_url={image_url}; no image in url')
            break
        except RuntimeError:
            print(f'RuntimeError: problem with image_url={image_url}; unknown image type')
            break
        except ValueError:
            print(f'ValueError: problem with image_url={image_url}; incorrect url form')
            break
        except AttributeError:
            print(f'AttributeError: problem with image_url={image_url}; ???')
            break
        except ContentTooShortError:
            print(f'ContentTooShortError: problem with image_url={image_url}; incomplete downlaod; resuming')
            pass

    return path

def parse_json(data):
    '''
    parse data from mongodb to json
    '''
    data = json_util.dumps(data)
    dict_data = json.loads(data)

    convert = False
    if not isinstance(dict_data,list):
        convert = True
        dict_data = [dict_data]

    for i in range(len(dict_data)):
        dict_data[i]['_id'] = dict_data[i]['_id']["$oid"]

    if convert:
        dict_data = dict_data[0]

    return dict_data

def print_red(skk): print("\033[91m {}\033[00m" .format(skk))
def print_green(skk): print("\033[90m {}\033[00m" .format(skk))

def fetch_internal_image_url(meme):
    '''
    fetch the best image url useful for internal purposes (extracting feature vectors)
    '''
    image_url = meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_SOURCE]
    if meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_LOCAL]:
        image_url = meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_LOCAL]
    return image_url

def fetch_frontend_image_url(meme):
    '''
    fetch the best image url useful for external purposes (sending to frontend)
    '''
    image_url = meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_SOURCE]
    if meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_ALTER]:
        image_url = meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_ALTER]
    return image_url

def form_local_image_path(meme):
    file_name =  meme[MEMES_COL_ID]
    file_ext = meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_SOURCE].split('.')[-1]
    if file_ext not in ['jpg','jpeg','png']:
        return None
    out_path = LOCAL_IMG_STORAGE+f'/{file_name}.{file_ext}'
    return out_path

def download_local_image_url(meme):

    os.makedirs(LOCAL_IMG_STORAGE,exist_ok=True)

    out_path = form_local_image_path(meme)

    if out_path:
        image_path = download_url(image_url = meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_SOURCE],
                                    out_path = out_path)
        meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_LOCAL] = image_path
    return meme

def is_url(image_url: str):
    if 'http://' in image_url or 'https://' in image_url:
        return True
    return False

def file_exists(image_url: str):
    return os.path.exists(image_url)
