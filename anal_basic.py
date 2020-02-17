import subprocess
import time
import os
import sys

sys.path.append('bin')
import config as cfg
import argparse
import functools, operator
import glob
import merge_metadata
import feature_extract
import cluster_scipy

parser = argparse.ArgumentParser(prog='basic analyzer tool')

parser.add_argument('--metadatas',nargs='+')
#parser.add_argument('--analdir',default=cfg.default_analdir)
parser.add_argument('--analname',default='analysis01')
#parser.add_argument('--clustercutoff',default=5,help='cluster size cutoff')
args = parser.parse_args()

# parse regex like *.tsv into list of files
mds0 = list(map(glob.glob,args.metadatas))
mds = list(set(functools.reduce(operator.iconcat, mds0 , [])))
#mds = args.metadatas

analdir = cfg.default_analdir
analname = args.analname
analdir_full = os.path.join(analdir,analname)


# mkdir if it does not exist
if (not os.path.isdir(analdir)):
	os.mkdir(analdir)

# mkdir if it does not exist
if (not os.path.isdir(analdir_full)):
	os.mkdir(analidr_full)


mddir = os.path.join(analdir_full,analname+'.tsv')

# 1) merge reports for further analysis
print('merging metadata files: ',mds)
print('merged file',mddir)

merge_metadata.run(metadatas=mds,merged_metadata=mddir)

# 2) run feature extraction
# Xception
# VGG16
# VGG19
# InceptionV3
# MobileNet
print('running feature extraction')

feature_extract.run(metadata=mddir,model='Xception')

# 3) run basic clustering
print('find euclidean distance clusters')

mdfeaturedir = os.path.splitext(mddir)[0]+'_features.tsv'
cluster_scipy.run(metadata=mdfeaturedir,th=7.8)
# cmd = 'python '+os.path.join('bin','cluster_basic.py')+' --metadata '+mdfeaturedir
# print(cmd)
# subprocess.call(cmd,shell=True)
