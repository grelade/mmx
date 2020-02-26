import sys
import os
import time
import argparse
import pandas as pd

# package libs
sys.path.append('bin')
import tools
from scrape_reddit import scraper
from merge_mds import merger
from feature_extract import feature_extractor
from cluster_scipy import clustering
from to_web import web_prepare
import config as cfg

# load columns names from config file
cells = cfg.metadata_columns
mindex = cfg.metadata_index_columns


if __name__ == "__main__":

	#argument parser
	parser = argparse.ArgumentParser()
	parser.add_argument('--sublist',type=str,default='subreddits.tsv',help='specify tsv file with list of subreddits')
	parser.add_argument('--cluster_cutoff',type=int,default=5,help='specify cluster size cutoff to include in the web summary')
	parser.add_argument('--th',type=int,default=5,help='specify similarity threshold in clustering algorithm')
	parser.add_argument('--max_duplicate',type=int,default=10,help='specify the maximum number of duplicates after which subreddit scraping is skipped')
	parser.add_argument('--analdir',type=str,default='anal',help='set main dir storing all analyses')
	parser.add_argument('--analcurrdir',type=str,default='a02',help='set dir for current analysis')
	parser.add_argument('--datadir',type=str,default='data',help='set main dir storing data')

	args = parser.parse_args()

	# loading conf file with list of subreddits
	cfile = args.sublist
	c = pd.read_csv(cfile,sep='\t')
	c_active = c[c['active']==1] # pick only active ones
	subreddits = c_active['subreddit'].to_list()
	nopages =c_active['nopages'].to_list()

	# set single timestamp for whole hoard session
	time0 = time.strftime(cfg.default_date_format, time.localtime())

	# paths
	datadir = os.path.join(args.datadir,time0)
	tools.mkdir(datadir)


	print('scraper')
	id = 0
	dupl_num = 0
	dupl_max = args.max_duplicate

	for subreddit,nopage in zip(subreddits,nopages):

		scrap = scraper(name=subreddit,nopages=nopage)
		subdir = os.path.join(datadir,subreddit)
		tools.mkdir(subdir)
		mdpath = os.path.join(datadir,subreddit+'.tsv')
		# create new main metadata
		md = pd.DataFrame(columns=cfg.md_cols)

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
						# download image
						imgpath = os.path.join(subdir,record[cells['image_filename']])
						tools.wget(record[cells['image_url']],imgpath)
						# append img to metadata file
						md = md.append(record,ignore_index=True)

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
		tools.savemd(md,mdpath)


	print('merge')
	mds = [os.path.join(datadir,subreddit+'.tsv') for subreddit in subreddits]
	analdir = args.analdir
	analname = args.analcurrdir
	analprefix = 'md'
	analcurrdir = os.path.join(analdir,analname)
	tools.mkdir(analcurrdir)
	md_mergedpath = os.path.join(analcurrdir,analprefix+'.tsv')

	m = merger(mds)
	md_merged = m.merge()

	tools.savemd(md_merged,md_mergedpath)


	print('feature_extract')
	md_featspath = os.path.join(analcurrdir,analprefix+'_features.tsv')
	md_feats = pd.DataFrame(columns=cfg.md_feats_cols)

	fe = feature_extractor('resnet')
	for i,record in md_merged.iterrows():

		path = os.path.join(datadir,record[cells['scrape_source']],record[cells['image_filename']])
		print(path)
		feature = fe.extract_path(path)
		md_feats = md_feats.append({cells['id']:record[cells['id']],cells['scrape_time']:record[cells['scrape_time']],cells['scrape_source']:record[cells['scrape_source']],cells['feature_vector']:feature},ignore_index=True)

	tools.savemd(md_feats,md_featspath)


	print('find euclidean distance clusters')
	md_clusters = pd.DataFrame(columns=cfg.md_clusters_cols)
	md_clusterspath = os.path.join(analcurrdir,analprefix+'_clusterscipy.tsv')

	th=args.th
	clust = clustering(threshold=th)
	clust.load_features(md_feats.copy())
	md_clusters = clust.gen_clusters()

	tools.savemd(md_clusters,md_clusterspath)


	print('prepare for website')
	md_webpath = os.path.join(analcurrdir,analprefix+'_web.tsv')

	cutoff=args.cluster_cutoff
	wp = web_prepare(cluster_cutoff=cutoff)
	wp.setmd(md.copy())
	wp.setmd_cluster(md_clusters.copy())
	md_web = wp.combine_web().copy()

	tools.savemd(md_web,md_webpath)
