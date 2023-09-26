import numpy as np
from tqdm import tqdm
from typing import Union, Dict, List, Tuple

from .const import *
from .servers_core import mmx_server
from .scraping import scraper_reddit
from .ml import feat_extract,denstream_clustering, hcluster_clustering
from .utils import hash_string

class mmx_server_scrape_embed(mmx_server):

    def __init__(self, mongodb_url: str, verbose: bool = False):
        super().__init__(mongodb_url = mongodb_url, verbose = verbose)

        self.scraping_module = scraper_reddit(verbose = verbose)
        self.feature_extracting_module = feat_extract(verbose = verbose)

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


class mmx_server_cluster(mmx_server):

    def __init__(self, mongodb_url: str, verbose: bool = False):
        super().__init__(mongodb_url = mongodb_url, verbose = verbose)

        if CLUSTERING_MODEL == 'denstream':
            self._clustering_module_func = denstream_clustering
        elif CLUSTERING_MODEL == 'hcluster':
            self._clustering_module_func = hcluster_clustering
        self.clustering_module = self._clustering_module_func(verbose = verbose)

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
        string_repr = mmx_server_cluster._form_string_repr(memes)

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

    def _load_clustering_snapshot(self,clustering_snapshot: Dict) -> None:
        '''
        Load a clustering snapshot into the self.clustering_module.
        '''
        # clustering_snapshot = clustering_snapshot.copy()
        self.clustering_module.alg_func.load_state_dict_compressed(state_dict_compressed = clustering_snapshot[CLUSTERS_COL_CLUSTERING_STATE_DICT],
                                                             decompressor_func = self._gen_features_array)

    def _form_next_clustering_snapshot(self, new_memes: List[Dict], previous_clustering_snapshot: Dict) -> Dict:
        '''
        Form a snapshot from the current state of the self.clustering_module,
        newly clustered data and the previous snapshot.
        '''
        new_timestamp = max([meme[MEMES_COL_PUBL_TIMESTAMP] for meme in new_memes])
        new_ntotal = previous_clustering_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_NTOTAL] + len(new_memes)
        hash_base = previous_clustering_snapshot[CLUSTERS_COL_SNAPSHOT][CLUSTERS_COL_SNAPSHOT_HASH]
        new_string_repr = mmx_server_cluster._form_string_repr(new_memes)
        new_hash = hash_string(hash_base + new_string_repr)


        new_snapshot_info_dict = {CLUSTERS_COL_SNAPSHOT_TIMESTAMP: new_timestamp,
                                  CLUSTERS_COL_SNAPSHOT_NTOTAL: new_ntotal,
                                  CLUSTERS_COL_SNAPSHOT_HASH: new_hash
                                  }

        new_clustered_ids_ = list(filter(lambda x: len(x) >= CLUSTERING_MIN_CLUSTER_SIZE, self.clustering_module.clusters))
        print(len(new_clustered_ids_))

        new_init_clusters_info_list = []
        for new_clustered_ids in new_clustered_ids_:
            new_memes_sub = [meme for meme in new_memes if meme[MEMES_COL_ID] in new_clustered_ids]
            new_example_imgs = [meme[MEMES_COL_IMAGE_URL] for meme in new_memes_sub]
            new_nmemes = len(new_clustered_ids)
            new_total_comments = sum([meme[MEMES_COL_COMMENTS] for meme in new_memes_sub])
            new_total_upvotes = sum([meme[MEMES_COL_UPVOTES] for meme in new_memes_sub])

            new_init_clusters_info_dict = {CLUSTERS_COL_INFO_EXAMPLE_IMAGE: new_example_imgs,
                                        CLUSTERS_COL_INFO_IDS: new_clustered_ids,
                                        CLUSTERS_COL_INFO_NMEMES: new_nmemes,
                                        CLUSTERS_COL_INFO_TOTAL_COMMENTS: new_total_comments,
                                        CLUSTERS_COL_INFO_TOTAL_UPVOTES: new_total_upvotes
                                        }

            new_init_clusters_info_list.append(new_init_clusters_info_dict)

        new_clustering_state_dict = self.clustering_module.alg_func.state_dict_compressed()

        new_clustering_snapshot = {CLUSTERS_COL_SNAPSHOT: new_snapshot_info_dict,
                                   CLUSTERS_COL_INFO: new_init_clusters_info_list,
                                   CLUSTERS_COL_CLUSTERING_STATE_DICT: new_clustering_state_dict
                                   }

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

    def exec_clustering_run(self, clustering_batch_size: int = None) -> None:

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


            if clustering_batch_size:
                new_memes = new_memes[:clustering_batch_size]
                cluster_condition = len(new_memes) == clustering_batch_size
            else:
                cluster_condition = len(new_memes) > 0

            if cluster_condition:
                # run clustering
                if self.verbose: print('Run clustering...')
                self.clustering_module.append_data(new_memes)
                self.clustering_module.form_clusters()

                # save the results as a snapshot
                new_clustering_snapshot = self._form_next_clustering_snapshot(new_memes = new_memes,
                                                                            previous_clustering_snapshot = clustering_snapshot_lc)
                self._write_clustering_snapshot_to_db(clustering_snapshot = new_clustering_snapshot)

            else:
                if self.verbose: print('No new data; no need to run clustering')
                break

        if self.verbose: print('FINISH Clustering snapshots:')
        self._plot_clustering_snapshots()

        if self.verbose: print('='*100)

