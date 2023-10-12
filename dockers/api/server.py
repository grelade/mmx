import argparse
from flask import Flask
from flask_cors import CORS
import os

import sys
sys.path.append('./')
from mmx.servers_core import mmx_server
from mmx.servers_api import info_view,memes_view
from mmx.const import *



def gen_app(mongodb_url):

    app = Flask(__name__)
    CORS(app)

    # mongodb_url = args.mongodb_url
    # mongodb_url = os.environ.get('MONGODB_URL')
    # print('mongodb_url:',mongodb_url)
    server = mmx_server(mongodb_url = mongodb_url, verbose = True)

    info_view.register(app)
    memes_view.register(app,init_argument = server)

    if not server.is_mongodb_active():
        print('Could not connect to mongo; exiting')
        exit()

    return app


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='mmx api server')
    parser.add_argument('-m', '--mongodb_url', type=str, default='/run/secrets/mongodb_url',
                        help='''Specify the url for MONGO database. Could be:
                                URI: mongodb://localhost:27100 or,
                                Path to file: /run/secrets/mongodb_url (useful in docker secrets)''')
    args = parser.parse_args()
    mongodb_url = args.mongodb_url
    app = gen_app(mongodb_url)

    app.run(debug = False, host='0.0.0.0', port = 8002)
