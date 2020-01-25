import subprocess
import time
import os
import sys

sys.path.append('bin')
import config as cfg
import argparse


parser = argparse.ArgumentParser(prog='analyzer tool')

parser.add_argument('--metadatas',nargs='+')
parser.add_argument('--analdir',default=cfg.default_analdir)
parser.add_argument('--analname',default='analysis01')

args = parser.parse_args()

mds = args.metadatas

analdir = args.analdir
analname = args.analname
analdir_full = os.path.join(analdir,analname)


# mkdir if it does not exist
if (not os.path.isdir(analdir)):
	subprocess.call('mkdir '+analdir,shell=True)

# mkdir if it does not exist
if (not os.path.isdir(analdir_full)):
	subprocess.call('mkdir '+analdir_full,shell=True)


#datasets = ['data/2020-01-24_04:33/memes.tsv', 'data/2020-01-24_04:33/dankmemes.tsv', 'data/2020-01-24_04:33/wholesomememes.tsv']

mddir = os.path.join(analdir_full,analname+'.tsv')
#time0 = time.strftime("%Y-%m-%d_%H:%M", time.localtime())

mds_arg = ''
for md in mds:
    mds_arg=mds_arg+md+' '

# 1) merge reports for further analysis
print('merging metadata files: ',mds)
print('merged file',mddir)

cmd = 'python '+os.path.join('bin','merge_metadata.py')	+' --metadatas '+mds_arg
														+' --merged_metadata '+mddir
print(cmd)
subprocess.call(cmd,shell=True)



# 2) run feature extraction
print('running feature extraction')
cmd = 'python '+os.path.join('bin','feature_extract.py')+' --metadata '+mddir
print(cmd)
subprocess.call(cmd,shell=True)

mdfeaturedir = os.path.splitext(mddir)[0]+'_features.tsv'

# 3) run basic clustering
print('find euclidean distance clusters')
cmd = 'python '+os.path.join('bin','cluster_basic.py')+' --metadata '+mdfeaturedir
print(cmd)
subprocess.call(cmd,shell=True)

# 4) run umap feature reduction
print('find umap coords for visualization')
cmd = 'python '+os.path.join('bin','visual_umap.py')+' --metadata '+mdfeaturedir
print(cmd)
subprocess.call(cmd,shell=True)

# 5) run visualization tool to see how well clustering works
print('run visualization tool')
mdfeaturedir_cluster = os.path.splitext(mdfeaturedir)[0]+'_clusterbasic.tsv'
mdfeaturedir_reduction = os.path.splitext(mdfeaturedir)[0]+'_umap.tsv'

cmd = 'python '+os.path.join('bin','visual_tool.py')+' --metadata_cluster '+mdfeaturedir_cluster
													+' --metadata_reduction '+mdfeaturedir_reduction
													+' --metadata '+mddir
													+' --minclustersize '+'10'
print(cmd)
subprocess.call(cmd,shell=True)
