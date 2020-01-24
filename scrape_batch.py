# automated scraping script

import subprocess
import time
import sys

sys.path.append('bin')
import config as cfg

subreddits = ['memes','dankmemes','wholesomememes']
time0 = time.strftime(cfg.default_date_format, time.localtime())
nopages = 1

for sub in subreddits:

    subprocess.call('python bin/scrape_reddit.py --subreddit '+sub+' --datadir '+cfg.default_datadir+' --time '+time0+' --nopages '+str(nopages),shell=True)
