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
args = {}

def run(*a,**kwargs):

	global args
	default_args = vars(parser.parse_known_args()[0])
	args = argparse.Namespace(**{**default_args,**kwargs})
	# print(args)
	# input()
	mds = args.metadatas
	mergedmd = args.merged_metadata

	cols = pd.read_csv(mds[0],sep="\t").columns
	merged_dataset = pd.DataFrame(columns=cols)
	# new_cols = pd.DataFrame(columns=['date','sourcename'])

	# merged_dataset = pd.concat([dataset0,new_cols],axis=1).set_index(['id','da','sourcename'])

	for dataset in mds:
	    # extract current name and date
	    # name = os.path.splitext(source)[0].split(os.sep)[-1]
	    # time0 = os.path.splitext(source)[0].split(os.sep)[-2]

	    dataset_csv = pd.read_csv(dataset,sep="\t")
	    # appendix = pd.DataFrame.from_dict({'date':[date for i in range(len(dataset))],'sourcename':[name for i in range(len(dataset))],'id':[i for i in range(len(dataset))]})
	    # appendix = appendix.set_index('id')
	    # dataset2 = dataset.merge(appendix,on='id')
	    # dataset2.set_index(['id','date','sourcename'])
	    merged_dataset = merged_dataset.append(dataset_csv)

	merged_dataset = merged_dataset.set_index(mindex)
	merged_dataset.to_csv(mergedmd,sep='\t')

parser = argparse.ArgumentParser(prog='metadata merge tool')
parser.add_argument('--metadatas',nargs='+')
parser.add_argument('--merged_metadata',default='merged.tsv')

if __name__ == "__main__":
	args = parser.parse_args()
	run(**vars(args))
