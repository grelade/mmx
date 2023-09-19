from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from mmx.const import *
from mmx.utils import is_mmx_configured

if not is_mmx_configured():
    exit()

def test_mongodb_connection(mongodb_url):
    try:
        mongodb = MongoClient(mongodb_url)
        print('looking for mongo database...')
        # The ismaster command is cheap and does not require auth.
        mongodb.admin.command('ismaster')
        print(f'Server at {mongodb_url} found!')
        return mongodb

    except ConnectionFailure:
        print(f'NO server at {mongodb_url}!')
        return None


mongodb = test_mongodb_connection(MONGODB_URL)
