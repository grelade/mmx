import hashlib
import os
import wget
from urllib.error import HTTPError, ContentTooShortError
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
    TEMP_PATH = 'img.tmp'

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
                wget.download(image_url, out = TEMP_PATH)
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
        except ContentTooShortError:
            print(f'ContentTooShortError: problem with image_url={image_url}; incomplete downlaod; resuming')
            pass

    return path
