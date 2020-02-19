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

# tested method, less secure for unknown urls
def wget(url,out):

	com = "wget --no-check-certificate " + url + " -q -O \""+ out + "\""
	res = 1
	tries = 0
	limit = 10
	print('wget:',url,'->',out)
	while res>0 and tries < limit:
		try:
			res = subprocess.call(com,shell=True)
			tries = tries + 1
			#print('wget:',res)
			if res>0: time.sleep(2)
		except subprocess.TimeoutExpired as e:
			print('timeout reached:',e)
			continue


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

# loa metadata
def loadmd(logpath):
	print("load metadata file")
	#log = log.set_index(mindex)
	return pd.read_csv(logpath,sep='\t')


# make dir if nonexistent
def mkdir(a):
    sep = os.sep
    dirs = a.strip(sep).split(sep)
    path=''
    for dire in dirs:
        path = os.path.join(path,dire)
        if (not os.path.isdir(path)):
            os.mkdir(path)

class scraper:

	def __init__(self,*args,**kwargs):
		self.nopages = kwargs['nopages']
		self.subreddit = kwargs['name']
		self.active = True
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
		# extract one meme
		if len(self.all_urls)>0:
		    return self.extract()

		# reached self.nopages
		elif self.nopages==self.currpage:
		    self.active = False
		    print("reached page",self.nopages)
		    return {}

		# page ends
		elif self.nopages>self.currpage:
		    regex1 = "next-button.+?\"(.+?)\""
		    pattern1 = re.compile(regex1)
		    link1 = re.findall(pattern1,self.htmltext)

			# is it last page
		    if(len(link1) < 4 and link1[0]=='desktop-onboarding-sign-up__form-note'): # dirty way of identifying last page
		        print("reached subreddits' last page",self.currpage)
		        self.active = False
		        return {}

			# move to next page
		    else:
		        self.url = link1[0]
		        self.currpage += 1
		        self.gethtml()
		        return self.extract()

class feature_extractor:

	def __init__(self,model):
		self.model = self.named_model(model)
		self.dlfile = dlmethod = globals()['wget']

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
		self.dlfile(imgurl,temp_file)

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

	def __init__(self,*args,**kwargs):
		self.md_feats = ''
		self.th = kwargs['threshold']

	def load_features(self,feats):
		self.md_feats = feats

	# clustering function
	def cl(self,thr,arr):
	    return hcluster.fclusterdata(arr, thr, criterion="distance")


	def gen_clusters(self):
		th = self.th # threshold value
		self.md_feats[cells['feature_vector']] = self.md_feats[cells['feature_vector']].apply(lambda x:list(map(float,x.split(','))))

		size0 = len(self.md_feats[cells['feature_vector']][0])
		for i in range(0,size0):
		    self.md_feats['feat_'+str(i)] = self.md_feats[cells['feature_vector']].apply(lambda x: x[i])
		arr = self.md_feats[['feat_'+str(i) for i in range(size0)]].to_numpy()

		distances = [np.linalg.norm(arr[0]-arr[i]) for i in range(1,len(arr))]
		meandist,stddist = np.mean(distances), np.std(distances)

		cls = self.cl(meandist-th*stddist,arr[:])

		cluster_col = pd.Series(cls,name=cells['cluster_id'])
		result = self.md_feats[mindex].join(cluster_col)

		return result

class web_prepare:

	def __init__(self,**kwargs):
		self.md = ''
		self.md_cluster = ''
		self.cutoff = kwargs['cluster_cutoff']

	def setmd(self,md):
		self.md = md

	def setmd_cluster(self,mdcluster):
		self.md_cluster = mdcluster

	def combine_web(self):

		test = self.md
		csv = self.md_cluster

		t = csv[cells['cluster_id']].value_counts()
		csv[cells['cluster_size']] = csv[cells['cluster_id']].map(lambda x:t[x])
		csv20 = pd.merge(csv,test).sort_values(by=cells['image_publ_date'])
		csv2 = csv20.drop_duplicates(subset=[cells['cluster_size'],cells['cluster_id']])
		csv3 = csv2.sort_values(by=cells['cluster_size'],ascending=False)
		csv4 = csv3[csv3[cells['cluster_size']]>=5][1:]

		result = csv4
		return result

def pick_th_optimal(ms,which):
	df = pd.DataFrame(ms,columns=['th','nclust']).sort_values(by='nclust',ascending=False)
	thmax = df['th'].iloc[0]
	df2 = df[df['th']>=thmax]
	return df2['th'].iloc[which]


#argument parser
parser = argparse.ArgumentParser(prog='all-in-one online tool')
# parser.add_argument('--subreddit',type=str,default='memes',help='which subreddit to scrape; default=memes')
# parser.add_argument('--nopages',type=int,default=10,help='how many pages to scrape, if -1 then alg scrapes everything; default=10')
# parser.add_argument('--time',type=str,default='2020-01-01_00-00',help='scrape session timestamp')
# parser.add_argument('--datadir',type=str,default=cfg.default_datadir,help='where downloaded data should be stored; default='+cfg.default_datadir)
# parser.add_argument('--timelag',type=int,default=5,help='algorithm halt when connection limit is reached given in seconds; default=5')
# parser.add_argument('--dlmethod',default='wgetpy',help='download methods: wgetpy, wget (UNIX only) and urllibdl; default=wgetpy')

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
	analname = 'a01'
	analmd = 'md'
	dir = os.path.join(analdir,analname)
	mkdir(dir)
	mdpath = os.path.join(dir,analmd+'.tsv')
	md_featspath = os.path.join(dir,analmd+'_features.tsv')
	md_clusterspath = os.path.join(dir,analmd+'_clusterscipy.tsv')
	md_webpath = os.path.join(dir,analmd+'_web.tsv')

	# check whether continue or start new analysis
	if os.path.exists(mdpath) and os.path.exists(md_featspath) and os.path.exists(md_clusterspath) and os.path.exists(md_webpath):
		# load existing main metadata
		md = loadmd(mdpath)
		# load existing features metadata
		md_feats = loadmd(md_featspath)
		#load existing clusters metadata
		md_clusters = loadmd(md_clusterspath)

	else:
		# create new main metadata
		md = pd.DataFrame(columns=mindex + [cells['image_filename'],cells['image_title'],cells['image_upvotes'],cells['no_of_comments'],cells['image_publ_date'],cells['image_url']])
		# features metadata
		md_feats = pd.DataFrame(columns=mindex + [cells['feature_vector']])
		# clusters metadata
		md_clusters = pd.DataFrame(columns=mindex + [cells['cluster_id']])



	# ResNet feature extractor
	fe = feature_extractor('resnet')

	id = 0
	dupl_num = 0
	dupl_max = 10

	for subreddit,nopage in zip(subreddits,nopages):
		scrap = scraper(name=subreddit,nopages=nopage)

		while scrap.active:
			try:
				#scraping
				record = scrap.getmeme()
				if not record == {}:
					# temporary record df
					mdtemp = pd.DataFrame(columns=mindex + [cells['image_filename'],cells['image_title'],cells['image_upvotes'],cells['no_of_comments'],cells['image_publ_date'],cells['image_url']])
					record[cells['id']] = id
					mdtemp = mdtemp.append(record,ignore_index=True)

					# identify record duplicates
					cmpfields = [cells['scrape_source'],cells['image_title'],cells['image_url']]
					record_exists = (md[cmpfields]==mdtemp[cmpfields].iloc[0]).apply(lambda x: x.all(),axis=1).any()
					if not record_exists:

						md = md.append(record,ignore_index=True)
						#feature extraction
						feature = fe.extract(record[cells['image_url']])
						md_feats = md_feats.append({cells['id']:record[cells['id']],cells['scrape_time']:record[cells['scrape_time']],cells['scrape_source']:record[cells['scrape_source']],cells['feature_vector']:feature},ignore_index=True)
						id += 1
					else:
						print('duplicate found')
						if dupl_num<dupl_max:
							dupl_num += 1
						else:
							print('maximum duplicate reached; skipping to next subreddit')
							dupl_num = 0
							break

			except Exception as ex:
				# skip all exceptions for now
				print(ex)
				pass


	# th0 = 5
	# ms = []
	# nmeasures = 20
	# # find optimal threshold
	# for i in np.linspace(-1,.3,nmeasures):
	# 	th = th0 + th0*i
	#
	# 	print('clustering('+str(th)+')')
	# 	clust = clustering(threshold=th)
	# 	clust.load_features(md_feats.copy())
	# 	md_clusters = clust.gen_clusters()
	#
	# 	print('web_prepare(5)')
	# 	wp = web_prepare(cluster_cutoff=5)
	# 	wp.setmd(md.copy())
	# 	wp.setmd_cluster(md_clusters.copy())
	# 	md_web = wp.combine_web()
	#
	# 	noclusters = md_web.values.shape[0]
	# 	print('# of clusters>5:',noclusters)
	# 	ms.append([th,noclusters])
	#
	# # cluster/web_prepare with optimal threshold
	# th_optimal = pick_th_optimal(ms,2)
	# # clustering
	# print('clustering('+str(th_optimal)+')')
	# clust = clustering(threshold=th_optimal)
	# clust.load_features(md_feats.copy())
	# md_clusters = clust.gen_clusters()
	md_clusters = loadmd(md_clusterspath)
	# prepare for web
	print('web_prepare()')
	wp = web_prepare(cluster_cutoff=5)
	wp.setmd(md.copy())
	wp.setmd_cluster(md_clusters.copy())
	md_web = wp.combine_web()

	savemd(md,mdpath)
	savemd(md_feats,md_featspath)
	savemd(md_clusters,md_clusterspath)
	savemd(md_web,md_webpath)
