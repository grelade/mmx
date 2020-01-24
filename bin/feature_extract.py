#
# Copyright 2017 Zegami Ltd
# modifications: grelade 2020

"""Preprocess images using Keras pre-trained models."""

import argparse
import csv
import os

from keras import applications
from keras.applications.resnet50 import preprocess_input
from keras.preprocessing import image
import numpy as np
import pandas as pd

import config as cfg

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def named_model(name):
    # include_top=False removes the fully connected layer at the end/top of the network
    # This allows us to get the feature vector as opposed to a classification
    if name == 'Xception':
        return applications.xception.Xception(weights='imagenet', include_top=False, pooling='avg')

    if name == 'VGG16':
        return applications.vgg16.VGG16(weights='imagenet', include_top=False, pooling='avg')

    if name == 'VGG19':
        return applications.vgg19.VGG19(weights='imagenet', include_top=False, pooling='avg')

    if name == 'InceptionV3':
        return applications.inception_v3.InceptionV3(weights='imagenet', include_top=False, pooling='avg')

    if name == 'MobileNet':
        return applications.mobilenet.MobileNet(weights='imagenet', include_top=False, pooling='avg')

    return applications.resnet50.ResNet50(weights='imagenet', include_top=False, pooling='avg')


parser = argparse.ArgumentParser(prog='Feature extractor')
parser.add_argument('--metadata', default=None, help='Path to the metadata tsv file')
#parser.add_argument('--imagedir', default=None)
parser.add_argument('--datadir',type=str,default=cfg.default_datadir)
parser.add_argument(
    '--model',
    default='ResNet50',
    nargs="?",
    type=named_model,
    help='Name of the pre-trained model to use'
)


pargs = parser.parse_args()

# load metadata column names from config file
cells = cfg.metadata_columns
mindex = cfg.metadata_index_columns

metadata = pargs.metadata
datadir = pargs.datadir

def get_feature(metadata):
    #print('{}'.format(metadata['id']))

    try:
        # reconstruct path to image
        img_path = os.path.join(datadir,metadata[cells['scrape_time']],metadata[cells['scrape_source']], metadata[cells['image_filename']])

        if os.path.isfile(img_path):
            print('exec feature extraction: {}'.format(img_path))
            try:
                # load image setting the image size to 224 x 224
                img = image.load_img(img_path, target_size=(224, 224))
                # convert image to numpy array
                x = image.img_to_array(img)
                # the image is now in an array of shape (3, 224, 224)
                # but we need to expand it to (1, 2, 224, 224) as Keras is expecting a list of images
                x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)

                # extract the features
                features = pargs.model.predict(x)[0]
                # convert from Numpy to a list of values
                features_arr = np.char.mod('%f', features)

                return {cells['id']: metadata[cells['id']],
                        cells['scrape_time']: metadata[cells['scrape_time']],
                        cells['scrape_source']: metadata[cells['scrape_source']],
                        cells['feature_vector']: ','.join(features_arr)}
            except Exception as ex:
                # skip all exceptions for now
                print(ex)
                pass
    except Exception as ex:
        # skip all exceptions for now
        print(ex)
        pass
    return None


def start():
    try:
        # read the source file
        data = pd.read_csv(metadata, sep='\t')

        # extract features
        features = map(get_feature, data.T.to_dict().values())

        # remove empty entries
        #features = filter(None, features)

        # write to a tab delimited file

        data_features = pd.DataFrame(columns=mindex + [cells['feature_vector']])

        for feature in features:
            data_features = data_features.append(feature,ignore_index=True)
        #
        # with open(os.path.join(source_dir, '{}_features.tsv'.format(source_filename)), 'w') as output:
        #     w = csv.DictWriter(output, fieldnames=['id', 'features'], delimiter='\t', lineterminator='\n')
        #     w.writeheader()
        #     w.writerows(features)

        data_features_path = os.path.splitext(metadata)[0]+'_features.tsv'
        data_features = data_features.set_index(mindex)
        data_features.to_csv(data_features_path, sep='\t')

    except EnvironmentError as e:
        print(e)


if __name__ == '__main__':
    start()
