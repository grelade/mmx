from typing import Union, Dict, List, Tuple

from .servers_core import mmx_server
from .const import *

class mmx_server_api(mmx_server):

    def __init__(self, mongodb_url: str, verbose: bool = False):
        super().__init__(mongodb_url = mongodb_url, verbose = verbose)
