from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from mmx.const import *
from mmx.utils import is_mmx_configured

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


mongodb_url = input(f'check server [default = {MONGODB_URL}]')
if mongodb_url == "":
    mongodb_url = MONGODB_URL

mongodb = test_mongodb_connection(mongodb_url)
