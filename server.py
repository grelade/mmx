from flask import Flask, request, send_file
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from tqdm import tqdm

from mmx.core import mmx_server

server = mmx_server(verbose = True)

def mmx_scraping_job():
    print('='*100)
    print('#'*25+' running mmx_scraping_job() ' + '#'*25)
    server.exec_meme_scraping_run()

def mmx_clustering_job():
    print('='*100)
    print('#'*25+' running mmx_clustering_job() ' + '#'*25)
    server.exec_clustering_run()

tnow = datetime.now()
tdelta_scraping = timedelta(seconds=10)
tdelta_clustering = timedelta(seconds=60)

scheduler = BackgroundScheduler()
job = scheduler.add_job(mmx_scraping_job,
                        'interval',
                        minutes = 30,
                        next_run_time = tnow + tdelta_scraping)

job = scheduler.add_job(mmx_clustering_job,
                        'interval',
                        minutes = 120,
                        next_run_time = tnow + tdelta_clustering)

scheduler.start()

app = Flask(__name__)
# app.debug = True

@app.route("/api/clusters")
def fetch_clusters():
    return 'jiojio'

@app.route("/api/memes")
def fetch_memes():
    return 'jiojio'

if __name__ == '__main__':

    app.run(port=8001)


