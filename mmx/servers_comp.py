from typing import Union, Dict, List, Tuple
from pymongo.errors import BulkWriteError

from .const import *
from .servers_core import mmx_server
from .scraping import scraper_reddit
from .featvec import features_module
from .utils import fetch_internal_image_url, download_local_image_url, form_local_image_path

class mmx_server_scrape_featvec(mmx_server):

    def __init__(self, mongodb_url: str, verbose: bool = False):
        super().__init__(mongodb_url = mongodb_url, verbose = verbose)

        self.scraping_module = scraper_reddit(verbose = verbose)
        self.feature_extracting_module = features_module(verbose = verbose)

    def _put_memes_and_featvecs(self, memes: List[Dict]) -> bool:
        try:

            meme_ids = [x[MEMES_COL_ID] for x in memes]
            n_update_memes = self.memes_col.count_documents({MEMES_COL_ID:{'$in':meme_ids}})
            n_all_memes = len(memes)
            n_new_memes = n_all_memes - n_update_memes
            print(f'new_memes = {n_new_memes}; update_memes = {n_update_memes}')

            for i,meme in enumerate(memes):

                if i % 50 == 0:
                    if self.verbose: print(f'{i}/{len(memes)}')

                filter_ = {MEMES_COL_ID: meme[MEMES_COL_ID]}
                update_ = {'$push': {MEMES_COL_SNAPSHOT: meme[MEMES_COL_SNAPSHOT]}}
                out_update = self.memes_col.find_one_and_update(filter=filter_,
                                                                update=update_)
                if out_update:
                    # if self.verbose: print('meme updated')
                    pass
                else:

                    if not meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_LOCAL]:
                        image_path = form_local_image_path(meme)
                        if image_path:
                            # print('image already found in local image path')
                            meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_LOCAL] = image_path
                        else:
                            # print('downloading the image...')
                            meme = download_local_image_url(meme)

                    image_url = fetch_internal_image_url(meme)

                    meme[MEMES_COL_FEAT_VEC] = self.feature_extracting_module.get_features_from_url(image_url)
                    meme[MEMES_COL_FEAT_VEC_MODEL] = FEAT_EXTRACT_MODEL
                    meme = self._validate_meme(meme = meme, send_to_db = True)
                    meme[MEMES_COL_SNAPSHOT] = [meme[MEMES_COL_SNAPSHOT]]
                    out_insert = self.memes_col.insert_one(meme)
                    if out_insert.acknowledged:
                        # if self.verbose: print('meme inserted')
                        pass
            return True

        except BulkWriteError as e:
            if self.verbose: print('error',e)
            return False

    def exec_meme_scraping_feat_extract_run(self) -> None:

        if self.verbose: print('='*100)

        for subreddit in SUBREDDITS:

            if self.verbose: print(f'scraping/feature-extraction from subreddit = {subreddit}')

            # most_recent_memes_timestamp = self._read_most_recent_memes_timestamp_from_db(subreddit = subreddit)
            # if self.verbose: print(f'most_recent_memes_timestamp = {most_recent_memes_timestamp}')

            # scraping part
            self.scraping_module.load_subreddit(subreddit = subreddit)
            # memes = self.scraping_module.fetch_memes(end_at_timestamp = most_recent_memes_timestamp)
            memes = self.scraping_module.fetch_memes()
            memes = self._validate_memes(memes, send_to_db = True)

            # feature extraction
            if len(memes) > 0:
                # self._write_memes_to_db(memes = memes)
                self._put_memes_and_featvecs(memes = memes)
            else:
                if self.verbose: print('No new memes; no feature extraction...')

            if self.verbose: print('-'*100)
        if self.verbose: print('='*100)
