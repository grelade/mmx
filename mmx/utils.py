import hashlib
import os
import wget
from urllib.error import HTTPError
from urllib.parse import urlparse

def hash_string(input_string):
    # Create a new SHA-256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the input string encoded as bytes
    sha256_hash.update(input_string.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_string = sha256_hash.hexdigest()

    return hashed_string

def download_url(image_url: str) -> str:
    '''
    download image file located at image_url.
    Returns temp file path or None if no file/inappropriate file.
    '''
    TEMP_PATH = './tempimg'
    path = None

    try:
        if os.path.exists(TEMP_PATH): os.remove(TEMP_PATH)
        url_parsed = urlparse(image_url)

        if url_parsed.netloc == 'v.redd.it':
            # do not download videos
            return path
        elif len(url_parsed.path.split('.')) == 2 and url_parsed.path.split('.')[1] == 'gif':
            # do not download gifs
            return path
        else:
            wget.download(image_url, out = TEMP_PATH)
        path = TEMP_PATH

    except HTTPError:
        print(f'HTTPError: problem with image_url={image_url}; no image in url')

    except RuntimeError:
        print(f'RuntimeError: problem with image_url={image_url}; unknown image type')

    return path
