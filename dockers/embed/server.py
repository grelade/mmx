from flask import Flask, request
import sys
sys.path.append('./')

from mmx.embed import embedder

app = Flask(__name__)
# app.debug=True

em = embedder()
em.load_model('mobilenet-v3-224')

@app.route("/embedding",methods=["POST"])
def calc_img_embedding():
    # get image
    # img_data = request.data
    fp = request.files.get('file')
    embedding = em.embed_file(fp)
    del fp
    return {'img_embed':embedding}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8001)
