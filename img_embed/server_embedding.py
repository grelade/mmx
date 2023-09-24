from flask import Flask, request, send_file
from PIL import Image
import numpy as np
from core import embedder


app = Flask(__name__)
app.debug=True

em = embedder()
em.load_model('mobilenet-v3-224')

@app.route("/embedding",methods=["POST"])
def calc_img_embedding():
    # get image
    # img_data = request.data
    fp = request.files.get('file')
    img = Image.open(fp.stream)
    img_array = np.array(img)
    embedding = em.embed(img_array)
    return {'img_embed':embedding.tolist()}

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port = 8001)
