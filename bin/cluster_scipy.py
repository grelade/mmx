import scipy.cluster.hierarchy as hcluster
import numpy as np
import config as cfg
import pandas as pd

# load columns names from config file


class clustering:

	def __init__(self,*args,**kwargs):
		self.md_feats = ''
		self.th = kwargs['threshold']
		self.cells = cfg.metadata_columns
		self.mindex = cfg.metadata_index_columns

	def load_features(self,feats):
		self.md_feats = feats

	# clustering function
	def cl(self,thr,arr):
	    return hcluster.fclusterdata(arr, thr, criterion="distance")


	def gen_clusters(self):
		th = self.th # threshold value
		self.md_feats[self.cells['feature_vector']] = self.md_feats[self.cells['feature_vector']].apply(lambda x:list(map(float,x.split(','))))

		size0 = len(self.md_feats[self.cells['feature_vector']][0])
		for i in range(0,size0):
		    self.md_feats['feat_'+str(i)] = self.md_feats[self.cells['feature_vector']].apply(lambda x: x[i])
		arr = self.md_feats[['feat_'+str(i) for i in range(size0)]].to_numpy()

		distances = [np.linalg.norm(arr[0]-arr[i]) for i in range(1,len(arr))]
		meandist,stddist = np.mean(distances), np.std(distances)

		cls = self.cl(meandist-th*stddist,arr[:])

		cluster_col = pd.Series(cls,name=self.cells['cluster_id'])
		result = self.md_feats[self.mindex].join(cluster_col)

		return result

if __name__ == "__main__":

	parser = argparse.ArgumentParser(prog='cluster tool')
	# parser.add_argument('--subreddit',type=str,default='memes',help='which subreddit to scrape; default=memes')
	# parser.add_argument('--nopages',type=int,default=10,help='how many pages to scrape, if -1 then alg scrapes everything; default=10')
	# parser.add_argument('--time',type=str,default='2020-01-01_00-00',help='scrape session timestamp')
	# parser.add_argument('--datadir',type=str,default=cfg.default_datadir,help='where downloaded data should be stored; default='+cfg.default_datadir)
	# parser.add_argument('--timelag',type=int,default=5,help='algorithm halt when connection limit is reached given in seconds; default=5')
	# parser.add_argument('--dlmethod',default='wgetpy',help='download methods: wgetpy, wget (UNIX only) and urllibdl; default=wgetpy')

	args = parser.parse_args()
