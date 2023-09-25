from flask import Flask, request, send_file
import sys
sys.path.append('./')

from mmx.api import mmx_api
from mmx.const import *
from mmx.utils import parse_json

server = mmx_api(verbose = True)

app = Flask(__name__)
# app.debug = True

@app.route("/")
def info():
    return 'API server'

@app.route("/api/clusters")
def fetch_clusters():
    # sorting_criterion = (f'{CLUSTERS_COL_SNAPSHOT}.{CLUSTERS_COL_SNAPSHOT_TIMESTAMP}', DESCENDING)
    # filter_criterion = {f'{CLUSTERS_COL_SNAPSHOT}.{CLUSTERS_COL_SNAPSHOT_TIMESTAMP}':1,
    #                     f'{CLUSTERS_COL_DENSTREAM_STATE_DICT}.p_micro_clusters.creation_time':1,
    #                     f'{CLUSTERS_COL_DENSTREAM_STATE_DICT}.p_micro_clusters.id_array':1}

    # result = server.clusters_col.find(filter={},projection=filter_criterion,sort=[sorting_criterion])
    # output = next(result)
    return parse_json(output)

@app.route("/api/memes")
def fetch_memes():
    return 'jiojiookk'

if __name__ == '__main__':
    app.run(debug = False, host='0.0.0.0', port = 8000)


