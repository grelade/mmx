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
pargs = parser.parse_args()

cfile = pargs.conf

#
#subreddits = ['memes','dankmemes','wholesomememes','MemeEconomy','AdviceAnimals','ComedyCemetery','terriblefacebookmemes','funny']
#
time0 = time.strftime(cfg.default_date_format, time.localtime())
#nopages = 50

# loading conf file
c = pd.read_csv(cfile,sep='\t')
c_active = t[t['active']==1]
subreddits = c_active['subreddit'].to_list()
nopages =c_active['nopages'].to_list()

for sub,nopage in zip(subreddits,nopages):

    subprocess.call('python '+os.path.join('bin','scrape_reddit.py')+' --subreddit '+sub+' --datadir '+cfg.default_datadir+' --time '+time0+' --nopages '+str(nopage),shell=True)
    time.sleep(10)
