# automated scraping script

import subprocess
import time
import sys
import os
sys.path.append('bin')
import config as cfg
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--conf',default='subreddits.tsv')
parser.add_argument('--dlmethod',default='wgetpy')
pargs = parser.parse_args()

cfile = pargs.conf


time0 = time.strftime(cfg.default_date_format, time.localtime())

# loading conf file with list of subreddits
c = pd.read_csv(cfile,sep='\t')
c_active = c[c['active']==1] # pick only active ones
subreddits = c_active['subreddit'].to_list()
nopages =c_active['nopages'].to_list()


dlmethod = pargs.dlmethod

for sub,nopage in zip(subreddits,nopages):

    subprocess.call('python '   +os.path.join('bin','scrape_reddit.py')
                                +' --subreddit '+sub
                                +' --datadir '+cfg.default_datadir
                                +' --time '+time0
                                +' --nopages '+str(nopage)
                                +' --dlmethod '+dlmethod,shell=True)
    time.sleep(10)
