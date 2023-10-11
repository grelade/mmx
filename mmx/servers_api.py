from flask_classful import FlaskView, route
from flask import request
from typing import Union, Dict, List, Tuple
from datetime import datetime, timedelta
import bson
import scipy.stats
import numpy as np

from .servers_core import mmx_server
from .const import *
from .utils import parse_json




pick_nonnull_featvecs = {"$match":
                            {MEMES_COL_FEAT_VEC:
                            {"$ne": None}
                            }
                        }

fetch_most_recent_snapshot = {"$set":
                                {MEMES_COL_LAST_SNAPSHOT:
                                {"$last": f"${MEMES_COL_SNAPSHOT}"}
                                }
                                }

find_popularity_score = {'$set':
                            {MEMES_COL_POPULARITY_SCORE:
                            {"$add":
                            [f"${MEMES_COL_LAST_SNAPSHOT}.{MEMES_COL_SNAPSHOT_UPVOTES}",
                            {"$multiply":
                                [COMMENTS_TO_UPVOTES_FACTOR,
                                f"${MEMES_COL_LAST_SNAPSHOT}.{MEMES_COL_SNAPSHOT_COMMENTS}"
                                ]
                            }
                            ]
                            }
                            }
                        }

sort_by_popularity_score = lambda ord: {'$sort':
                            {MEMES_COL_POPULARITY_SCORE: ord}
                            }

sort_by_publ_timestamp = lambda ord: {'$sort':
                            {MEMES_COL_PUBL_TIMESTAMP: ord}
                            }

sort_by_comments = lambda ord: {'$sort':
                    {f"{MEMES_COL_LAST_SNAPSHOT}.{MEMES_COL_SNAPSHOT_COMMENTS}": ord}
                    }

sort_by_upvotes = lambda ord: {'$sort':
                    {f"{MEMES_COL_LAST_SNAPSHOT}.{MEMES_COL_SNAPSHOT_UPVOTES}": ord}
                    }

# /cluster
find_similar_memes = lambda feat_vec, k: {
        "$search": {
          "index": MEMES_COL_SEARCH_INDEX,
          "knnBeta": {
            "vector": feat_vec,
            "path": MEMES_COL_FEAT_VEC,
            "k": k
         }
        }
       }

fetch_search_score = {"$set": {MEMES_COL_SEARCH_SCORE: { '$meta': "searchScore"}}}
trim_search_score = lambda th: {"$match": {MEMES_COL_SEARCH_SCORE: {"$gte": th}}}

# /trends
unwind_snapshots = {"$unwind": {"path": f"${MEMES_COL_SNAPSHOT}"}}
trim_timestamps = lambda tmin: {'$match': {f'{MEMES_COL_SNAPSHOT}.{MEMES_COL_SNAPSHOT_TIMESTAMP}':{'$gte': tmin}}}

bucket_snapshots =  lambda timestamps: {'$bucket': {
         'groupBy': f"${MEMES_COL_SNAPSHOT}.{MEMES_COL_SNAPSHOT_TIMESTAMP}",
         'boundaries': timestamps,
         'output': {'count': {"$sum": 1},
                    "memes": {"$push": {MEMES_COL_ID: f"${MEMES_COL_ID}",
                                        MEMES_COL_SNAPSHOT_UPVOTES: f"${MEMES_COL_SNAPSHOT}.{MEMES_COL_SNAPSHOT_UPVOTES}",
                                        MEMES_COL_SNAPSHOT_COMMENTS: f"${MEMES_COL_SNAPSHOT}.{MEMES_COL_SNAPSHOT_COMMENTS}"}}
                    }
     }}

memes_group = {
    "$map": {
      "input": {
        "$setUnion": {
          "$map": {
            "input": "$memes",
            "in": f'$$this.{MEMES_COL_ID}'
          }
        }
      },
      "as": "unique_meme_id",
      "in": {
        MEMES_COL_ID: "$$unique_meme_id",
        "count": {
          "$size": {
            "$filter": {
              "input": '$memes',
              "cond": {
                "$eq": [f'$$this.{MEMES_COL_ID}', "$$unique_meme_id"]
              }
            }
          }
        },
        "upvotes_group": {
          "$reduce": {
            "input": '$memes',
            "initialValue": 0,
            "in": {
              "$cond": {
                "if": {"$eq": [f'$$this.{MEMES_COL_ID}', "$$unique_meme_id"]},
                "then": {"$add": [f'$$this.{MEMES_COL_SNAPSHOT_UPVOTES}', "$$value"]},
                "else": "$$value"
              }
            }
          }
        },
        "comments_group": {
          "$reduce": {
            "input": '$memes',
            "initialValue": 0,
            "in": {
              "$cond": {
                "if": {"$eq": [f'$$this.{MEMES_COL_ID}', "$$unique_meme_id"]},
                "then": {"$add": [f'$$this.{MEMES_COL_SNAPSHOT_COMMENTS}', "$$value"]},
                "else": "$$value"
              }
            }
          }
        }
      }
    }
  }

group_average_snapshots = [{"$set": {
    "memes_group": memes_group,
    }},
    {"$project": {
        "count": {"$size": "$memes_group"},
        "memes":
              {'$map': { 'input': '$memes_group',
               'as': 'meme_group',
               'in': {MEMES_COL_ID: f'$$meme_group.{MEMES_COL_ID}',
                    #   'group_count': '$$meme_group.count',
                      f'{MEMES_COL_SNAPSHOT_UPVOTES}': {'$divide': ['$$meme_group.upvotes_group','$$meme_group.count']},
                      f'{MEMES_COL_SNAPSHOT_COMMENTS}': {'$divide': ['$$meme_group.comments_group','$$meme_group.count']}}
    }
    }}}]

densify_snapshots = lambda tmin,tmax,dt: [{ '$densify': {
    'field': "_id",
    'range': { 'step': dt, 'bounds': [tmin,tmax] }}},
    { '$set': { 'count': { '$cond': [ { '$not': ["$count"] }, 0, "$count" ] } } }]

calc_total_snapshots = {'$project': {'count': '$count',
                                     'total_comments': {'$sum': '$memes.comments'},
                                     'total_upvotes': {'$sum': '$memes.upvotes'}}
                                     }


skip = lambda i: {'$skip': i}
limit = lambda i: {'$limit': i}

drop = lambda field: {'$unset': field}



# class mmx_server_api(mmx_server):
#     def __init__(self, mongodb_url: str, verbose: bool = False):
#         super().__init__(mongodb_url = mongodb_url, verbose = verbose)

class info_view(FlaskView):
    route_prefix = API_V1_BASE_URL
    route_base = '/'

    def index(self):
        info = 'mmx API server<br>'
        info += 'endpoints:<br>'
        info += f'<b>{API_V1_BASE_URL}/memes/</b> - fetch all memes (paginated), sorted in descending order by popularity<br>'
        info += f'<b>{API_V1_BASE_URL}/memes/?by=(publ_ts,upvotes,comments,popularity)</b> - fetch all memes (paginated), sorted by publ_timestamp, num of upvotes, num of comments or popularity score = upvotes + 50*comments<br>'
        info += f'<b>{API_V1_BASE_URL}/memes/?sort=(asc,desc)</b> - fetch all memes (paginated), ascending, descending order<br>'
        info += f'<b>{API_V1_BASE_URL}/memes/[meme_id]</b> - fetch a single meme with [meme_id]<br>'
        info += f'<b>{API_V1_BASE_URL}/memes/[meme_id]/cluster</b> - fetch memes similar to meme with [meme_id]<br>'
        info += f'<b>{API_V1_BASE_URL}/memes/[meme_id]/trend</b> - establish a trend for meme [meme_id]<br>'
        # info += f'<b>{API_V1_BASE_URL}/clusters/</b> - fetch newest clusters<br>'
        # info += f'[NOT WORKING] <b>{API_V1_BASE_URL}/clusters/?detailed=1</b> - fetch newest clusters, detailed version<br>'
        return info

class memes_view(FlaskView):
    route_prefix = API_V1_BASE_URL
    route_base = '/memes/'

    def __init__(self, mmx_server):
        self.mmx_server = mmx_server

    @route('/',methods=["GET"])
    def fetch_all_memes(self):
        id_sort = request.args.get('sort',default='desc',type = str)
        page = request.args.get('page',default = 1, type = int)
        by = request.args.get('by',default='popularity',type = str)

        id_sort_mongo = {'asc' : ASCENDING,
                         'desc' : DESCENDING }[id_sort]

        agg = []
        agg.append(pick_nonnull_featvecs)
        agg.append(fetch_most_recent_snapshot)

        if by == 'publ_ts':
            agg.append(sort_by_publ_timestamp(ord = id_sort_mongo))
        elif by == 'upvotes':
            agg.append(sort_by_upvotes(ord = id_sort_mongo))
        elif by == 'comments':
            agg.append(sort_by_comments(ord = id_sort_mongo))
        elif by == 'popularity':
            agg.append(find_popularity_score)
            agg.append(sort_by_popularity_score(ord = id_sort_mongo))
        else:
            agg.append(find_popularity_score)
            agg.append(sort_by_popularity_score(ord = id_sort_mongo))

        agg.append(drop(MEMES_COL_FEAT_VEC))
        agg.append(skip(API_PAGE_LIMIT * (page - 1)))
        agg.append(limit(API_PAGE_LIMIT))

        memes_count = self.mmx_server.memes_col.count_documents({})
        memes = list(self.mmx_server.memes_col.aggregate(agg, allowDiskUse=True))

        if page*API_PAGE_LIMIT < memes_count:
            next_url = f"{API_V1_BASE_URL}/memes/?page={page+1}&sort={id_sort}&by={by}"
        else:
            next_url = None

        return {API_NEXT_URL : next_url,
                MEMES_COLLECTION : parse_json(memes)}


    # fetch single meme
    @route("/<meme_id>",methods=["GET"])
    def fetch_meme(self,meme_id: str):

        projection = {}
        # projection = {MEMES_COL_FEAT_VEC:0}
        meme = self.mmx_server.memes_col.find_one(filter={MEMES_COL_ID:meme_id},
                                                  projection=projection)
        return parse_json(meme)

    @route("/<meme_id>/cluster",methods=["GET"])
    def fetch_similar_memes(self, meme_id: str):

        projection = {'_id':0, MEMES_COL_FEAT_VEC:1}
        meme = self.mmx_server.memes_col.find_one(filter={MEMES_COL_ID: meme_id},
                                                  projection=projection)
        feat_vec = meme[MEMES_COL_FEAT_VEC]

        agg = []
        agg.append(find_similar_memes(feat_vec,k=MEMES_COL_SEARCH_LIMIT))
        agg.append(fetch_search_score)
        agg.append(trim_search_score(MEMES_COL_SEARCH_THRESHOLD))
        agg.append(drop(MEMES_COL_FEAT_VEC))
        agg.append(fetch_most_recent_snapshot)
        agg.append(find_popularity_score)
        agg.append(sort_by_popularity_score(ord = DESCENDING))
        agg.append(drop(MEMES_COL_FEAT_VEC))
        out = self.mmx_server.memes_col.aggregate(agg)

        memes = []
        for o in out:
            memes.append(o)

        return {MEMES_COLLECTION : parse_json(memes)}

    @route("/<meme_id>/trend", methods=["GET"])
    def fetch_meme_trend(self, meme_id: str):
        projection = {'_id':0, MEMES_COL_FEAT_VEC:1}
        meme = self.mmx_server.memes_col.find_one(filter={MEMES_COL_ID: meme_id},
                                                  projection=projection)
        feat_vec = meme[MEMES_COL_FEAT_VEC]

        # form timestamp bins
        dt = timedelta(minutes=TREND_SNAPSHOT_BIN_WIDTH)
        t0 = datetime.now()
        ts = [t0]
        for i in range(TREND_SNAPSHOT_NUM_BINS):
            ts.append(ts[-1]-dt)

        ts = ts[::-1]
        timestamps = list(map(lambda x: int(x.timestamp()*1000),ts))
        dt = bson.int64.Int64(timestamps[1]-timestamps[0])
        tmin,tmax = bson.int64.Int64(timestamps[0]), bson.int64.Int64(timestamps[-1])

        agg = []
        agg.append(find_similar_memes(feat_vec,k=MEMES_COL_SEARCH_LIMIT))
        agg.append(fetch_search_score)
        agg.append(trim_search_score(MEMES_COL_SEARCH_THRESHOLD))
        agg.append(unwind_snapshots)
        agg.append(trim_timestamps(tmin = timestamps[0])) # remove snapshots with timestamps < tmin
        agg.append(bucket_snapshots(timestamps)) # bin snapshots into timestamps
        agg+=group_average_snapshots # take inter-meme group averages over snapshots to not overcount the upvotes/comments
        agg+=densify_snapshots(tmin,tmax,dt) # include empty buckets (where no snapshots were taken)
        agg.append(calc_total_snapshots) # calculate total bucketed snapshot impact

        out = self.mmx_server.memes_col.aggregate(agg)

        snaps = []
        for o in out:
            # print(o)
            snaps.append(o)
        # print(snaps)
        # return {}

        # find the trend
        upvotes_nonzero = []
        comments_nonzero = []
        ts_nonzero = []
        for tlow,thigh in zip(timestamps[:-1],timestamps[1:]):
            for snap in snaps:
                if snap['_id'] == tlow:
                    if snap['count']>0:
                        ts_nonzero.append((thigh+tlow)/2)
                        upvotes_nonzero.append(snap['total_upvotes'])
                        comments_nonzero.append(snap['total_comments'])
                        break

        upvotes_nonzero,comments_nonzero,ts_nonzero = np.array(upvotes_nonzero),np.array(comments_nonzero),np.array(ts_nonzero)

        lreg = scipy.stats.linregress(ts_nonzero,upvotes_nonzero + COMMENTS_TO_UPVOTES_FACTOR*comments_nonzero)
        da = lreg.stderr
        a = lreg.slope

        trend_thresholds = np.array([a-2*da,a-da,a+da,a+2*da])
        n_positive = sum(trend_thresholds>=0) # establishing trend strength
        # print(n_positive,a,da)
        if n_positive == 0:
            trend = TREND_STRONG_DECREASE
        elif n_positive == 1:
            trend = TREND_WEAK_DECREASE
        elif n_positive == 2:
            trend = TREND_NO_CHANGE
        elif n_positive == 3:
            trend = TREND_WEAK_INCREASE
        elif n_positive == 4:
            trend = TREND_STRONG_INCREASE

        return {MEMES_COL_ID: meme_id,
                'trend': trend,
                'timestamps':list(ts_nonzero),
                'total_upvotes':list(upvotes_nonzero),
                'total_comments': list(comments_nonzero)}
