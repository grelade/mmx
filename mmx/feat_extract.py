import numpy as np
import tflite_support
from PIL import Image, UnidentifiedImageError
from typing import Union, List
from werkzeug.datastructures import FileStorage
from .const import *

AVAILABLE_FEAT_EXTRACT_MODELS = {'mobilenet_v3_small': 'mmx/feat_extract_model/mobilenet_v3_small.tflite',
                              'mobilenet_v3_large': 'mmx/feat_extract_model/mobilenet_v3_large.tflite',
                              'resnet_v1_50': 'mmx/feat_extract_model/resnet_v1_50.tflite',
                              'efficientnet_v2_m': 'mmx/feat_extract_model/efficientnet_v2_m.tflite'}

class feat_extractor:

    def __init__(self):

        self.model_name = None
        self.model = None
        self.input_image_size = None
        self.n_features = None

    def _infer_model_parameters(self, model_path: str):
        md = tflite_support.metadata.MetadataDisplayer.with_model_file(model_path)
        metadata = eval(md.get_metadata_json())
        input_metadata = metadata['subgraph_metadata'][0]['input_tensor_metadata'][0]['description']
        output_metadata = metadata['subgraph_metadata'][0]['output_tensor_metadata'][0]['description']
        if 'optimal_input_size' in input_metadata:
            self.input_image_size = eval(input_metadata.split('=')[1])
        else:
            print(f'''could not infer input_image_size from "{input_metadata}"''')
            self.input_image_size = [224,224]
            print(f'setting input_image_size = {self.input_image_size}')

        if 'n_features' in output_metadata:
            self.n_features = eval(output_metadata.split('=')[1])
        else:
            print(f'''could not infer n_features from "{output_metadata}"''')
            self.n_features = 1024
            print(f'setting n_features = {self.n_features}')

    def load_model(self, model_name: str = FEAT_EXTRACT_MODEL) -> bool:

        for model_name_, model_path in AVAILABLE_FEAT_EXTRACT_MODELS.items():
            if model_name == model_name_:
                self.model = tflite_support.task.vision.ImageEmbedder.create_from_file(model_path)
                self._infer_model_parameters(model_path)
                self.model_name = model_name
                return True
        return False


    def get_featvec(self, file_storage: Union[FileStorage,str]) -> Union[None,List]:
        feat_vec = None
        try:

            if isinstance(file_storage,FileStorage):
                img = Image.open(file_storage.stream)
            else:
                img = Image.open(file_storage)

            img = img.resize(self.input_image_size)
            img = img.convert(mode='RGB')
            img_array = np.array(img)

            img = tflite_support.task.vision.TensorImage(img_array)
            featvec_result = self.model.embed(img)
            del img,img_array
            feat_vec = featvec_result.embeddings[0].feature_vector.value.tolist()

        except UnidentifiedImageError as e:
            print(f'UnidentifiedImageError: feature extraction fail {e}')

        return feat_vec

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.model.close()

