from typing import Union, Dict, List, Tuple

from .base import mmx_server
from .const import *

class mmx_server_api(mmx_server):

    def __init__(self, mongodb_url: str, verbose: bool = False):
        super().__init__(mongodb_url = mongodb_url, verbose = verbose)

    def read_memes(self, meme_ids: List):
        pass

    def read_clusters(self):
        result = self.clusters_col.find_one({})
