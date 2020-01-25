# visualization tool
# combine umap/tsne feature reduction with clustering
# grelade 2020

import pandas as pd
import argparse
import os

import matplotlib.pyplot as plt
import cv2
from mpl_toolkits.axes_grid1 import ImageGrid

import config as cfg

parser = argparse.ArgumentParser(prog='visualization tool')

parser.add_argument('--metadata_clustering')
parser.add_argument('--metadata_reduction')
parser.add_argument('--metadata')
parser.add_argument('--minclustersize',type=int,default=5)
#parser.add_argument('--merged_metadata',default='merged.tsv')

args = parser.parse_args()

# load columns names from config file
cells = cfg.metadata_columns
mindex = cfg.metadata_index_columns

md = args.metadata
md_cluster = args.metadata_clustering
md_reduction = args.metadata_reduction

mincluster = args.minclustersize

md_cluster_csv = pd.read_csv(md_cluster,sep='\t')
md_reduction_csv = pd.read_csv(md_reduction,sep='\t')

md_combined_csv = pd.merge(md_cluster_csv,md_reduction_csv)
#md_combined_csv[cells['cluster_id']] =

freq = md_combined_csv[cells['cluster_id']].value_counts()
md_combined_csv['cluster_size'] = md_combined_csv[cells['cluster_id']].map(lambda x: freq[x])
#.plot.scatter(x='umap_x',y='umap_y',c='cluster')

plot = md_combined_csv[md_combined_csv['cluster_size']>mincluster].plot.scatter(x=cells['umap_x_coord'],
                                                                                y=cells['umap_y_coord'],
                                                                                c=cells['cluster_id'],
                                                                                cmap='gist_rainbow')
plt.show()


md_csv = pd.read_csv(md,sep='\t')
combined2 = pd.merge(md_combined_csv,md_csv)

files = combined2[combined2['cluster_size']>mincluster].sort_values(by='cluster_size',ascending=False)[{cells['scrape_time'],
                                                                                                        cells['scrape_source'],
                                                                                                        cells['image_filename']}]

filesarray = []
for index,file in files.iterrows():
    filesarray.append(os.path.join( cfg.default_datadir,
                                    file[cells['scrape_time']],
                                    file[cells['scrape_source']],
                                    file[cells['image_filename']]))

fa2 = map(lambda x: cv2.cvtColor(cv2.resize(cv2.imread(x),(400, 400), interpolation=cv2.INTER_LINEAR),cv2.COLOR_BGR2RGB),filesarray)


fig = plt.figure(figsize=(50., 50.))


grid = ImageGrid(fig, 111,  # similar to subplot(111)
                 nrows_ncols=(3, 27),  # creates 2x2 grid of axes
                 axes_pad=0,  # pad between axes in inch.
                 )

for ax, im in zip(grid, fa2):
    # Iterating over the grid returns the Axes.
    ax.axis('off')
    ax.imshow(im)


plt.show()
