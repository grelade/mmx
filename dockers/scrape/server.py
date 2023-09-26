from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from time import sleep
import argparse

import sys
sys.path.append('./')
from mmx.core import mmx_server_scrape_embed_cluster

parser = argparse.ArgumentParser(description='mmx scrape server')

parser.add_argument('-m', '--mongodb_url', type=str, required=True,
                    help='''Specify the url for MONGO database. Could be:
                            URI: mongodb://localhost:27100 or,
                            Path to file: /var/secrets/mongodb_url (useful in docker secrets)''')

parser.add_argument('-r', '--run_mode', type=str, default='single', choices=['single','continuous'],
                    help='''Run mode = [continuous, single]. Single run will run scraping job once.
                            Continuous mode will be open forever and executed every job_interval minutes''')

parser.add_argument('-i', '--job_interval', type=int, default=120,
                    help='''Specify the time interval in minutes for which the job is executed in the continuous run mode.
                            Ignored for single run mode.''')

args = parser.parse_args()
mongodb_url = args.mongodb_url
run_mode = args.run_mode
job_interval = args.job_interval

server = mmx_server_scrape_embed_cluster(mongodb_url = mongodb_url, verbose = True)
if not server.is_mongodb_active():
    print('Could not connect to mongo; exiting')
    exit()

def scrape_job():
    print('='*100)
    print('#'*25 + f' SCRAPE job start ' + '#'*25)
    server.exec_meme_scraping_feat_extract_run()

print('running SCRAPE server')
print(f'run_mode = {run_mode}')
if run_mode == 'continuous':
    print(f'job_interval = {job_interval}')

if run_mode == 'continuous':

    tnow = datetime.now()
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(scrape_job,
                            'interval',
                            minutes = job_interval,
                            next_run_time = tnow + timedelta(seconds=5))

    scheduler.start()
    while True:
        sleep(1)

else:
    scrape_job()
