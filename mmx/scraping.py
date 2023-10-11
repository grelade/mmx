import numpy as np
import urllib
import sys
import re
import time
from typing import List, Dict
from datetime import datetime

from .const import *

def fetch_html(url: str, try_limit: int = 5, verbose: bool = False) -> str:
    '''download html data of url using urllib'''

    if verbose: print(f'fetch_html({url})')
    tries = 0

    while tries < try_limit:
        try:
            htmlfile = urllib.request.urlopen(url)
            htmltext = htmlfile.read().decode("utf-8")
            return htmltext

        except urllib.error.HTTPError:
            if verbose: print('reached connection limit: sleeping')
            time.sleep(20)
            tries += 1
            continue
        except ValueError:
            if verbose: print('ValueError detected!')
            tries += 1
            continue
        except:
            if verbose: print('catched other error: ',sys.exc_info()[0])
            tries += 1
            continue

    return ''

class scraper_reddit:

    def __init__(self,
                 verbose: bool = False):

        # self.url = subreddit_url
        self.verbose = verbose
        self.subreddit = None
        self.subreddit_url = None

    def load_subreddit(self,subreddit: str = 'memes'):
        self.subreddit = subreddit
        self.subreddit_url = BASEURL_REDDIT + subreddit + '/?limit=100'

    @staticmethod
    def _extract_meme_ids(html: str) -> List:
        '''
        extract meme ids from html string
        '''
        ids_regex = "data-fullname=\"(.+?)\""
        ids_pattern = re.compile(ids_regex)
        ids = re.findall(ids_pattern, html)
        return ids

    @staticmethod
    def _extract_meme_image_urls(html: str) -> List:
        '''
        extract image urls from html string
        '''
        urls_regex = "data-url=\"(.+?)\""
        # urls_regex = "data-url=\"([^?]+?)\"" # name.jpg?property=121 bug fix
        urls_pattern = re.compile(urls_regex)
        urls = re.findall(urls_pattern,html)
        return urls

    @staticmethod
    def _extract_meme_titles(html: str) -> List:
        '''
        extract image titles from html string
        '''
        titles_regex = "data-event-action=\"title\".+?>(.+?)<"
        titles_pattern = re.compile(titles_regex)
        titles = re.findall(titles_pattern, html)
        return titles

    @staticmethod
    def _extract_meme_upvotes(html: str) -> List:
        '''
        extract image upvotes from html string
        '''
        # regex to identify upvotes
        upvotes_regex = "data-score.+?\"(.+?)\""
        upvotes_pattern = re.compile(upvotes_regex)
        upvotes = re.findall(upvotes_pattern, html)
        return upvotes

    @staticmethod
    def _extract_meme_comments(html: str) -> List:
        '''
        extract image comments from html string
        '''
        # regex number of comments
        comments_regex = "data-comments-count.+?\"(.+?)\""
        comments_pattern = re.compile(comments_regex)
        comments = re.findall(comments_pattern, html)
        return comments

    @staticmethod
    def _extract_meme_publ_timestamps(html: str) -> List:
        '''
        extract image publication timestamp from html string
        '''
        # regex meme publication timestamp
        publtimestamp_regex = "data-timestamp.+?\"(.+?)\""
        publtimestamp_pattern = re.compile(publtimestamp_regex)
        publtimestamp = re.findall(publtimestamp_pattern, html)
        return publtimestamp

    @staticmethod
    def _extract_nextpage_url(html: str) -> List:
        nextpage_url_regex = "next-button.+?\"(.+?)\""
        nextpage_url_pattern = re.compile(nextpage_url_regex)
        nextpage_url = re.findall(nextpage_url_pattern,html)
        if(len(nextpage_url) < 4 and nextpage_url[0]=='desktop-onboarding-sign-up__form-note'):
            return ''
        else:
            return nextpage_url[0]

    def _fetch_memes_to_data_dict(self,
                                  n_pages: int = -1,
                                  end_at_timestamp: int = None) -> Dict:

        # small helper conversion function
        str2int = lambda data: [int(x) for x in data]

        nextpage_url = self.subreddit_url
        ids = []
        image_urls = []
        titles = []
        upvotes = []
        comments = []
        publ_timestamps = []

        page = 0
        while True:
            html = fetch_html(nextpage_url, verbose = self.verbose)
            new_ids = scraper_reddit._extract_meme_ids(html)
            new_image_urls = scraper_reddit._extract_meme_image_urls(html)
            new_titles = scraper_reddit._extract_meme_titles(html)
            new_upvotes = scraper_reddit._extract_meme_upvotes(html)
            new_comments = scraper_reddit._extract_meme_comments(html)
            new_publ_timestamps = scraper_reddit._extract_meme_publ_timestamps(html)
            if not (len(new_ids) == len(new_image_urls) == len(new_titles) == len(new_upvotes) == len(new_comments) == len(new_publ_timestamps)):
                if self.verbose: print(f'scraping dims incompatible: ids[{len(new_ids)}] image_urls[{len(new_image_urls)}] titles[{len(new_titles)}] upvotes[{len(new_upvotes)}] comments[{len(new_comments)}] publ_timestamps[{len(new_publ_timestamps)}]')
            ids += new_ids
            image_urls += new_image_urls
            titles += new_titles
            upvotes += new_upvotes
            comments += new_comments
            publ_timestamps += new_publ_timestamps
            nextpage_url = scraper_reddit._extract_nextpage_url(html)

            page += 1
            if self.verbose: print(f'page = {page}')
            if page == n_pages:
                break
            if nextpage_url == '':
                break
            if end_at_timestamp:
                if min(str2int(publ_timestamps)) < end_at_timestamp:
                    break

        # conversion
        ids = np.array(ids)
        image_urls = np.array(image_urls)
        titles = np.array(titles)
        upvotes = str2int(upvotes)
        upvotes = np.array(upvotes,dtype=int)
        comments = str2int(comments)
        comments = np.array(comments,dtype=int)
        publ_timestamps = str2int(publ_timestamps)
        publ_timestamps = np.array(publ_timestamps,dtype=int)

        if len(ids.shape) > 1 or len(image_urls.shape) > 1 or len(titles.shape) > 1 or len(upvotes.shape) > 1 or len(comments.shape) > 1 or len(publ_timestamps.shape) > 1:
            print(ids.shape, image_urls.shape, titles.shape, upvotes.shape, comments.shape, publ_timestamps.shape)
            # input('WAITING')

        # sort the scraped memes
        sort_ixs = np.argsort(publ_timestamps)
        ids = ids[sort_ixs]
        image_urls = image_urls[sort_ixs]
        titles = titles[sort_ixs]
        upvotes = upvotes[sort_ixs]
        comments = comments[sort_ixs]
        publ_timestamps = publ_timestamps[sort_ixs]

        # restrict to publ_timestamps > end_at_timestamps
        if end_at_timestamp:
            sub_ixs = np.argwhere(publ_timestamps > end_at_timestamp)
            ids = ids[sub_ixs]
            image_urls = image_urls[sub_ixs]
            titles = titles[sub_ixs]
            upvotes = upvotes[sub_ixs]
            comments = comments[sub_ixs]
            publ_timestamps = publ_timestamps[sub_ixs]

        snapshot_timestamps = [int(datetime.now().timestamp()*1000)]*len(ids)

        subreddits = np.array([self.subreddit]*len(ids))
        image_urls_local = [None]*len(ids)
        image_urls_alter = [None]*len(ids)

        # return {MEMES_COL_ID: ids,
        #         MEMES_COL_IMAGE_URL: image_urls,
        #         MEMES_COL_TITLE: titles,
        #         MEMES_COL_SNAPSHOT: {MEMES_COL_SNAPSHOT_TIMESTAMP: snapshot_timestamps,
        #                              MEMES_COL_SNAPSHOT_UPVOTES: upvotes,
        #                              MEMES_COL_SNAPSHOT_COMMENTS: comments},
        #         MEMES_COL_PUBL_TIMESTAMP: publ_timestamps,
        #         MEMES_COL_SUBREDDIT: subreddits}

        return {MEMES_COL_ID: ids,
                MEMES_COL_IMAGE_URL: {MEMES_COL_IMAGE_URL_SOURCE :image_urls,
                                      MEMES_COL_IMAGE_URL_LOCAL: image_urls_local,
                                      MEMES_COL_IMAGE_URL_ALTER: image_urls_alter},
                MEMES_COL_TITLE: titles,
                MEMES_COL_SNAPSHOT: {MEMES_COL_SNAPSHOT_TIMESTAMP: snapshot_timestamps,
                                     MEMES_COL_SNAPSHOT_UPVOTES: upvotes,
                                     MEMES_COL_SNAPSHOT_COMMENTS: comments},
                MEMES_COL_PUBL_TIMESTAMP: publ_timestamps,
                MEMES_COL_SUBREDDIT: subreddits}

    @staticmethod
    def _convert_data_dict_shallow_to_db_list(data_dict: Dict) -> List:
        '''
        convert memes data dictionary returned by the self._fetch_memes_to_data_dict to a mongodb-friendly list of records
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

    @staticmethod
    def _convert_data_dict_to_db_list(data_dict: Dict) -> List:
        conv = scraper_reddit._convert_data_dict_to_db_list
        conv_shallow = scraper_reddit._convert_data_dict_shallow_to_db_list

        if isinstance(data_dict, dict):
            if not all(map(lambda x: isinstance(x,(list, np.ndarray)), data_dict.values())):
                data_dict = {k: conv(v) for k,v in data_dict.items()}

            return conv_shallow(data_dict)
        elif isinstance(data_dict, (list, np.ndarray)):
            return data_dict

    def fetch_memes(self,
                    n_pages: int = -1,
                    end_at_timestamp: int = None) -> List:

        data_dict = self._fetch_memes_to_data_dict(n_pages = n_pages, end_at_timestamp = end_at_timestamp)

        memes = scraper_reddit._convert_data_dict_to_db_list(data_dict)
        return memes

