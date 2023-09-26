import os
from typing import Union, Dict, List, Tuple
import numpy as np

from urllib.parse import urlparse
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import BulkWriteError, ConnectionFailure

from .const import *
from .utils import hash_string, print_red, print_green

class clusters_col_handler:
    pass

class memes_col_handler:
    pass

class mmx_server:

    def __init__(self, mongodb_url: str, verbose: bool = True):
        self.verbose = verbose
        self.mongodb_url = mongodb_url
        self.mongodb = mmx_server._get_mongoclient(self.mongodb_url)
        self.memes_col = self.mongodb[MAIN_DB][MEMES_COLLECTION]
        self.clusters_col = self.mongodb[MAIN_DB][CLUSTERS_COLLECTION]

    # db related
    def is_mongodb_active(self) -> bool:
        try:
            if self.verbose: print('looking for mongo database...')
            # The ismaster command is cheap and does not require auth.
            self.mongodb.admin.command('ismaster')
            if self.verbose: print(f'Server at mongodb_url = {self.mongodb_url} found!')
            return True

        except ConnectionFailure:
            if self.verbose: print(f'NO server at mongodb_url = {self.mongodb_url}!')
            return False
    # todo
    def is_ssl_active(self) -> bool:
        return False

    @staticmethod
    def _get_mongoclient(mongodb_url: str):
        def is_valid_url(url):
            try:
                result = urlparse(url)
                return all([result.scheme, result.netloc])
            except ValueError:
                return False

        if os.path.exists(mongodb_url):
            # path to file with url (used in docker secrets)
            with open(mongodb_url) as f: mongodb_url = f.readline().strip('\n')

        if is_valid_url(mongodb_url):
            if 'mongodb+srv' in mongodb_url:
                return MongoClient(mongodb_url, server_api=ServerApi('1'))
            else:
                return MongoClient(mongodb_url)
        else:
            if self.verbose: print(f'mongoclient({mongodb_url}): could not identify mongodb_url')
            return None

    # memes
    def _write_memes_to_db(self, memes: List[Dict]) -> bool:
        if self.verbose: print('_write_memes_to_db')

        # do nothing when no memes to write
        if len(memes)==0:
            return True

        try:
            memes = self._validate_memes(memes, send_to_db = True)
            result = self.memes_col.insert_many(memes)
            return result.acknowledged
        except BulkWriteError as e:
            if self.verbose: print('error',e)
            return False
    # todo
    def _read_memes_from_db(self) -> List:
        pass

    def _validate_meme(self, meme: Dict, send_to_db: bool = False) -> Dict:
        '''
        ensure memes extracted from mongodb are in the correct format used in the mmx_server.
        if send_to_db = True, validate meme record to fit the mongodb format instead.
        '''
        keys = [MEMES_COL_ID,MEMES_COL_IMAGE_URL,MEMES_COL_TITLE,MEMES_COL_UPVOTES,MEMES_COL_COMMENTS,MEMES_COL_PUBL_TIMESTAMP,MEMES_COL_SUBREDDIT]

        # msg = ''
        # for key in keys+[MEMES_COL_FEAT_VEC]:
        #     if key in meme.keys():
        #         msg+=f'{key}, {type(meme[key])} '
        # print(msg)

        meme = meme.copy()
        # ensure no lists are in the record (besides feat_vec)

        for key in keys:
            if key in meme.keys():
                if isinstance(meme[key],list):
                    meme[key] = meme[key][0]

        # ensure correct types are passed on
        if MEMES_COL_ID in meme.keys():
            if not isinstance(meme[MEMES_COL_ID],str):
                meme[MEMES_COL_ID] = str(meme[MEMES_COL_ID])

        if MEMES_COL_IMAGE_URL in meme.keys():
            if not isinstance(meme[MEMES_COL_IMAGE_URL],str):
                meme[MEMES_COL_IMAGE_URL] = str(meme[MEMES_COL_IMAGE_URL])

        if MEMES_COL_TITLE in meme.keys():
            if not isinstance(meme[MEMES_COL_TITLE],str):
                meme[MEMES_COL_TITLE] = str(meme[MEMES_COL_TITLE])

        if MEMES_COL_UPVOTES in meme.keys():
            if not isinstance(meme[MEMES_COL_UPVOTES],int):
                meme[MEMES_COL_UPVOTES] = int(meme[MEMES_COL_UPVOTES])

        if MEMES_COL_COMMENTS in meme.keys():
            if not isinstance(meme[MEMES_COL_COMMENTS],int):
                meme[MEMES_COL_COMMENTS] = int(meme[MEMES_COL_COMMENTS])

        if MEMES_COL_PUBL_TIMESTAMP in meme.keys():
            if not isinstance(meme[MEMES_COL_PUBL_TIMESTAMP],int):
                meme[MEMES_COL_PUBL_TIMESTAMP] = int(meme[MEMES_COL_PUBL_TIMESTAMP])

        if MEMES_COL_SUBREDDIT in meme.keys():
            if not isinstance(meme[MEMES_COL_SUBREDDIT],str):
                meme[MEMES_COL_SUBREDDIT] = str(meme[MEMES_COL_SUBREDDIT])

        if send_to_db:
            # mongodb does not accept np.ndarrays
            if MEMES_COL_FEAT_VEC in meme.keys():
                if isinstance(meme[MEMES_COL_FEAT_VEC],np.ndarray):
                    meme[MEMES_COL_FEAT_VEC] = meme[MEMES_COL_FEAT_VEC].reshape(-1)
                    meme[MEMES_COL_FEAT_VEC] = meme[MEMES_COL_FEAT_VEC].tolist()
        else:
            # mmx_server works on np.ndarrays
            if MEMES_COL_FEAT_VEC in meme.keys():
                if isinstance(meme[MEMES_COL_FEAT_VEC],list):
                    meme[MEMES_COL_FEAT_VEC] = np.array(meme[MEMES_COL_FEAT_VEC])

        # msg = ''
        # for key in keys+[MEMES_COL_FEAT_VEC]:
        #     if key in meme.keys():
        #         msg+=f'{key}, {type(meme[key])} '
        # print(msg)

        return meme

    def _validate_memes(self, memes: List, send_to_db: bool = False) -> List:
        '''
        ensure memes extracted from and put into mongodb are in the mmx_server format.
        if send_to_db = True, validate meme record to fit the mongodb format instead.
        '''
        for i in range(len(memes)):
            memes[i] = self._validate_meme(memes[i], send_to_db = send_to_db)
        return memes

    def _read_memes_between_timestamps(self, timestamp_min: int, timestamp_max: int) -> List:
        '''
        reads all memes between timestamps: ( timestamp_min, timestamp_max ]
        '''
        result = self.memes_col.find({MEMES_COL_PUBL_TIMESTAMP: {'$gt': timestamp_min,'$lte': timestamp_max},
                                      MEMES_COL_FEAT_VEC: {"$ne": None}})
        result = result.sort([(MEMES_COL_PUBL_TIMESTAMP, ASCENDING)])
        memes_subset = []
        for meme in result:
            memes_subset.append(meme)

        memes_subset = self._validate_memes(memes_subset)
        return memes_subset

    def _read_most_recent_memes_timestamp_from_db(self, subreddit: str = None) -> int:
        '''
        read timestamp of the most recent scraped meme for a particular subreddit.
        If subreddit = None, will look for a global timestamp.
        '''
        filter_dict = {}
        if subreddit:
            filter_dict = {MEMES_COL_SUBREDDIT: subreddit}

        meme = self.memes_col.find_one(filter_dict,
                                         sort=[(MEMES_COL_PUBL_TIMESTAMP, DESCENDING)])

        if meme:
            meme = self._validate_meme(meme)
            timestamp = meme[MEMES_COL_PUBL_TIMESTAMP]
        else:
            timestamp = 0

        return timestamp


    # clustering snapshots
    def _get_init_clustering_snapshot(self) -> Dict:
        init_snapshot_info_dict = {CLUSTERS_COL_SNAPSHOT_TIMESTAMP: 0,
                                   CLUSTERS_COL_SNAPSHOT_NTOTAL: 0,
                                   CLUSTERS_COL_SNAPSHOT_HASH: hash_string('')}

        init_clusters_info_list = [{CLUSTERS_COL_INFO_EXAMPLE_IMAGE: None,
                                   CLUSTERS_COL_INFO_IDS: None,
                                   CLUSTERS_COL_INFO_NMEMES: 0,
                                   CLUSTERS_COL_INFO_TOTAL_COMMENTS: 0,
                                   CLUSTERS_COL_INFO_TOTAL_UPVOTES: 0}]

        init_denstream_state_dict = self._clustering_module_func().alg_func.state_dict_compressed()

        init_snapshot = {CLUSTERS_COL_SNAPSHOT: init_snapshot_info_dict,
                         CLUSTERS_COL_INFO: init_clusters_info_list,
                         CLUSTERS_COL_CLUSTERING_STATE_DICT: init_denstream_state_dict}

        return init_snapshot

    def _write_clustering_snapshot_to_db(self, clustering_snapshot: Dict) -> bool:
        '''
        write clustering snapshot consisting of general snapshot information in snapshot_info_dict,
        , and the denstream clustering model in denstream_state_dict
        '''
        if self.verbose: print('_write_clustering_snapshot_to_db')

        # clustering_snapshot = self._encode_clustering_snapshot(clustering_snapshot)

        try:
            result = self.clusters_col.insert_one(clustering_snapshot)
            return result.acknowledged
        except BulkWriteError as e:
            if self.verbose: print('error',e)
            return False

    def _remove_clustering_snapshots(self, clustering_snapshot_fi: Dict) -> bool:
        timestamp_fi = clustering_snapshot_fi[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]
        filter_criterion = {CLUSTERS_COL_SNAPSHOT+'.'+CLUSTERS_COL_SNAPSHOT_TIMESTAMP: {'$gte': timestamp_fi}}
        # result = self.clusters_col.find({},filter=filter_criterion)

        # snapshots_to_delete = []
        # for r in result:
        #     snapshots_to_delete.append(r)

        result = self.clusters_col.delete_many(filter_criterion)
        return result.acknowledged

    def _plot_clustering_snapshots(self) -> None:
        sort_criterion = (f'{CLUSTERS_COL_SNAPSHOT}.{CLUSTERS_COL_SNAPSHOT_TIMESTAMP}', ASCENDING)
        result = self.clusters_col.find({},sort=[sort_criterion])

        clustering_snapshots = [self._get_init_clustering_snapshot()]
        for r in result:
            clustering_snapshots.append(r)

        print_func =  print_green
        for snapshot in clustering_snapshots:
            snapshot_ = snapshot[CLUSTERS_COL_SNAPSHOT]
            timestamp = snapshot_[CLUSTERS_COL_SNAPSHOT_TIMESTAMP]
            hash_ = snapshot_[CLUSTERS_COL_SNAPSHOT_HASH]
            ntotal = snapshot_[CLUSTERS_COL_SNAPSHOT_NTOTAL]
            is_consistent_flag = self._is_clustering_snapshot_consistent(snapshot)
            if not is_consistent_flag: print_func = print_red
            is_consistent = {True:'C',False:'I'}[is_consistent_flag]
            print_func(f'{is_consistent} | {timestamp:13d} | {ntotal:6d} | {hash_}')
