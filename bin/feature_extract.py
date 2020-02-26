from keras import applications
from keras.applications.resnet50 import preprocess_input
from keras.preprocessing import image

import tools
import os
import numpy as np
#import subprocess

class feature_extractor:

	def __init__(self,model):
		self.model = self.named_model(model)
		self.dlfile = dlmethod = tools.wget

	def named_model(self,name):
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

	def extract(self,file):

		# load image setting the image size to 224 x 224
		img = image.load_img(file,target_size=(224, 224))

		# convert image to numpy array
		x = image.img_to_array(img)
		# the image is now in an array of shape (3, 224, 224)
		# but we need to expand it to (1, 2, 224, 224) as Keras is expecting a list of images
		x = np.expand_dims(x, axis=0)
		x = preprocess_input(x)

		# extract the features
		features = self.model.predict(x)[0]
		# convert from Numpy to a list of values
		features_arr = np.char.mod('%f', features)
		#print(features)
		return ','.join(features_arr)


	def extract_url(self,imgurl):
		temp_file = 'temp'+os.path.splitext(imgurl)[1]
		if os.path.exists(temp_file): os.remove(temp_file)
		self.dlfile(imgurl,temp_file)
		try:
			a = self.extract(temp_file)
			os.remove(temp_file)
			return a
		except OSError:
			print('file not an image')
			os.remove(temp_file)


	def extract_path(self,imgpath):
		try:
			return self.extract(imgpath)
		except OSError:
			print('file not an image')


if __name__ == "__main__":

	parser = argparse.ArgumentParser(prog='feature_extract tool for reddit')
	# parser.add_argument('--subreddit',type=str,default='memes',help='which subreddit to scrape; default=memes')
	# parser.add_argument('--nopages',type=int,default=10,help='how many pages to scrape, if -1 then alg scrapes everything; default=10')
	# parser.add_argument('--time',type=str,default='2020-01-01_00-00',help='scrape session timestamp')
	# parser.add_argument('--datadir',type=str,default=cfg.default_datadir,help='where downloaded data should be stored; default='+cfg.default_datadir)
	# parser.add_argument('--timelag',type=int,default=5,help='algorithm halt when connection limit is reached given in seconds; default=5')
	# parser.add_argument('--dlmethod',default='wgetpy',help='download methods: wgetpy, wget (UNIX only) and urllibdl; default=wgetpy')

	args = parser.parse_args()
