from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from time import sleep
import argparse

import sys
sys.path.append('./')
from mmx.servers_comp import mmx_server_cluster

parser = argparse.ArgumentParser(description='mmx cluster server')

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

parser.add_argument('-b', '--batch_size', type=int, default=500,
                    help='''Specify the batch size for clustering algorithm. Set to -1 to cluster all available data at once.''')

args = parser.parse_args()
mongodb_url = args.mongodb_url
run_mode = args.run_mode
job_interval = args.job_interval
batch_size = args.batch_size
batch_size = None if batch_size==-1 else batch_size

server = mmx_server_cluster(mongodb_url = mongodb_url, verbose = True)
if not server.is_mongodb_active():
    print('Could not connect to mongo; exiting')
    exit()

def cluster_job():
    print('='*100)
    print('#'*25 + f' CLUSTER job start ' + '#'*25)
    server.exec_clustering_run(clustering_batch_size = batch_size)

print('running CLUSTER server')
print(f'run_mode = {run_mode}')
if run_mode == 'continuous':
    print(f'job_interval = {job_interval}')
print(f'batch_size = {batch_size}')

if run_mode == 'continuous':

    tnow = datetime.now()
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(cluster_job,
                            'interval',
                            minutes = job_interval,
                            next_run_time = tnow + timedelta(seconds=5))

    scheduler.start()
    while True:
        sleep(1)

else:
    cluster_job()
