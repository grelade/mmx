# all-in-one online tool
# grelade 2020

import urllib
import re
import subprocess
import time
import sys
import os
import pandas as pd
import argparse
import numpy as np
import wget as wg
import csv
from datetime import datetime
sys.path.append('bin')
import config as cfg

from keras import applications
from keras.applications.resnet50 import preprocess_input
from keras.preprocessing import image

import scipy.cluster.hierarchy as hcluster

# load columns names from config file
cells = cfg.metadata_columns
mindex = cfg.metadata_index_columns

# needs python3-wget
def wgetpy(url,out):
	print('wgetpy:',url,'->',out)
	res = wg.download(url,out=out)
	print('wgetpy:',res)

# download whole html file
def geturl(urls):
	print('geturl URL:',urls)
	htmltext = ''
	ifsuccesful = False
	tries = 0
	limit = 25

	while not ifsuccesful and tries < limit:
		try:
			htmlfile = urllib.request.urlopen(urls)
			htmltext = htmlfile.read().decode("utf-8")
			ifsuccesful = True

		except urllib.error.HTTPError:
			print('reached connection limit: sleeping')
			time.sleep(20)
			tries = tries + 1
			continue
		except ValueError:
			print('ValueError detected!')
			tries = tries + 1
			continue
		except:
			print('catched other error: ',sys.exc_info()[0])
			tries = tries + 1
			continue

	return htmltext

# save metadata
def savemd(log,logpath):
	print("saving metadata file")
	log = log.set_index(mindex)
	log.to_csv(logpath,mode = 'w',sep='\t')

# make dir if nonexistent
def mkdir(a):
    sep = os.sep
    dirs = a.strip(sep).split(sep)
    path=''
    for dire in dirs:
        path = os.path.join(path,dire)
        if (not os.path.isdir(path)):
            os.mkdir(path)


#argument parser
parser = argparse.ArgumentParser(prog='all-in-one online tool')
# parser.add_argument('--subreddit',type=str,default='memes',help='which subreddit to scrape; default=memes')
# parser.add_argument('--nopages',type=int,default=10,help='how many pages to scrape, if -1 then alg scrapes everything; default=10')
# parser.add_argument('--time',type=str,default='2020-01-01_00-00',help='scrape session timestamp')
# parser.add_argument('--datadir',type=str,default=cfg.default_datadir,help='where downloaded data should be stored; default='+cfg.default_datadir)
# parser.add_argument('--timelag',type=int,default=5,help='algorithm halt when connection limit is reached given in seconds; default=5')
# parser.add_argument('--dlmethod',default='wgetpy',help='download methods: wgetpy, wget (UNIX only) and urllibdl; default=wgetpy')

class scraper:

	def __init__(self,*args,**kwargs):
		self.nopages = kwargs['nopages']
		self.subreddit = kwargs['name']
		self.activity = True
		self.currpage = 1
		self.url = "https://old.reddit.com/r/" + self.subreddit + "/"

		self.htmltext=''

		self.app_urls=''
		self.names=''
		self.upvotes=''
		self.comments=''
		self.publdate=''

		self.gethtml()

	def gethtml(self):
		self.htmltext = geturl(self.url)

		# regex to find urls
		these_regex = "data-url=\"(.+?)\""
		pattern = re.compile(these_regex)
		self.all_urls = re.findall(pattern,self.htmltext)

		# regex to find names
		names_regex = "data-event-action=\"title\".+?>(.+?)<"
		names_pattern = re.compile(names_regex)
		self.names = re.findall(names_pattern, self.htmltext)

		# regex to identify upvotes
		upvotes_regex = "data-score.+?\"(.+?)\""
		upvotes_pattern = re.compile(upvotes_regex)
		self.upvotes = re.findall(upvotes_pattern,self.htmltext)

		# regex number of comments
		comments_regex = "data-comments-count.+?\"(.+?)\""
		comments_pattern = re.compile(comments_regex)
		self.comments = re.findall(comments_pattern,self.htmltext)

		# regex publication date
		publdate_regex = "data-timestamp.+?\"(.+?)\""
		publdate_pattern = re.compile(publdate_regex)
		self.publdate = re.findall(publdate_pattern,self.htmltext)


	def extract(self):
		record = {}
		currurl = self.all_urls.pop(0)

		record[cells['scrape_time']] = int(datetime.timestamp(datetime.now()))
		record[cells['scrape_source']] = self.subreddit
		record[cells['image_title']] = self.names.pop(0)
		record[cells['image_upvotes']] = self.upvotes.pop(0)
		record[cells['no_of_comments']] = self.comments.pop(0)
		record[cells['image_publ_date']] = self.publdate.pop(0)
		record[cells['image_url']] = currurl

        # regex to identify extensions
        #ext_regex = "\.(jpg|jpeg|png|gif)"
		ext_regex = "\.("+(''.join(map(lambda x:x+'|',cfg.filetypes))[:-1])+")"
		ext_pattern = re.compile(ext_regex)
		ext = re.findall(ext_pattern,currurl)

		if len(ext)==1: return record
		else: return {}


	def getmeme(self):
		if len(self.all_urls)>0:
		    return self.extract()

		elif self.nopages>self.currpage:
		    regex1 = "next-button.+?\"(.+?)\""
		    pattern1 = re.compile(regex1)
		    link1 = re.findall(pattern1,self.htmltext)
		    print(link1)
		    if(len(link1) < 4 and link1[0]=='desktop-onboarding-sign-up__form-note'): # dirty way of identifying last page
		        print("reached subreddits' last page",self.currpage)
		        self.activity = False
		        return {}
		    else:
		        self.url = link1[0]
		        self.currpage += 1
		        self.gethtml()
		        return self.extract()
		elif self.nopages==self.currpage:
		    self.activity = False
		    print("reached page",self.nopages)
		    return {}

class feature_extractor:

	def __init__(self,model):
		self.model = self.named_model(model)

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

	def extract(self,imgurl):

		temp_file = 'temp'+os.path.splitext(imgurl)[1]
		if os.path.exists(temp_file): os.remove(temp_file)
		wgetpy(imgurl,temp_file)
		# load image setting the image size to 224 x 224
		img = image.load_img(temp_file, target_size=(224, 224))

		os.remove(temp_file)
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

class clustering:

	def __init__(self):
		self.md_feats = ''

	def load_features(self,feats):
		self.md_feats = feats

	# clustering function
	def cl(self,thr,arr):
	    return hcluster.fclusterdata(arr, thr, criterion="distance")


	def gen_clusters(self):
		th = 10 # threshold value
		self.md_feats[cells['feature_vector']] = self.md_feats[cells['feature_vector']].apply(lambda x:list(map(float,x.split(','))))

		size0 = len(self.md_feats[cells['feature_vector']][0])
		for i in range(0,size0):
		    self.md_feats['feat_'+str(i)] = self.md_feats[cells['feature_vector']].apply(lambda x: x[i])
		arr = self.md_feats[['feat_'+str(i) for i in range(size0)]].to_numpy()

		distances = [np.linalg.norm(arr[0]-arr[i]) for i in range(1,len(arr))]
		meandist,stddist = np.mean(distances), np.std(distances)

		cls = self.cl(meandist-th*stddist,arr[:])

		cluster_col = pd.Series(cls,name=cells['cluster_id'])
		return self.md_feats[mindex].join(cluster_col)

class web_prepare:

	def __init__(self,cutoff):
		self.md = ''
		self.md_cluster = ''
		self.cutoff = cutoff

	def setmd(self,md):
		self.md = md

	def setmd_cluster(self,mdcluster):
		self.md_cluster = mdcluster

	def combine_web(self):

		test = self.md
		csv = self.md_cluster

		t = csv[cells['cluster_id']].value_counts()
		csv[cells['cluster_size']] = csv[cells['cluster_id']].map(lambda x:t[x])
		csv2 = csv.drop_duplicates(subset=[cells['cluster_size'],cells['cluster_id']])
		csv3 = csv2.sort_values(by=cells['cluster_size'],ascending=False)
		csv4 = csv3[csv3[cells['cluster_size']]>=self.cutoff]


		result = pd.merge(csv4,test)


		# concat filename
		#destination_dir = os.path.dirname(md)
		#source_filename = os.path.splitext(md)[0].split(os.sep)[-1]
		#tsv_name = os.path.join(destination_dir, '{}_web.tsv'.format(source_filename))
		return result



	# extract relevant images and copy to anal dir
	# imgs = result[['time','source','filename']].values
	# for img in imgs:
	#     path = os.path.join(destination_dir,cfg.default_datadir,img[0],img[1])
	#     mkdir(path)
	#     file = os.path.join(cfg.default_datadir,img[0],img[1],img[2])
	#     where = os.path.join(path,img[2])
	#     shutil.copy(file,where)


if __name__ == "__main__":
	# tentative vars
	# subreddits = ['memes']
	# nopages = [1]

	# loading conf file with list of subreddits
	cfile = 'subreddits.tsv'
	c = pd.read_csv(cfile,sep='\t')
	c_active = c[c['active']==1] # pick only active ones
	subreddits = c_active['subreddit'].to_list()
	nopages =c_active['nopages'].to_list()

	#paths
	analdir = 'anal'
	analname = 'a07'
	mkdir(os.path.join(analdir,analname))
	mdpath = os.path.join(analdir,analname,analname+'.tsv')
	md_featspath = os.path.join(analdir,analname,analname+'_features.tsv')
	md_clusterspath = os.path.join(analdir,analname,analname+'_clusterscipy.tsv')
	md_webpath = os.path.join(analdir,analname,analname+'_web.tsv')

	# main metadata
	md = pd.DataFrame(columns=mindex + [cells['image_filename'],cells['image_title'],cells['image_upvotes'],cells['no_of_comments'],cells['image_publ_date']])

	# features metadata
	md_feats = pd.DataFrame(columns=mindex + [cells['feature_vector']])

	# clusters metadata
	md_clusters = pd.DataFrame(columns=mindex + [cells['cluster_id']])

	# ResNet feature extractor
	fe = feature_extractor('resnet')
	id = 0
	for subreddit,nopage in zip(subreddits,nopages):
		scrap = scraper(name=subreddit,nopages=nopage)

		while scrap.activity:
			try:
				#scraping
				record = scrap.getmeme()
				if not record == {}:

					#feature extraction
					feature = fe.extract(record[cells['image_url']])

					# append to md, md_feats
					record[cells['id']] = id
					md = md.append(record,ignore_index=True)
					md_feats = md_feats.append({cells['id']:record[cells['id']],cells['scrape_time']:record[cells['scrape_time']],cells['scrape_source']:record[cells['scrape_source']],cells['feature_vector']:feature},ignore_index=True)
					id += 1

			except Exception as ex:
				# skip all exceptions for now
				print(ex)
				pass

	# clustering
	clust = clustering()
	clust.load_features(md_feats)
	md_clusters = clust.gen_clusters()

	# prepare for web
	wp = web_prepare(2)
	wp.setmd(md)
	wp.setmd_cluster(md_clusters)
	md_web = wp.combine_web()

	savemd(md,mdpath)
	savemd(md_feats,md_featspath)
	savemd(md_clusters,md_clusterspath)
	savemd(md_web,md_webpath)
