import pandas as pd
import numpy as np
import argparse
import os
import config as cfg
import scipy.cluster.hierarchy as hcluster


parser = argparse.ArgumentParser(prog='scipy clustering tool')

parser.add_argument('--metadata',default=None, help='metadata with extracted features') #
parser.add_argument('--th',default=25, help='threshold value')
args = parser.parse_args()

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

def cl(th,arr):
    return hcluster.fclusterdata(arr, th, criterion="distance")

cls = cl(meandist-10*stddist,arr[:])

#cells['cluster_id']

addcol = pd.Series(cls,name=cells['cluster_id'])
cluster_features = features[mindex].join(addcol)


destination_dir = os.path.dirname(dset)
source_filename = os.path.splitext(dset)[0].split(os.sep)[-1]
tsv_name = os.path.join(destination_dir, '{}_clusterscipy.tsv'.format(source_filename))
#sorted_all = sorted_all.join(names,on='id',how='right',lsuffix='0',sort=False).drop('id',axis=1)
#sorted_all = sorted_all.rename(columns={"id0":"id"})

# export
cluster_features = cluster_features.set_index(mindex)
cluster_features.to_csv(tsv_name,sep='\t')

#print(sorted_all.value_counts())
