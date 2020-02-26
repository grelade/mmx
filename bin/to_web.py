import pandas as pd
import config as cfg

class web_prepare:

	def __init__(self,**kwargs):
		self.md = ''
		self.md_cluster = ''
		self.cutoff = kwargs['cluster_cutoff']
		self.cells = cfg.metadata_columns
		self.mindex = cfg.metadata_index_columns

	def setmd(self,md):
		self.md = md

	def setmd_cluster(self,mdcluster):
		self.md_cluster = mdcluster

	def combine_web(self):

		test = self.md
		csv = self.md_cluster
		t = csv[self.cells['cluster_id']].value_counts()
		csv[self.cells['cluster_size']] = csv[self.cells['cluster_id']].map(lambda x:t[x])
		csv1 = pd.merge(csv,test)
		#csv1.to_csv('csv1_test.tsv',mode = 'w',sep='\t')
		#input()
		csv20 = csv1.sort_values(by=self.cells['image_publ_date'],na_position='last')
		#csv20 = pd.merge(csv,test)
		csv2 = csv20.drop_duplicates(subset=[self.cells['cluster_size'],self.cells['cluster_id']])
		csv3 = csv2.sort_values(by=self.cells['cluster_size'],ascending=False)
		csv4 = csv3[csv3[self.cells['cluster_size']]>=5][1:]

		result = csv4
		return result

if __name__ == "__main__":

	parser = argparse.ArgumentParser(prog='web-prepare tool for reddit')
	# parser.add_argument('--subreddit',type=str,default='memes',help='which subreddit to scrape; default=memes')
	# parser.add_argument('--nopages',type=int,default=10,help='how many pages to scrape, if -1 then alg scrapes everything; default=10')
	# parser.add_argument('--time',type=str,default='2020-01-01_00-00',help='scrape session timestamp')
	# parser.add_argument('--datadir',type=str,default=cfg.default_datadir,help='where downloaded data should be stored; default='+cfg.default_datadir)
	# parser.add_argument('--timelag',type=int,default=5,help='algorithm halt when connection limit is reached given in seconds; default=5')
	# parser.add_argument('--dlmethod',default='wgetpy',help='download methods: wgetpy, wget (UNIX only) and urllibdl; default=wgetpy')

	args = parser.parse_args()
