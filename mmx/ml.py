import numpy as np
from typing import Union, List, Dict
from tqdm import tqdm
import scipy.cluster.hierarchy

import torch
import torch.nn as nn
from torchvision.io import read_image, ImageReadMode
from torchvision.models.quantization import resnet50, ResNet50_QuantizedWeights
from torchvision.models.quantization import mobilenet_v3_large, MobileNet_V3_Large_QuantizedWeights
from torchvision.models.quantization import resnet18, ResNet18_QuantizedWeights

from .denstream import DenStream
from .utils import download_url
from .const import *

class identity(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return x

class feat_extract:
    '''
    feature extraction module: output features from an image using an ML model
    '''
    def __init__(self,
                 model: str = 'resnet50',
                 verbose: bool = False) -> None:

        self.embedding_model, self.preprocess_model = feat_extract._get_model(model)
        self.verbose = verbose

    @staticmethod
    def _get_model(model: str):
        if model == 'resnet50':
            # 2048 features
            weights = ResNet50_QuantizedWeights.DEFAULT
            preprocess = weights.transforms()
            model = resnet50(weights=weights, quantize=True)
            model.fc = identity()
            model.eval()
            return model, preprocess

        elif model == 'resnet18':
            # 512 features
            weights = ResNet18_QuantizedWeights.DEFAULT
            preprocess = weights.transforms()
            model = resnet18(weights=weights, quantize=True)
            model.fc = identity()
            model.eval()
            return model, preprocess

        elif model == 'mobilenet':
            # 960 features
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

    def get_features_from_urls(self,image_urls: List[str]) -> List[np.ndarray]:

        if self.verbose: print(f'n_features = {len(image_urls)}')
        features = []
        for image_url in tqdm(image_urls):
            feature = self.get_features_from_url(image_url)
            features += [feature]

        return features

# class clustering:
#     def __init__(self,*args,**kwargs):
#         self.alg_func = None
#         self.verbose = None
#         self.labels = None

#     def append_data(self, data: List[Dict]) -> None:
#         pass

#     def fetch_clusters(self) -> List:
#         pass

class hcluster_clustering:

    def __init__(self,
                 base_threshold: float = HCLUSTER_THRESHOLD,
                 verbose: bool = False):

        self.base_threshold = base_threshold
        self.alg_func = hcluster_wrapper(base_threshold = self.base_threshold)
        self.labels = None
        self.meme_ids = None
        self.clusters = None
        self.verbose = verbose

    def append_data(self, data: List[Dict]) -> None:

        features = []
        meme_ids = []
        for meme in data:
            features.append(meme[MEMES_COL_FEAT_VEC])
            meme_ids.append(meme[MEMES_COL_ID])
        features = np.array(features)

        # distances = [np.linalg.norm(features[0]-features[i]) for i in range(1,len(features))]
        # meandist, stddist = np.mean(distances), np.std(distances)

        distances = np.sqrt(((np.expand_dims(features[::5],1)- np.expand_dims(features[::5],0))**2).sum(axis=-1))
        distances = np.triu(distances).reshape(-1)
        distances = distances[distances>0]
        meandist, stddist = np.mean(distances),np.std(distances)

        threshold = meandist-self.base_threshold*stddist
        self.labels = self.alg_func(features, threshold)
        self.meme_ids = meme_ids

    def form_clusters(self) -> None:
        if not (self.labels is None):
            mids = np.array(self.meme_ids)
            lbls = np.array(self.labels)

            clusters = []
            for lbl in np.unique(lbls):
                clusters.append(mids[np.argwhere(lbls==lbl)].reshape(-1).tolist())

            clusters.sort(key= lambda x: len(x),reverse=True)
            self.clusters = clusters
        else:
            print('no data! run append_data')


class hcluster_wrapper:
    '''
    wrapper of hcluster including load_dict methods
    '''
    def __init__(self, base_threshold: float, criterion: str = 'distance'):
        self.base_threshold = base_threshold
        self.criterion = criterion
        self._hcluster = self._gen_hcluster()

    def __call__(self,features,threshold):
        return self._hcluster(features,threshold)

    def _gen_hcluster(self):
        def hcluster(features,threshold):
            return scipy.cluster.hierarchy.fclusterdata(features, threshold, criterion = self.criterion)
        return hcluster

    def state_dict(self) -> Dict:
        state_dict = {key: value for key, value in self.__dict__.items()}
        del state_dict['_hcluster']
        return state_dict

    def state_dict_compressed(self) -> Dict:
        state_dict = self.state_dict().copy()
        return state_dict

    def load_state_dict(self, state_dict: Dict):
        state_dict = state_dict.copy()
        self.__dict__.update(state_dict)
        self._hcluster = self._gen_hcluster()

    def load_state_dict_compressed(self, state_dict_compressed: Dict, decompressor_func = None):
        self.load_state_dict(state_dict_compressed)

class denstream_clustering:
    '''denstream clustering module'''

    def __init__(self,
                 eps: float = DENSTREAM_EPS,
                 beta: float = DENSTREAM_BETA,
                 mu: int = DENSTREAM_MU,
                 lambd: float = DENSTREAM_LAMBDA,
                 min_samples: int = 5,
                 verbose: bool = False):

        # label_metrics_list = [metrics.homogeneity_score, metrics.completeness_score]
        self.alg_func = DenStream(eps, beta, mu, lambd, min_samples)
        # self.labels = None
        # self.meme_ids = None
        self.clusters = None
        self.verbose = verbose

    def append_datum(self, datum: np.ndarray, data_id: str, timestamp: int) -> None:

        if len(datum.shape) == 1:
            datum = datum.reshape(1,-1)

        self.alg_func.partial_fit(feature_array = datum,
                            time = timestamp,
                            label = None,
                            data_id = data_id,
                            request_period = 50)

    def append_data(self, data: List[Dict]) -> None:

        if self.verbose: print(f'clustering new data: {len(data)}')
        for meme in data:
            feature = meme[MEMES_COL_FEAT_VEC]
            meme_id = meme[MEMES_COL_ID]
            publ_timestamp = meme[MEMES_COL_PUBL_TIMESTAMP]
            self.append_datum(datum = feature,
                                data_id = meme_id,
                                timestamp = publ_timestamp)

    def form_clusters(self) -> None:
        self.clusters = None
    # def fetch_clusters(self) -> List:
        # clusters = self.ds._cluster_evaluate(self.ds.iterations)
        # clusters = self.ds.p_micro_clusters
        # clusters = [x.id_array for x in clusters]
        # return clusters.tolist()


