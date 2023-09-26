import os
from urllib.parse import urlparse
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import BulkWriteError, ConnectionFailure

from .const import *

class mmx_server:

    def __init__(self, mongodb_url: str, verbose: bool = True):
        self.verbose = verbose
        self.mongodb_url = mongodb_url
        self.mongodb = mmx_server._get_mongoclient(self.mongodb_url)
        self.memes_col = self.mongodb[MAIN_DB][MEMES_COLLECTION]
        self.clusters_col = self.mongodb[MAIN_DB][CLUSTERS_COLLECTION]

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
