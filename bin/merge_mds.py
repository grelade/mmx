# merge tool
# combine multiple metadata files into one
# useful when creating daily snapshots of meme markets
# grelade 2020

import pandas as pd
import argparse
import os

import config as cfg

# load columns names from config file
cells = cfg.metadata_columns
mindex = cfg.metadata_index_columns

class merger:

	def __init__(self,mds):
		self.mds = mds

	def merge(self):
		cols = pd.read_csv(self.mds[0],sep="\t").columns
		merged_dataset = pd.DataFrame(columns=cols)

		for dataset in self.mds:
		    # extract current name and date
		    dataset_csv = pd.read_csv(dataset,sep="\t")
		    merged_dataset = merged_dataset.append(dataset_csv)

		return merged_dataset

if __name__ == "__main__":

	parser = argparse.ArgumentParser(prog='merge tool')
	# parser.add_argument('--subreddit',type=str,default='memes',help='which subreddit to scrape; default=memes')
	# parser.add_argument('--nopages',type=int,default=10,help='how many pages to scrape, if -1 then alg scrapes everything; default=10')
	# parser.add_argument('--time',type=str,default='2020-01-01_00-00',help='scrape session timestamp')
	# parser.add_argument('--datadir',type=str,default=cfg.default_datadir,help='where downloaded data should be stored; default='+cfg.default_datadir)
	# parser.add_argument('--timelag',type=int,default=5,help='algorithm halt when connection limit is reached given in seconds; default=5')
	# parser.add_argument('--dlmethod',default='wgetpy',help='download methods: wgetpy, wget (UNIX only) and urllibdl; default=wgetpy')

	args = parser.parse_args()
