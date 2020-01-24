# visualization tool
# combine umap/tsne feature reduction with clustering
# grelade 2020

import pandas as pd
import argparse
import os

import matplotlib.pyplot as plt

import config as cfg

parser = argparse.ArgumentParser(prog='visualization tool')

parser.add_argument('--metadata_clustering')
parser.add_argument('--metadata_reduction')
#parser.add_argument('--merged_metadata',default='merged.tsv')

args = parser.parse_args()

# load columns names from config file
cells = cfg.metadata_columns
mindex = cfg.metadata_index_columns

md_cluster = args.metadata_clustering
md_reduction = args.metadata_reduction


md_cluster_csv = pd.read_csv(md_cluster,sep='\t')
md_reduction_csv = pd.read_csv(md_reduction,sep='\t')

md_combined_csv = pd.merge(md_cluster_csv,md_reduction_csv)

plot = md_combined_csv.plot.scatter(x=cells['umap_x_coord'],y=cells['umap_y_coord'],c=cells['cluster_id'])
plt.show()
