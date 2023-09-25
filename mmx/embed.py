import numpy as np
import mediapipe as mp
from PIL import Image, UnidentifiedImageError
from typing import Union, List

from .const import *

BaseOptions = mp.tasks.BaseOptions
ImageEmbedder = mp.tasks.vision.ImageEmbedder
ImageEmbedderOptions = mp.tasks.vision.ImageEmbedderOptions
VisionRunningMode = mp.tasks.vision.RunningMode

class embedder:

    def __init__(self, quantize_model: bool = True):

        self.model_name = None
        self.quantize_model = quantize_model
        self.model = None

    def load_model(self,model_name: str):
        if model_name != self.model_name:

            options = ImageEmbedderOptions(
                base_options=BaseOptions(model_asset_path=EMBEDDING_MODEL_PATH),
                quantize=self.quantize_model,
                running_mode=VisionRunningMode.IMAGE)

            self.model = ImageEmbedder.create_from_options(options)
            self.model_name = model_name

    def embed_file(self,file_storage) -> Union[None,List]:
        output = None
        try:
            img = Image.open(file_storage.stream)
            img_array = np.array(img)
            img = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_array)
            embedding_result = self.model.embed(img)
            del img,img_array
            output = embedding_result.embeddings[0].embedding.tolist()

        except UnidentifiedImageError as e:
            print('UnidentifiedImageError: embedding fail {e}')

        return output

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.model.close()


