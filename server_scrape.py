from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from time import sleep

from mmx.core import mmx_server
from mmx.const import *

server = mmx_server(verbose = True)

def mmx_scraping_job():
    print('='*100)
    print('#'*25 + f' running mmx_scraping_job(minutes={SCRAPING_JOB_INTERVAL}) ' + '#'*25)
    server.exec_meme_scraping_feat_extract_run()

tnow = datetime.now()

scheduler = BackgroundScheduler()
job = scheduler.add_job(mmx_scraping_job,
                        'interval',
                        minutes = SCRAPING_JOB_INTERVAL,
                        next_run_time = tnow + timedelta(seconds=5))

scheduler.start()

print('running server_scrape.py')
while True:
    sleep(1)
