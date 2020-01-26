import pandas as pd
import torch
import argparse
import os
import config as cfg

# meme similarity measure
def dist(x,y):
    return torch.norm(torch.tensor(x)-torch.tensor(y))

parser = argparse.ArgumentParser(prog='euclidean distance cluster tool')

parser.add_argument('--metadata',default=None)
parser.add_argument('--th',default=25)
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

# create df with clusters
cluster_features = pd.DataFrame(columns=mindex + [cells['cluster_id']])





# find and cluster similar images
i = 1

while features.shape[0]>0:
    point = features.iloc[0] # fix one vec
    rem_pts = features.shift(-1)[:-1] # create df of remaining vecs
    rem_pts[cells['id']] = rem_pts[cells['id']].map(int) # deal with peculiarity of shift func

    # create temporary df holding all vecs similar to point
    cluster_temp = pd.DataFrame(columns=mindex + [cells['feature_vector']])
    cluster_temp = cluster_temp.append(point)

    # compare vector point with rem_pts through euclidean distance and threshold th
    similar_pts = rem_pts[rem_pts[cells['feature_vector']].map(lambda x: dist(point[cells['feature_vector']],x).numpy()) < th]
    #print(similar_pts)
    # append all similar points to df
    cluster_temp = cluster_temp.append(similar_pts)

    # drop vecs whose cluster was identified
    features = pd.concat([features,cluster_temp]).drop_duplicates(subset=mindex,keep=False)
    cluster_temp[cells['cluster_id']] = i
    print(cluster_temp)
    # append vecs with cluster i
    cluster_features = cluster_features.append(cluster_temp[set(mindex+[cells['cluster_id']])],sort=False)
    i+=1


# append names


destination_dir = os.path.dirname(dset)
source_filename = os.path.splitext(dset)[0].split(os.sep)[-1]
tsv_name = os.path.join(destination_dir, '{}_clusterbasic.tsv'.format(source_filename))
#sorted_all = sorted_all.join(names,on='id',how='right',lsuffix='0',sort=False).drop('id',axis=1)
#sorted_all = sorted_all.rename(columns={"id0":"id"})

# export
cluster_features = cluster_features.set_index(mindex)
cluster_features.to_csv(tsv_name,sep='\t')

#print(sorted_all.value_counts())
