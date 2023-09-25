from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime,timedelta
from time import sleep
import sys
sys.path.append('./')

from mmx.core import mmx_server
from mmx.const import *

server = mmx_server(verbose = True)

def mmx_clustering_job():
    print('='*100)
    print('#'*25 + f' running mmx_clustering_job(minutes={CLUSTERING_JOB_INTERVAL}) ' + '#'*25)
    server.exec_clustering_run()

tnow = datetime.now()

scheduler = BackgroundScheduler()
job = scheduler.add_job(mmx_clustering_job,
                        'interval',
                        minutes = CLUSTERING_JOB_INTERVAL,
                        next_run_time = tnow + timedelta(seconds=2))

scheduler.start()

print('running server_cluster.py')

while True:
    sleep(1)

