import numpy as np
import os
from typing import Union

import torch
import torch.nn as nn
from torchvision.io import read_image, ImageReadMode
from torchvision.models.quantization import resnet50, ResNet50_QuantizedWeights
from torchvision.models.quantization import mobilenet_v3_large, MobileNet_V3_Large_QuantizedWeights

from .denstream import DenStream
from .utils import download_url

class identity(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return x

# 	def named_model(self,name):
# 		if name == 'Xception':
# 		    return applications.xception.Xception(weights='imagenet', include_top=False, pooling='avg')

# 		if name == 'VGG16':
# 		    return applications.vgg16.VGG16(weights='imagenet', include_top=False, pooling='avg')

# 		if name == 'VGG19':
# 		    return applications.vgg19.VGG19(weights='imagenet', include_top=False, pooling='avg')

# 		if name == 'InceptionV3':
# 		    return applications.inception_v3.InceptionV3(weights='imagenet', include_top=False, pooling='avg')

# 		if name == 'MobileNet':
# 		    return applications.mobilenet.MobileNet(weights='imagenet', include_top=False, pooling='avg')

# 		return applications.resnet50.ResNet50(weights='imagenet', include_top=False, pooling='avg')

class feat_extract:
    '''
    output features from an image using a computer vision ML model
    '''
    def __init__(self,
                 model: str = 'resnet50',
                 verbose: bool = False) -> None:

        self.embedding_model, self.preprocess_model = feat_extract._get_model(model)
        self.verbose = verbose

    @staticmethod
    def _get_model(model: str):
        if model == 'resnet50':
            weights = ResNet50_QuantizedWeights.DEFAULT
            preprocess = weights.transforms()
            model = resnet50(weights=weights, quantize=True)
            model.fc = identity()
            model.eval()
            return model, preprocess

        elif model == 'mobilenet':
            weights = MobileNet_V3_Large_QuantizedWeights.DEFAULT
            preprocess = weights.transforms()
            model = mobilenet_v3_large(weights=weights, quantize=True)
            model.classifier = identity()
            model.eval()
            return model, preprocess
        else:
            if self.verbose: print(f'unknown model = {model}')
            return None, None

    @staticmethod
    def image_url_to_tensor(image_url: str) -> Union[torch.Tensor,None]:

        temp_path = download_url(image_url = image_url)
        img = None
        try:
            if temp_path:
                img = read_image(temp_path, mode = ImageReadMode.RGB)

        except RuntimeError as e:
            print(f'read_image({image_url}) error: {e}')

        return img

    def get_features(self, image_tensor: torch.Tensor) -> Union[np.ndarray,None]:
        # output = 2*np.random.rand() - 1 + 0.1*np.array([random.random() for _ in range(128)])
        # output = output.astype(np.float32)
        output = None
        if isinstance(image_tensor,torch.Tensor):
            batch = self.preprocess_model(image_tensor).unsqueeze(0)
            output = self.embedding_model(batch).squeeze().numpy()

        return output

    def get_features_from_url(self, image_url: str) -> Union[np.ndarray,None]:
        image_tensor = feat_extract.image_url_to_tensor(image_url)
        # print(image_url, image_tensor.shape)
        feat = self.get_features(image_tensor)
        return feat

class denstream_clustering:
    '''denstream clustering algorithm'''

    def __init__(self,
                 eps: float = 5,
                 beta: float = 0.2,
                 mu: int = 6,
                 lambd: float = 1/500000,
                 min_samples: int = 5,
                 verbose: bool = False):

        # label_metrics_list = [metrics.homogeneity_score, metrics.completeness_score]
        self.ds = DenStream(eps, beta, mu, lambd, min_samples)
        self.verbose = verbose

    def cluster_data(self, data: np.ndarray, data_id: str, timestamp: int):

        if len(data.shape) == 1:
            data = data.reshape(1,-1)

        self.ds.partial_fit(feature_array = data,
                            time = timestamp,
                            label = None,
                            data_id = data_id,
                            request_period = None)


    def fetch_clusters(self):
        _ = self.ds._request_clustering()
        clusters = self.ds.p_micro_clusters
        clusters = [x.id_array for x in clusters]
        return clusters
