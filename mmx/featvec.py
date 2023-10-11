from tqdm import tqdm
import numpy as np
import requests
from requests.exceptions import JSONDecodeError
from urllib.error import URLError
from typing import List,Union

from .const import *
from .utils import download_url, is_url, file_exists

class feat_extract:
    '''
    feature extraction module: output features from an image using an ML model
    '''

    def __init__(self,
                 verbose: bool = False) -> None:
        self.verbose = verbose
        self.local_embedder = None

    def _embedding_via_api(self, image_path: str) -> np.ndarray:
        img = None
        with open(image_path, "rb") as f:
            image = f.read()

        headers = {}
        response = requests.post(EMBEDDING_API_URL,
                                    headers = headers,
                                    files = {'file':image})

        response = response.json()
        if 'img_embed' in response.keys():
            img = np.array(response['img_embed'])

        return img

    def _set_local_embedder(self,model_name: str = EMBEDDING_MODEL) -> None:
        if not self.local_embedder:
            from .embed import embedder
            self.local_embedder = embedder()
            self.local_embedder.load_model(model_name = model_name)

    def _embedding_via_local_embedder(self, image_path: str) -> np.ndarray:
        self._set_local_embedder()

        img = None
        img = self.local_embedder.embed_file(image_path)
        if isinstance(img,list):
            img = np.array(img)

        return img

    def get_features_from_url(self, image_url: str, emb_mode: str = 'api') -> Union[np.ndarray,None]:

        img = None
        try:
            if is_url(image_url):
                image_path = download_url(image_url = image_url)
            elif file_exists(image_url):
                image_path = image_url
            else:
                image_path = None

            if image_path:
                if emb_mode == 'local':
                    img = self._embedding_via_local_embedder(image_path)
                elif emb_mode == 'api':
                    img = self._embedding_via_api(image_path)

        except RuntimeError as e:
            print(f'RuntimeError: read_image({image_url}) error: {e}')

        except JSONDecodeError as e:
            print(f'JSONDecodeError: response.json() ({image_url}) response error: {e}')

        except URLError as e:
            print(f'URLError: {image_url} {e}')

        except ValueError as e:
            print(f'ValueError: {image_url} {e}')

        return img

    def get_features_from_urls(self,image_urls: List[str]) -> List[np.ndarray]:

        if self.verbose: print(f'n_features = {len(image_urls)}')
        features = []
        for image_url in tqdm(image_urls):
            feature = self.get_features_from_url(image_url)
            features += [feature]

        return features
