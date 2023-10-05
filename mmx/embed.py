import numpy as np
# import mediapipe as mp
import tflite_support
from PIL import Image, UnidentifiedImageError
from typing import Union, List

from .const import *

# BaseOptions = mp.tasks.BaseOptions
# ImageEmbedder = mp.tasks.vision.ImageEmbedder
# ImageEmbedderOptions = mp.tasks.vision.ImageEmbedderOptions
# VisionRunningMode = mp.tasks.vision.RunningMode

MOBILENET_V3_NAME = 'mobilenet_v3'
MOBILENET_V3_PATH = 'mmx/embed_model/mobilenet_v3_small_075_224_embedder.tflite'

RESNET50_NAME = 'resnet50'
RESNET50_PATH = 'mmx/embed_model/resnet50.tflite'


class embedder:

    def __init__(self, quantize_model: bool = True):

        self.model_name = None
        self.quantize_model = quantize_model
        self.model = None

    def load_model(self,model_name: str):

        if model_name == MOBILENET_V3_NAME:
            # options = ImageEmbedderOptions(
            #     base_options=BaseOptions(model_asset_path=MOBILENET_V3_PATH),
            #     quantize=self.quantize_model,
            #     running_mode=VisionRunningMode.IMAGE)

            self.model = tflite_support.task.vision.ImageEmbedder.create_from_file(MOBILENET_V3_PATH)
            # self.model = ImageEmbedder.create_from_options(options)
            self.model_name = model_name

        elif model_name == RESNET50_NAME:
            self.model = tflite_support.task.vision.ImageEmbedder.create_from_file(RESNET50_PATH)
            self.model_name = model_name


    def embed_file(self,file_storage) -> Union[None,List]:
        output = None
        try:
            img = Image.open(file_storage.stream)
            img = img.resize((224, 224))
            img_array = np.array(img)

            img = tflite_support.task.vision.TensorImage(img_array)
            # img = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_array)
            embedding_result = self.model.embed(img)
            del img,img_array
            # output = embedding_result.embeddings[0].embedding.tolist()
            output = embedding_result.embeddings[0].feature_vector.value.tolist()

        except UnidentifiedImageError as e:
            print(f'UnidentifiedImageError: embedding fail {e}')

        return output

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.model.close()


class feat_extract:
    '''
    feature extraction module: output features from an image using an ML model
    '''

    def __init__(self,
                 verbose: bool = False) -> None:

        self.verbose = verbose

    # def get_features(self,image_array: np.ndarray) -> Union[np.ndarray,None]:

    #     output = None
    #     if isinstance(image_array,np.ndarray):
    #         output = self.embedding_model(image_array)
    #     return output

    def get_features_from_url(self, image_url: str) -> Union[np.ndarray,None]:

        image_path = download_url(image_url = image_url)

        img = None
        try:
            if image_path:
                with open(image_path, "rb") as f:
                    image = f.read()

                headers = {}
                response = requests.post(FEAT_EXTRACT_API_URL,
                                         headers = headers,
                                         files = {'file':image})

                response = response.json()
                if 'img_embed' in response.keys():
                    img = np.array(response['img_embed'])

        except RuntimeError as e:
            print(f'read_image({image_url}) error: {e}')

        return img

    def get_features_from_urls(self,image_urls: List[str]) -> List[np.ndarray]:

        if self.verbose: print(f'n_features = {len(image_urls)}')
        features = []
        for image_url in tqdm(image_urls):
            feature = self.get_features_from_url(image_url)
            features += [feature]

        return features
