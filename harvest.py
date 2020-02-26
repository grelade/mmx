# all-in-one online tool
# grelade 2020

import time
import sys
import os
import pandas as pd
import argparse
import numpy as np
from datetime import datetime

# package libs
sys.path.append('bin')
import tools
from scrape_reddit import scraper
from feature_extract import feature_extractor
from cluster_scipy import clustering
from to_web import web_prepare
import config as cfg

# load columns names from config file
cells = cfg.metadata_columns
mindex = cfg.metadata_index_columns


def pick_th_optimal(ms,which):
	df = pd.DataFrame(ms,columns=['th','nclust']).sort_values(by='nclust',ascending=False)
	thmax = df['th'].iloc[0]
	df2 = df[df['th']>=thmax]
	try:
		return df2['th'].iloc[which]
	except IndexError:
		print('too little th points, picking largest')
		return df2['th'].iloc[0]


# parser.add_argument('--subreddit',type=str,default='memes',help='which subreddit to scrape; default=memes')
# parser.add_argument('--nopages',type=int,default=10,help='how many pages to scrape, if -1 then alg scrapes everything; default=10')
# parser.add_argument('--time',type=str,default='2020-01-01_00-00',help='scrape session timestamp')
# parser.add_argument('--datadir',type=str,default=cfg.default_datadir,help='where downloaded data should be stored; default='+cfg.default_datadir)
# parser.add_argument('--timelag',type=int,default=5,help='algorithm halt when connection limit is reached given in seconds; default=5')
# parser.add_argument('--dlmethod',default='wgetpy',help='download methods: wgetpy, wget (UNIX only) and urllibdl; default=wgetpy')

if __name__ == "__main__":

	#argument parser
	parser = argparse.ArgumentParser(prog='all-in-one online tool')
	parser.add_argument('--sublist',type=str,default='subreddits.tsv',help='specify tsv file with list of subreddits')
	parser.add_argument('--cluster_cutoff',type=int,default=5,help='specify cluster size cutoff to include in the web summary')
	parser.add_argument('--th_samplesize',type=int,default=20,help='specify number of samples in similarity threshold search')
	parser.add_argument('--th_which',type=int,default=2,help='specify which similarity threshold to pick starting from value maximizing total number of clusters')
	parser.add_argument('--max_duplicate',type=int,default=10,help='specify the maximum number of duplicates after which subreddit scraping is skipped')
	parser.add_argument('--analdir',type=str,default='anal',help='set main dir storing all analyses')
	parser.add_argument('--analcurrdir',type=str,default='a01',help='set dir for current analysis')

	args = parser.parse_args()

	# loading conf file with list of subreddits
	cfile = args.sublist
	c = pd.read_csv(cfile,sep='\t')
	c_active = c[c['active']==1] # pick only active ones
	subreddits = c_active['subreddit'].to_list()
	nopages =c_active['nopages'].to_list()

	#paths
	analdir = args.analdir
	analname = args.analcurrdir
	analmd = 'md'
	dir = os.path.join(analdir,analname)
	tools.mkdir(dir)
	mdpath = os.path.join(dir,analmd+'.tsv')
	md_featspath = os.path.join(dir,analmd+'_features.tsv')
	md_clusterspath = os.path.join(dir,analmd+'_clusterscipy.tsv')
	md_webpath = os.path.join(dir,analmd+'_web.tsv')

	# check whether continue or start new analysis
	if os.path.exists(mdpath) and os.path.exists(md_featspath) and os.path.exists(md_clusterspath) and os.path.exists(md_webpath):
		print('found metadata files, appending new data')
		# load existing main metadata
		md = tools.loadmd(mdpath)
		# load existing features metadata
		md_feats = tools.loadmd(md_featspath)
		#load existing clusters metadata
		md_clusters = tools.loadmd(md_clusterspath)

	else:
		print('no metadata files found, creating new db')
		# create new main metadata
		md = pd.DataFrame(columns=cfg.md_cols)
		# features metadata
		md_feats = pd.DataFrame(columns=cfg.md_feats_cols)
		# clusters metadata
		md_clusters = pd.DataFrame(columns=cfg.md_clusters_cols)

	# ResNet feature extractor
	fe = feature_extractor('resnet')

	id = 0
	dupl_num = 0
	dupl_max = args.max_duplicate

	for subreddit,nopage in zip(subreddits,nopages):
		scrap = scraper(name=subreddit,nopages=nopage)

		while scrap.active:
			try:
				#scraping
				record = scrap.getmeme()
				if not record == {}:
					# temporary record df
					mdtemp = pd.DataFrame(columns=cfg.md_cols)
					record[cells['id']] = id
					mdtemp = mdtemp.append(record,ignore_index=True)

					# identify record duplicates
					cmpfields = [cells['scrape_source'],cells['image_title'],cells['image_url']]
					record_exists = (md[cmpfields]==mdtemp[cmpfields].iloc[0]).apply(lambda x: x.all(),axis=1).any()
					if not record_exists:

						md = md.append(record,ignore_index=True)
						#feature extraction
						feature = fe.extract_url(record[cells['image_url']])
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


	th0 = 5
	ms = []
	nmeasures = args.th_samplesize
	cutoff = args.cluster_cutoff
	# find optimal threshold
	for i in np.linspace(-1,.3,nmeasures):
		th = th0 + th0*i

		print('clustering('+str(th)+')')
		clust = clustering(threshold=th)
		clust.load_features(md_feats.copy())
		md_clusters = clust.gen_clusters()

		print('web_prepare('+str(cutoff)+')')
		wp = web_prepare(cluster_cutoff=cutoff)
		wp.setmd(md.copy())
		wp.setmd_cluster(md_clusters.copy())
		md_web = wp.combine_web().copy()

		noclusters = md_web.values.shape[0]
		print('# of clusters>'+str(cutoff)+':',noclusters)
		ms.append([th,noclusters])

	# cluster/web_prepare with optimal threshold
	th_optimal = pick_th_optimal(ms,args.th_which)
	# clustering
	print('clustering('+str(th_optimal)+')')
	clust = clustering(threshold=th_optimal)
	clust.load_features(md_feats.copy())
	md_clusters = clust.gen_clusters().copy()

	# prepare for web
	print('web_prepare()')
	wp = web_prepare(cluster_cutoff=cutoff)
	wp.setmd(md.copy())
	wp.setmd_cluster(md_clusters.copy())
	md_web = wp.combine_web().copy()

	tools.savemd(md,mdpath)
	tools.savemd(md_feats,md_featspath)
	tools.savemd(md_clusters,md_clusterspath)
	tools.savemd(md_web,md_webpath)
