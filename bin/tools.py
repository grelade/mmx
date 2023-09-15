import wget as wg
import subprocess
import time
import urllib
# import config as cfg
import os
import pandas as pd
import sys

# load columns names from config file
cells = cfg.metadata_columns
mindex = cfg.metadata_index_columns

# needs python3-wget
def wgetpy(url,out):
	'''download url and save as out using python3-wget'''
	print('wgetpy:',url,'->',out)
	res = wg.download(url,out=out)
	print('wgetpy:',res)

# tested method, less secure for unknown urls
def wget(url,out):
	'''download url and save as out using subprocess.call(wget) (LINUX only)'''
	com = "wget --no-check-certificate " + url + " -q -O \""+ out + "\""
	res = 1
	tries = 0
	limit = 10
	print('wget:',url,'->',out)
	while res>0 and tries < limit:
		try:
			res = subprocess.call(com,shell=True)
			tries = tries + 1
			#print('wget:',res)
			if res>0: time.sleep(2)
		except subprocess.TimeoutExpired as e:
			print('timeout reached:',e)
			continue


# save metadata
def savemd(log,logpath):
	'''save metadata pandas.DataFrame log file to logpath'''
	print("saving metadata file:",logpath)
	log = log.set_index(mindex)
	log.to_csv(logpath,mode = 'w',sep='\t')

# loa metadata
def loadmd(logpath):
	'''load metadata pandas.DataFrame log file from logpath'''
	print("load metadata file:",logpath)
	#log = log.set_index(mindex)
	return pd.read_csv(logpath,sep='\t')


# make dir if nonexistent
def mkdir(adir):
	'''mkdir adir (recursive function)'''
	sep = os.sep
	dirs = adir.strip(sep).split(sep)
	path=''
	for dire in dirs:
	    path = os.path.join(path,dire)
	    if (not os.path.isdir(path)): os.mkdir(path)
