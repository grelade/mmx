import pandas as pd
import numpy as np
import argparse
import os
import config as cfg
import scipy.cluster.hierarchy as hcluster


parser = argparse.ArgumentParser(prog='scipy clustering tool')
parser.add_argument('--metadata',default=None,type=str, help='metadata with extracted features') #
parser.add_argument('--th',default=10,type=float, help='threshold value given as multiplicity of stds of interimage distances')

def run(*a,**kwargs):

	default_args = vars(parser.parse_known_args()[0])
	args = argparse.Namespace(**{**default_args,**kwargs})

	# load metadata column names from config file
	cells = cfg.metadata_columns
	mindex = cfg.metadata_index_columns

	dset = args.metadata
	# similarity threshold
	th = args.th

	features = pd.read_csv(dset,sep='\t')
	# map 'features' col from str to list
	features[cells['feature_vector']] = features[cells['feature_vector']].apply(lambda x:list(map(float,x.split(','))))

	size0 = len(features[cells['feature_vector']][0])
	for i in range(0,size0):
	    features['feat_'+str(i)] = features[cells['feature_vector']].apply(lambda x: x[i])
	arr = features[['feat_'+str(i) for i in range(size0)]].to_numpy()

	distances = [np.linalg.norm(arr[0]-arr[i]) for i in range(1,len(arr))]
	meandist,stddist = np.mean(distances), np.std(distances)

	# clustering function
	def cl(thr,arr):
	    return hcluster.fclusterdata(arr, thr, criterion="distance")

	cls = cl(meandist-th*stddist,arr[:])


	cluster_col = pd.Series(cls,name=cells['cluster_id'])
	cluster_features = features[mindex].join(cluster_col)


	destination_dir = os.path.dirname(dset)
	source_filename = os.path.splitext(dset)[0].split(os.sep)[-1]
	tsv_name = os.path.join(destination_dir, '{}_clusterscipy.tsv'.format(source_filename))


	# export
	cluster_features = cluster_features.set_index(mindex)
	cluster_features.to_csv(tsv_name,sep='\t')


if __name__ == '__main__':
	args = parser.parse_args()
	run(**vars(args))
