from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from typing import Union, Dict, List, Tuple

class mmx_api:

    def __init__(self, verbose: bool = False):

        self.mongodb = MongoClient(MONGODB_URL)
        self.memes_col = self.mongodb[MAIN_DB][MEMES_COLLECTION]
        self.clusters_col = self.mongodb[MAIN_DB][CLUSTERS_COLLECTION]

        self.verbose = verbose

    def read_memes(self, meme_ids: List):
        pass

    def read_clusters(self):
        result = self.clusters_col.find_one({})
