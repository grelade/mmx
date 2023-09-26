import numpy as np
# import os
from tqdm import tqdm
# from pymongo import MongoClient
# from pymongo.server_api import ServerApi
# from pymongo.errors import BulkWriteError, ConnectionFailure
from typing import Union, Dict, List, Tuple
# from urllib.parse import urlparse

from .base import mmx_server
from .scraping import scraper_reddit
from .ml import feat_extract,denstream_clustering, hcluster_clustering
from .const import *
from .utils import hash_string, print_red, print_green

class mmx_server_scrape_embed_cluster(mmx_server):

    def __init__(self, mongodb_url: str, verbose: bool = False):
        super().__init__(mongodb_url = mongodb_url, verbose = verbose)

        self.scraping_module = scraper_reddit(verbose = verbose)
        self.feature_extracting_module = feat_extract(verbose = verbose)

        if CLUSTERING_MODEL == 'denstream':
            self._clustering_module_func = denstream_clustering
        elif CLUSTERING_MODEL == 'hcluster':
            self._clustering_module_func = hcluster_clustering
        self.clustering_module = self._clustering_module_func(verbose = verbose)

    # # general
    # def is_mongodb_active(self):
    #     try:
    #         if self.verbose: print('looking for mongo database...')
    #         # The ismaster command is cheap and does not require auth.
    #         self.smongodb.admin.command('ismaster')
    #         if self.verbose: print(f'Server at mongodb_url = {self.mongodb_url} found!')
    #         return True

    #     except ConnectionFailure:
    #         if self.verbose: print(f'NO server at mongodb_url = {self.mongodb_url}!')
    #         return False

    # @staticmethod
    # def _get_mongoclient(mongodb_url: str):
    #     def is_valid_url(url):
    #         try:
    #             result = urlparse(url)
    #             return all([result.scheme, result.netloc])
    #         except ValueError:
    #             return False

    #     if os.path.exists(mongodb_url):
    #         # path to file with url (used in docker secrets)
    #         with open(mongodb_url) as f: mongodb_url = f.readline().strip('\n')

    #     if is_valid_url(mongodb_url):
    #         if 'mongodb+srv' in mongodb_url:
    #             return MongoClient(mongodb_url, server_api=ServerApi('1'))
    #         else:
    #             return MongoClient(mongodb_url)
    #     else:
    #         if self.verbose: print(f'mongoclient({mongodb_url}): could not identify mongodb_url')

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
                                   CLUSTERS_COL_SNAPSHOT_HASH: hash_string(''),
                                   CLUSTERS_COL_CLUSTERED_IDS : None}

        init_denstream_state_dict = self._clustering_module_func().alg_func.state_dict_compressed()
        init_snapshot = {CLUSTERS_COL_SNAPSHOT: init_snapshot_info_dict,
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

    def _gen_features_array(self, meme_ids: List[str]) -> np.ndarray:
        '''
        generates features_array from meme_ids; used as decompressor_func in self.alg_func.load_state_dict_compressed.
        '''
        meme_ids = list(meme_ids)
        memes = self.memes_col.find({MEMES_COL_ID: {"$in": meme_ids}})

        features_array = []
        for meme in memes:
            meme = self._validate_meme(meme)
            features_array.append(meme[MEMES_COL_FEAT_VEC])
        features_array = np.array(features_array)

        return features_array

    def _is_clustering_snapshot_consistent(self, clustering_snapshot: Dict) -> bool:

        # first null snapshot is consistent by definition
        init_clustering_snapshot = self._get_init_clustering_snapshot()
        if clustering_snapshot == init_clustering_snapshot:
            return True

        snapshot = clustering_snapshot
        # snapshot_ntotal = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_NTOTAL]
        snapshot_hash = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
        snapshot_timestamp = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]

        timestamp_field = f'{CLUSTERS_COL_SNAPSHOT}.{CLUSTERS_COL_SNAPSHOT_TIMESTAMP}'
        sort_criterion = (timestamp_field, DESCENDING)
        result = self.clusters_col.find_one({timestamp_field : {'$lt': snapshot_timestamp}},sort=[sort_criterion])

        if result:
            prev_snapshot = result

        else:
            prev_snapshot = init_clustering_snapshot

        # prev_snapshot_ntotal = prev_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_NTOTAL]
        prev_snapshot_hash = prev_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
        prev_snapshot_timestamp = prev_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]

        memes = self._read_memes_between_timestamps(timestamp_min = prev_snapshot_timestamp, timestamp_max = snapshot_timestamp)
        string_repr = mmx_server_scrape_embed_cluster._form_string_repr(memes)

        if snapshot_hash != hash_string(prev_snapshot_hash + string_repr):
            return False

        return True

    def _find_last_consistent_first_inconsistent_clustering_snapshot(self) -> Tuple[Dict,Dict]:
        sort_criterion = (f'{CLUSTERS_COL_SNAPSHOT}.{CLUSTERS_COL_SNAPSHOT_TIMESTAMP}', ASCENDING)
        result = self.clusters_col.find({},sort=[sort_criterion])

        clustering_snapshots = [self._get_init_clustering_snapshot()]
        for r in result:
            clustering_snapshots.append(r)

        # no snapshots in db
        if len(clustering_snapshots) == 0:
            return self._get_init_clustering_snapshot(), None

        # find first inconsistent snapshot, if it exists
        clustering_snapshot_fi = None
        for ix in range(len(clustering_snapshots)):
            if not self._is_clustering_snapshot_consistent(clustering_snapshots[ix]):
                clustering_snapshot_fi = clustering_snapshots[ix]
                break
        if clustering_snapshot_fi:
            clustering_snapshot_fi = clustering_snapshots[ix]
            clustering_snapshot_lc = clustering_snapshots[ix-1]
        else:
            # no inconsistencies found
            clustering_snapshot_lc = clustering_snapshots[-1]

        return clustering_snapshot_lc, clustering_snapshot_fi

    def _find_last_consistent_first_inconsistent_clustering_snapshot_old(self) -> Tuple[Dict, Dict]:
        '''
        go through the snapshots and find the last consistent snapshot and first incosistent snapshot
        '''
        sort_criterion = (f'{CLUSTERS_COL_SNAPSHOT}.{CLUSTERS_COL_SNAPSHOT_TIMESTAMP}', ASCENDING)
        result = self.clusters_col.find({},sort=[sort_criterion])

        clustering_snapshots = []
        for r in result:
            clustering_snapshots.append(r)

        # no snapshots in db
        if len(clustering_snapshots) == 0:
            return self._get_init_clustering_snapshot(), None

        clustering_snapshots = [self._get_init_clustering_snapshot()] + clustering_snapshots

        prev_snapshot = None
        snapshot = None
        incosistency_found = False
        for ix in range(len(clustering_snapshots)):
            snapshot = clustering_snapshots[ix]
            # snapshot_ntotal = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_NTOTAL]
            snapshot_hash = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
            snapshot_timestamp = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]

            if ix == 0:
                continue
            else:
                prev_snapshot = clustering_snapshots[ix-1]
                # prev_snapshot_ntotal = prev_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_NTOTAL]
                prev_snapshot_hash = prev_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
                prev_snapshot_timestamp = prev_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]

            memes = self._read_memes_between_timestamps(timestamp_min = prev_snapshot_timestamp, timestamp_max = snapshot_timestamp)
            string_repr = mmx_server_scrape_embed_cluster._form_string_repr(memes)

            # if  snapshot_ntotal != prev_snapshot_ntotal + len(memes):
            #     if self.verbose: print('CLUSTERS_COL_SNAPSHOT_NTOTAL: inconsistency')
            #     incosistency_found = True
            #     break

            if snapshot_hash != hash_string(prev_snapshot_hash + string_repr):
                if self.verbose: print(f'CLUSTERS_COL_SNAPSHOT_HASH: inconsistent hash = {snapshot_hash}')
                incosistency_found = True
                break

        if incosistency_found:
            # clustering stack is inconsistent starting from clustering_spahost_fi
            clustering_snapshot_lc = prev_snapshot
            clustering_snapshot_fi = snapshot
        else:
            # clustering stack is fully consistent with data
            clustering_snapshot_lc = clustering_snapshots[-1]
            clustering_snapshot_fi = None

        return clustering_snapshot_lc, clustering_snapshot_fi

    def _remove_clustering_snapshots(self, clustering_snapshot_fi: Dict) -> bool:
        timestamp_fi = clustering_snapshot_fi[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]
        filter_criterion = {CLUSTERS_COL_SNAPSHOT+'.'+CLUSTERS_COL_SNAPSHOT_TIMESTAMP: {'$gte': timestamp_fi}}
        # result = self.clusters_col.find({},filter=filter_criterion)

        # snapshots_to_delete = []
        # for r in result:
        #     snapshots_to_delete.append(r)

        result = self.clusters_col.delete_many(filter_criterion)
        return result.acknowledged

    def _load_clustering_snapshot(self,clustering_snapshot: Dict) -> None:
        '''
        Load a clustering snapshot into the self.clustering_module.
        '''
        # clustering_snapshot = clustering_snapshot.copy()
        self.clustering_module.alg_func.load_state_dict_compressed(state_dict_compressed = clustering_snapshot[CLUSTERS_COL_CLUSTERING_STATE_DICT],
                                                             decompressor_func = self._gen_features_array)

    def _form_next_clustering_snapshot(self, new_data: List[Dict], previous_clustering_snapshot: Dict) -> Dict:
        '''
        Form a snapshot from the current state of the self.clustering_module,
        newly clustered data and the previous snapshot.
        '''
        new_timestamp = max([x[MEMES_COL_PUBL_TIMESTAMP] for x in new_data])
        new_ntotal = previous_clustering_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_NTOTAL] + len(new_data)
        hash_base = previous_clustering_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
        new_string_repr = mmx_server_scrape_embed_cluster._form_string_repr(new_data)
        new_hash = hash_string(hash_base + new_string_repr)
        new_clustered_ids = self.clustering_module.clusters
        new_snapshot_info_dict = {CLUSTERS_COL_SNAPSHOT_TIMESTAMP: new_timestamp,
                                    CLUSTERS_COL_SNAPSHOT_NTOTAL: new_ntotal,
                                    CLUSTERS_COL_SNAPSHOT_HASH: new_hash,
                                    CLUSTERS_COL_CLUSTERED_IDS: new_clustered_ids}
        new_clustering_state_dict = self.clustering_module.alg_func.state_dict_compressed()

        new_clustering_snapshot = {CLUSTERS_COL_SNAPSHOT: new_snapshot_info_dict,
                                    CLUSTERS_COL_CLUSTERING_STATE_DICT: new_clustering_state_dict}

        if self.verbose: print(f'new snapshot hash: {new_clustering_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]}')
        return new_clustering_snapshot

    @staticmethod
    def _form_string_repr(memes: List) -> str:
        '''
        form a string representation of memes dataset.
        To use in incremental hash data stream representation:
        hash_string(previous_hash + string_repr)
        '''
        str = ''.join([m[MEMES_COL_ID] for m in memes])
        return str

    def _plot_clustering_snapshots(self) -> None:
        sort_criterion = (f'{CLUSTERS_COL_SNAPSHOT}.{CLUSTERS_COL_SNAPSHOT_TIMESTAMP}', ASCENDING)
        result = self.clusters_col.find({},sort=[sort_criterion])

        clustering_snapshots = [self._get_init_clustering_snapshot()]
        for r in result:
            clustering_snapshots.append(r)

        print_func =  print_green
        for snapshot in clustering_snapshots:
            timestamp = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]
            hash = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
            ntotal = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_NTOTAL]
            is_consistent_flag = self._is_clustering_snapshot_consistent(snapshot)
            if not is_consistent_flag: print_func = print_red
            is_consistent = {True:'C',False:'I'}[is_consistent_flag]
            print_func(f'{is_consistent} | {timestamp:13d} | {ntotal:6d} | {hash}')


    # main functions
    def exec_meme_scraping_feat_extract_run(self) -> None:

        if self.verbose: print('='*100)

        for subreddit in SUBREDDITS:

            if self.verbose: print(f'scraping/feature-extraction from subreddit = {subreddit}')

            most_recent_memes_timestamp = self._read_most_recent_memes_timestamp_from_db(subreddit = subreddit)
            if self.verbose: print(f'most_recent_memes_timestamp = {most_recent_memes_timestamp}')

            # scraping part
            self.scraping_module.load_subreddit(subreddit = subreddit)
            memes = self.scraping_module.fetch_memes(end_at_timestamp = most_recent_memes_timestamp)
            memes = self._validate_memes(memes, send_to_db = True)

            # feature extraction
            if len(memes) > 0:
                if self.verbose: print('Extracting features...')
                for i in tqdm(range(len(memes))):
                    feature = self.feature_extracting_module.get_features_from_url(memes[i][MEMES_COL_IMAGE_URL])
                    memes[i][MEMES_COL_FEAT_VEC] = feature
                # image_urls = [meme[MEMES_COL_IMAGE_URL] for meme in memes]
                # features = self.feature_extracting_module.get_features_from_urls(image_urls)
                # memes[MEMES_COL_FEAT_VEC] = features

                self._write_memes_to_db(memes = memes)
            else:
                if self.verbose: print('No new memes; no feature extraction...')

            if self.verbose: print('-'*100)
        if self.verbose: print('='*100)

    def exec_clustering_run(self) -> None:

        if self.verbose: print('='*100)

        if self.verbose: print('START Clustering snapshots:')
        self._plot_clustering_snapshots()

        while True:
            # find last consistent and first inconsistent clustering snapshots
            clustering_snapshot_lc, clustering_snapshot_fi = self._find_last_consistent_first_inconsistent_clustering_snapshot()

            # deactivate/remove inconsistent snapshots starting from the first incosistent
            if clustering_snapshot_fi:
                print('incosistent snapshot',clustering_snapshot_fi[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH])
                success = self._remove_clustering_snapshots(clustering_snapshot_fi = clustering_snapshot_fi)
                if not success:
                    if self.verbose: print('could not remove incosistent clustering snapshots')

            # load the clustering from the last consistent snapshot

            self._load_clustering_snapshot(clustering_snapshot_lc)

            # load all memes not considered in the last consistent snapshot
            timestamp_min = clustering_snapshot_lc[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]
            timestamp_max = self._read_most_recent_memes_timestamp_from_db()
            new_memes = self._read_memes_between_timestamps(timestamp_min = timestamp_min, timestamp_max = timestamp_max)


            if CLUSTERING_BATCH_SIZE:
                new_memes = new_memes[:CLUSTERING_BATCH_SIZE]
                cluster_condition = len(new_memes) == CLUSTERING_BATCH_SIZE
            else:
                cluster_condition = len(new_memes) > 0

            if cluster_condition:
                # run clustering
                if self.verbose: print('Run clustering...')
                self.clustering_module.append_data(new_memes)
                self.clustering_module.form_clusters()

                # save the results as a snapshot
                new_clustering_snapshot = self._form_next_clustering_snapshot(new_data = new_memes,
                                                                            previous_clustering_snapshot = clustering_snapshot_lc)
                self._write_clustering_snapshot_to_db(clustering_snapshot = new_clustering_snapshot)

            else:
                if self.verbose: print('No new data; no need to run clustering')
                break

        if self.verbose: print('FINISH Clustering snapshots:')
        self._plot_clustering_snapshots()

        if self.verbose: print('='*100)
