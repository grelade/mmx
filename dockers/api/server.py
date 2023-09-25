from flask import Flask, request, send_file
import sys
sys.path.append('./')

from mmx.api import mmx_api
from mmx.const import *
from mmx.utils import parse_json

server = mmx_api(verbose = True)

app = Flask(__name__)
# app.debug = True

@app.route(f"{API_V1_BASE_URL}/")
def info():
    info = 'mmx API server<br>'
    info += 'endpoints:<br>'
    info += f'<b>{API_V1_BASE_URL}/memes/</b> - fetch all memes (paginated)<br>'
    info += f'<b>{API_V1_BASE_URL}/memes/?sort=asc</b> - fetch all memes (paginated), sorted by publ_timestamp<br>'
    info += f'<b>{API_V1_BASE_URL}/memes/[meme_id]</b> - fetch a single meme with [meme_id]<br>'
    info += f'<b>{API_V1_BASE_URL}/clusters/</b> - fetch newest clusters<br>'
    info += f'<b>{API_V1_BASE_URL}/clusters/?detailed=1</b> - fetch newest clusters, detailed version<br>'
    return info

# fetch all memes (paginated)
@app.route(f"{API_V1_BASE_URL}/memes/",methods=["GET"])
def fetch_all_memes():
    page = request.args.get('page',default = 1, type = int)
    id_sort = request.args.get('sort',default='desc',type = str)
    id_sort_mongo = {'asc' : ASCENDING,
                     'desc' : DESCENDING }[id_sort]

    memes_count = server.memes_col.count_documents({})
    memes = list(server.memes_col.find({},{MEMES_COL_FEAT_VEC:0}).sort(MEMES_COL_PUBL_TIMESTAMP, id_sort_mongo).skip(API_PAGE_LIMIT * (page - 1)).limit(API_PAGE_LIMIT))

    if page*API_PAGE_LIMIT < memes_count:
        next_url = f"{API_V1_BASE_URL}/memes/?page={page+1}&sort={id_sort}"
    else:
        next_url = None

    return {API_NEXT_URL : next_url,
            MEMES_COLLECTION : parse_json(memes)}

# fetch single meme
@app.route(f"{API_V1_BASE_URL}/memes/<meme_id>",methods=["GET"])
def fetch_meme(meme_id: str):

    projection = {}
    # projection = {MEMES_COL_FEAT_VEC:0}
    meme = server.memes_col.find_one(filter={MEMES_COL_ID:meme_id},
                                     projection=projection)
    return parse_json(meme)

# fetch last clustering
@app.route(f"{API_V1_BASE_URL}/clusters/",methods=["GET"])
def fetch_last_clusters():
    detailed = request.args.get('detailed',default = 0, type = int)
    detailed_bool = bool(detailed)
    out = server.clusters_col.find_one(filter={},
                                       projection={CLUSTERS_COL_CLUSTERING_STATE_DICT:0},
                                       sort=[(f'{CLUSTERS_COL_SNAPSHOT}.{CLUSTERS_COL_SNAPSHOT_TIMESTAMP}',DESCENDING)])

    #filter out singlets:
    out[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_CLUSTERED_IDS] = list(filter(lambda x: len(x)>1,out[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_CLUSTERED_IDS]))

    if detailed:
        return ''
    else:
        out[CLUSTERS_COL_SNAPSHOT_CLUSTERS_INFO] = [{'meme_ids': x} for x in out[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_CLUSTERED_IDS]]
        del out[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_CLUSTERED_IDS]

        n_clusters = len(out[CLUSTERS_COL_SNAPSHOT_CLUSTERS_INFO])
        for i in range(n_clusters):
            cluster_info = out[CLUSTERS_COL_SNAPSHOT_CLUSTERS_INFO][i]
            meme_ids = cluster_info['meme_ids']
            output = server.memes_col.find(filter = {MEMES_COL_ID: {'$in':meme_ids}})
            memes = []
            for meme in output:
                memes.append(meme)

            image_urls = [meme[MEMES_COL_IMAGE_URL] for meme in memes if meme[MEMES_COL_FEAT_VEC]]
            example_image_url = None
            if len(image_urls)>0:
                example_image_url = image_urls[0]

            cluster_info['example_image_url'] = image_urls
            cluster_info['total_upvotes'] = sum([meme[MEMES_COL_UPVOTES] for meme in memes])
            cluster_info['total_comments'] = sum([meme[MEMES_COL_COMMENTS] for meme in memes])
            cluster_info['num_memes'] = len(memes)


        return parse_json(out)

#

if __name__ == '__main__':
    app.run(debug = False, host='0.0.0.0', port = 8000)


