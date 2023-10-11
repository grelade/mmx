import os
from typing import Union, Dict, List, Tuple
import numpy as np

from urllib.parse import urlparse
from pymongo import MongoClient
from pymongo import IndexModel, ASCENDING, DESCENDING
from pymongo.server_api import ServerApi
from pymongo.errors import BulkWriteError, ConnectionFailure

from .const import *
from .utils import print_red, print_green

class mmx_server:

    def __init__(self, mongodb_url: str, verbose: bool = True):
        self.verbose = verbose
        self.mongodb_url = mongodb_url
        self.mongodb = mmx_server._get_mongoclient(self.mongodb_url)
        self.memes_col = self.mongodb[MAIN_DB][MEMES_COLLECTION]
        self.prepare_db()

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
            with open(mongodb_url) as f:
                mongodb_url = f.readline().strip('\n')
                # print(mongodb_url)

        if is_valid_url(mongodb_url):
            if 'mongodb+srv' in mongodb_url:
                return MongoClient(mongodb_url, server_api=ServerApi('1'))
            else:
                return MongoClient(mongodb_url)
        else:
            if self.verbose: print(f'mongoclient({mongodb_url}): could not identify mongodb_url')
            return None

    def prepare_db(self):

        # create basic index in memes
        if self.memes_col.count_documents({})==0:
            print(f'new/empty "{MEMES_COLLECTION}" collection detected')

        ix_info = self.memes_col.index_information()

        indices = []
        if 'meme_id_index' not in ix_info.keys():
            ix = IndexModel([("meme_id",DESCENDING)],name="meme_id_index",unique=True)
            indices.append(ix)

        if len(indices)>0:
            print(f'creating meme_id_index in "{MEMES_COLLECTION}" collection')
            self.memes_col.create_indexes(indices)

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
        keys = [MEMES_COL_ID,MEMES_COL_IMAGE_URL,MEMES_COL_TITLE,MEMES_COL_SNAPSHOT,MEMES_COL_PUBL_TIMESTAMP,MEMES_COL_SUBREDDIT]
        # snapshot_subkeys = [MEMES_COL_SNAPSHOT_COMMENTS,MEMES_COL_SNAPSHOT_TIMESTAMP,MEMES_COL_SNAPSHOT_UPVOTES]

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

        # if MEMES_COL_IMAGE_URL in meme.keys():
        #     if MEMES_COL_IMAGE_URL_SOURCE in meme[MEMES_COL_IMAGE_URL].keys():
        #         if not isinstance(meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_SOURCE],str):
        #             meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_SOURCE] = str(meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_SOURCE])
        #     if MEMES_COL_IMAGE_URL_LOCAL in meme[MEMES_COL_IMAGE_URL].keys():
        #         if not isinstance(meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_LOCAL],str):
        #             meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_LOCAL] = str(meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_LOCAL])
        #     if MEMES_COL_IMAGE_URL_ALTER in meme[MEMES_COL_IMAGE_URL].keys():
        #         if not isinstance(meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_ALTER],str):
        #             meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_ALTER] = str(meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_ALTER])

        if MEMES_COL_TITLE in meme.keys():
            if not isinstance(meme[MEMES_COL_TITLE],str):
                meme[MEMES_COL_TITLE] = str(meme[MEMES_COL_TITLE])

        if MEMES_COL_SNAPSHOT in meme.keys():
            if MEMES_COL_SNAPSHOT_COMMENTS in meme[MEMES_COL_SNAPSHOT].keys():
                if not isinstance(meme[MEMES_COL_SNAPSHOT][MEMES_COL_SNAPSHOT_COMMENTS],int):
                    meme[MEMES_COL_SNAPSHOT][MEMES_COL_SNAPSHOT_COMMENTS] = int(meme[MEMES_COL_SNAPSHOT][MEMES_COL_SNAPSHOT_COMMENTS])
            if MEMES_COL_SNAPSHOT_UPVOTES in meme[MEMES_COL_SNAPSHOT].keys():
                if not isinstance(meme[MEMES_COL_SNAPSHOT][MEMES_COL_SNAPSHOT_UPVOTES],int):
                    meme[MEMES_COL_SNAPSHOT][MEMES_COL_SNAPSHOT_UPVOTES] = int(meme[MEMES_COL_SNAPSHOT][MEMES_COL_SNAPSHOT_UPVOTES])
            if MEMES_COL_SNAPSHOT_TIMESTAMP in meme[MEMES_COL_SNAPSHOT].keys():
                if not isinstance(meme[MEMES_COL_SNAPSHOT][MEMES_COL_SNAPSHOT_TIMESTAMP],int):
                    meme[MEMES_COL_SNAPSHOT][MEMES_COL_SNAPSHOT_TIMESTAMP] = int(meme[MEMES_COL_SNAPSHOT][MEMES_COL_SNAPSHOT_TIMESTAMP])

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
