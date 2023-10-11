from flask import Flask, request
import sys
sys.path.append('./')

from mmx.feat_extract import feat_extractor
from mmx.const import *

app = Flask(__name__)
# app.debug=True

fe = feat_extractor()
fe.load_model(FEAT_EXTRACT_MODEL)

@app.route("/features",methods=["POST"])
def calc_img_features():
    # get image
    fp = request.files.get('file')
    feat_vec = fe.get_featvec(fp)
    del fp
    return {MEMES_COL_FEAT_VEC:feat_vec}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8001)
