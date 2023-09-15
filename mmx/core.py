import numpy as np
from tqdm import tqdm
# from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.errors import BulkWriteError
from typing import Union, Dict, List, Tuple

from .scraping import scraper_reddit
from .ml import feat_extract,denstream_clustering
from .const import *
from .utils import hash_string

class mmx_server:

    def __init__(self, verbose = False):
        self.scraping_module = scraper_reddit(verbose = verbose)
        self.feature_extracting_module = feat_extract(model = FEAT_EXTRACT_MODEL, verbose = verbose)
        self.clustering_module = denstream_clustering(verbose = verbose)
        self.mongodb = MongoClient(MONGODB_URL)
        self.memes_col = self.mongodb[MAIN_DB][MEMES_COLLECTION]
        self.clusters_col = self.mongodb[MAIN_DB][CLUSTERS_COLLECTION]
        # self.snapshots_col = self.mongodb[MAIN_DB][SNAPSHOTS_COLLECTION]

        self.verbose = verbose


    # memes
    @staticmethod
    def _convert_data_dict_to_db_list(data_dict: Dict) -> List:
        '''
        convert memes data dictionary returned by the self.scraping_module to a mongodb-friendly list of records
        '''
        keys = data_dict.keys()
        arr = [data_dict[k] for k in keys]
        db_list = []
        for values in zip(*arr):
            rec = dict()
            for k,v in zip(keys,values):
                if isinstance(v,np.int64):
                    v = int(v)
                elif isinstance(v,np.ndarray):
                    v = v.tolist()
                rec[k] = v
            db_list.append(rec)

        return db_list

    def _write_memes_to_db(self,memes: Union[Dict,List]) -> bool:
        if self.verbose: print('_write_memes_to_db')
        if isinstance(memes,Dict):
            memes = mmx_server._convert_data_dict_to_db_list(memes)

        # do nothing when no memes to write
        if len(memes)==0:
            return True

        try:
            result = self.memes_col.insert_many(memes)
            return result.acknowledged
        except BulkWriteError as e:
            if self.verbose: print('error',e)
            return False
    # todo
    def _read_memes_from_db(self) -> List:
        pass

    def _read_memes_between_timestamps(self, timestamp_min: int, timestamp_max: int) -> List:
        '''
        reads all memes between timestamps: ( timestamp_min, timestamp_max ]
        '''
        result = self.memes_col.find({MEMES_COL_PUBL_TIMESTAMP: {'$gt': timestamp_min,'$lte': timestamp_max}})
        result = result.sort([(MEMES_COL_PUBL_TIMESTAMP, ASCENDING)])
        memes_subset = []
        for r in result:
            memes_subset.append(r)

        return memes_subset

    # timestamps
    def _read_most_recent_memes_timestamp_from_db(self, subreddit: str = None) -> int:
        '''
        read timestamp of the most recent scraped meme for a particular subreddit.
        If subreddit = None, will look for a global timestamp.
        '''
        filter_dict = {}
        if subreddit:
            filter_dict = {MEMES_COL_SUBREDDIT: subreddit}

        result = self.memes_col.find_one(filter_dict,
                                         sort=[(MEMES_COL_PUBL_TIMESTAMP, DESCENDING)])

        if result:
            timestamp = int(result[MEMES_COL_PUBL_TIMESTAMP])
        else:
            timestamp = 0

        return timestamp

    def _read_most_recent_clustering_timestamp_from_db(self) -> int:
        '''
        read timestamp of the most recent self.clustering_module snapshot.
        '''
        result = self.clusters_col.find_one(sort=[('current_time', DESCENDING)])
        if result:
            timestamp = int(result['current_time'])
        else:
            timestamp = 0

        return timestamp


    # clusters
    def _get_init_clustering_snapshot(self) -> Dict:
        init_snapshot_info_dict = {CLUSTERS_COL_SNAPSHOT_TIMESTAMP: 0,
                                   CLUSTERS_COL_SNAPSHOT_NTOTAL: 0,
                                   CLUSTERS_COL_SNAPSHOT_HASH: hash_string('')}
        init_denstream_state_dict = denstream_clustering().ds.state_dict()
        init_snapshot = {CLUSTERS_COL_SNAPSHOT: init_snapshot_info_dict,
                         CLUSTERS_COL_DENSTREAM_STATE_DICT: init_denstream_state_dict}
        return init_snapshot

    def _write_clustering_snapshot_to_db(self, clustering_snapshot: Dict) -> bool:
        '''
        write clustering snapshot consisting of general snapshot information in snapshot_info_dict,
        , and the denstream clustering model in denstream_state_dict
        '''
        if self.verbose: print('_write_clustering_snapshot_to_db')

        clustering_snapshot = self._encode_clustering_snapshot(clustering_snapshot)

        try:
            result = self.clusters_col.insert_one(clustering_snapshot)
            return result.acknowledged
        except BulkWriteError as e:
            if self.verbose: print('error',e)
            return False

    def _compress_denstream_state_dict(self, denstream_state_dict: Dict) -> Dict:
        for keys in ['o_micro_clusters','p_micro_clusters','completed_o_clusters','completed_p_clusters']:
            for mc in denstream_state_dict[keys]:
                del mc['features_array']
                mc['time_array'] = mc['time_array'].reshape(-1).tolist()
                mc['labels_array'] = mc['labels_array'].tolist()
                mc['id_array'] = mc['id_array'].tolist()
                mc['weight'] = mc['weight'].tolist()
                mc['center'] = mc['center'].reshape(-1).tolist()

        return denstream_state_dict

    def _decompress_denstream_state_dict(self, denstream_state_dict: Dict) -> Dict:

        def gen_features_array(ids: List) -> np.ndarray:
            lids = list(ids)
            result = self.memes_col.find({MEMES_COL_ID: {"$in": lids}})
            features_array = []
            for r in result:
                features_array.append(r['feat_vec'])
            features_array = np.array(features_array)

            return features_array

        for keys in ['o_micro_clusters','p_micro_clusters','completed_o_clusters','completed_p_clusters']:
            for mc in denstream_state_dict[keys]:
                mc['features_array'] = gen_features_array(mc['id_array'])
                mc['time_array'] = np.array(mc['time_array']).reshape(-1,1)
                mc['labels_array'] = np.array(mc['labels_array'])
                mc['id_array'] = np.array(mc['id_array'])
                mc['weight'] = np.array(mc['weight'])
                mc['center'] = np.array(mc['center']).reshape(-1,1)

        return denstream_state_dict

    def _encode_clustering_snapshot(self,clustering_snaphot: Dict) -> Dict:
        clustering_snaphot[CLUSTERS_COL_DENSTREAM_STATE_DICT] = self._compress_denstream_state_dict(clustering_snaphot[CLUSTERS_COL_DENSTREAM_STATE_DICT])
        return clustering_snaphot

    def _decode_clustering_snapshot(self,clustering_snaphot: Dict) -> Dict:
        clustering_snaphot[CLUSTERS_COL_DENSTREAM_STATE_DICT] = self._decompress_denstream_state_dict(clustering_snaphot[CLUSTERS_COL_DENSTREAM_STATE_DICT])
        return clustering_snaphot

    def _find_last_consistent_first_inconsistent_clustering_snapshot(self) -> Tuple[Dict, Dict]:
        '''
        go through the snapshots and find the last consistent snapshot and first incosistent snapshot
        '''
        sort_criterion = (CLUSTERS_COL_SNAPSHOT+'.'+CLUSTERS_COL_SNAPSHOT_TIMESTAMP, ASCENDING)
        result = self.clusters_col.find({},sort=[sort_criterion])

        clustering_snapshots = []
        for r in result:
            clustering_snapshots.append(r)

        if len(clustering_snapshots) == 0:
            return self._get_init_clustering_snapshot(), None

        prev_snapshot = None
        snapshot = None
        incosistency_found = False
        for ix in range(len(clustering_snapshots)):
            snapshot = clustering_snapshots[ix]
            snapshot_ntotal = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_NTOTAL]
            snapshot_hash = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
            snapshot_timestamp = snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]

            if ix == 0:
                continue
            else:
                prev_snapshot = clustering_snapshots[ix-1]
                prev_snapshot_ntotal = prev_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_NTOTAL]
                prev_snapshot_hash = prev_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
                prev_snapshot_timestamp = prev_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]

            memes = self._read_memes_between_timestamps(timestamp_min = prev_snapshot_timestamp, timestamp_max = snapshot_timestamp)
            string_repr = self._form_string_repr(memes)

            if  snapshot_ntotal != prev_snapshot_ntotal + len(memes):
                if self.verbose: print('CLUSTERS_COL_SNAPSHOT_NTOTAL: inconsistency')
                incosistency_found = True
                break

            if snapshot_hash != hash_string(prev_snapshot_hash + string_repr):
                if self.verbose: print('CLUSTERS_COL_SNAPSHOT_HASH: inconsistency')
                incosistency_found = True
                break

        if incosistency_found:
            clustering_snapshot_lc = prev_snapshot
            clustering_snapshot_fi = snapshot
        else:
            clustering_snapshot_lc = clustering_snapshots[-1]
            clustering_snapshot_fi = None

        if clustering_snapshot_fi:
            clustering_snapshot_fi = self._decode_clustering_snapshot(clustering_snapshot_fi)
        if clustering_snapshot_lc:
            clustering_snapshot_lc = self._decode_clustering_snapshot(clustering_snapshot_lc)

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

    def _form_string_repr(self, memes: List) -> str:
        '''
        form a string representation of memes dataset.
        To use in incremental hash data stream representation:
        hash_string(previous_hash + string_repr)
        '''
        str = ''.join([m[MEMES_COL_ID] for m in memes])
        return str


    # main function
    def exec_meme_scraping_run(self):

        print('='*100)
        for subreddit in SUBREDDITS:

            print(f'scraping memes from subreddit = {subreddit}')

            most_recent_memes_timestamp = self._read_most_recent_memes_timestamp_from_db(subreddit = subreddit)
            print(f'most_recent_memes_timestamp = {most_recent_memes_timestamp}')
            self.scraping_module.load_subreddit(subreddit = subreddit)
            memes = self.scraping_module.fetch_memes(end_at_timestamp = most_recent_memes_timestamp)

            ids = memes[MEMES_COL_ID]
            image_urls = memes[MEMES_COL_IMAGE_URL]

            n_new_memes = len(ids)
            if self.verbose: print(f'{subreddit}: n_new_memes = {n_new_memes}')

            if n_new_memes > 0:
                if self.verbose: print('Extracting features...')
                features = []
                for image_url in tqdm(image_urls):
                    feature = self.feature_extracting_module.get_features_from_url(image_url)
                    features += [feature]

                # saving memes + features to db
                memes[MEMES_COL_FEAT_VEC] = features
                self._write_memes_to_db(memes = memes)

            print('-'*100)

        print('='*100)

    def exec_clustering_run(self):

        print('='*100)

        # find last consistent and first inconsistent clustering snapshots
        clustering_snapshot_lc, clustering_snapshot_fi = self._find_last_consistent_first_inconsistent_clustering_snapshot()

        # deactivate/remove inconsistent snapshots starting from the first incosistent
        if clustering_snapshot_fi:
            success = self._remove_clustering_snapshots(clustering_snapshot_fi = clustering_snapshot_fi)
            if not success:
                if self.verbose: print('could not remove incosistent clustering snapshots')

        # load the clustering from the last consistent snapshot
        self.clustering_module.ds.load_state_dict(clustering_snapshot_lc[CLUSTERS_COL_DENSTREAM_STATE_DICT])

        # load all memes not considered in the last consistent snapshot
        timestamp_min = clustering_snapshot_lc[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_TIMESTAMP]
        timestamp_max = self._read_most_recent_memes_timestamp_from_db()
        new_memes = self._read_memes_between_timestamps(timestamp_min = timestamp_min, timestamp_max = timestamp_max)

        if len(new_memes) > 0:
            # run clustering
            if self.verbose: print('Run clustering...')
            if self.verbose: print(f'clustering new memes: {len(new_memes)}')

            for new_m in new_memes:
                if isinstance(new_m[MEMES_COL_FEAT_VEC],list):
                    feature = np.array(new_m[MEMES_COL_FEAT_VEC])
                    meme_id = new_m[MEMES_COL_ID]
                    publ_timestamp = int(new_m[MEMES_COL_PUBL_TIMESTAMP])

                    self.clustering_module.cluster_data(data = feature,
                                                        data_id = meme_id,
                                                        timestamp = publ_timestamp)

            # save the results as a snapshot
            new_timestamp = timestamp_max
            new_ntotal = len(new_memes)
            hash_base = clustering_snapshot_lc[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
            new_string_repr = self._form_string_repr(new_memes)
            new_hash = hash_string(hash_base + new_string_repr)
            new_snapshot_info_dict = {CLUSTERS_COL_SNAPSHOT_TIMESTAMP: new_timestamp,
                                      CLUSTERS_COL_SNAPSHOT_NTOTAL: new_ntotal,
                                      CLUSTERS_COL_SNAPSHOT_HASH: new_hash}
            new_denstream_state_dict = self.clustering_module.ds.state_dict()

            new_clustering_snapshot = {CLUSTERS_COL_SNAPSHOT: new_snapshot_info_dict,
                                       CLUSTERS_COL_DENSTREAM_STATE_DICT: new_denstream_state_dict}

            self._write_clustering_snapshot_to_db(clustering_snapshot = new_clustering_snapshot)

        else:
            if self.verbose: print('No new data; no need to run clustering')

        print('='*100)
