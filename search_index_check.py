import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from mmx.servers_core import mmx_server
from mmx.const import *

ms = mmx_server('mongodb_url')

# import pymongo

# memes_col = ms.mongodb.mmx.memes_mobilenet_large
# memes_col = ms.mongodb.mmx.memes_mobilenet_small
# memes_col = ms.mongodb.mmx.memes_resnet
memes_col = ms.mongodb.mmx.memes_efficientnet

# index_name = 'fvindex-mobilenet-large'
# index_name = 'fvindex-mobilenet-small'
# index_name = 'fvindex-resnet'
index_name = 'fvindex-efficientnet'


# memes_col.find({}).sort({})

# meme_id = 't3_1712a0i'
# meme_id = 't3_17172r8'
meme_id = 't3_171c1e6'

meme = memes_col.find_one({MEMES_COL_ID : meme_id})

if not meme:
  print(meme_id)
  exit()

feat_vec = meme[MEMES_COL_FEAT_VEC]

print(meme[MEMES_COL_ID],meme[MEMES_COL_IMAGE_URL])

agg_query = [
  {
    "$search": {
      "index": index_name,
      "knnBeta": {
        "vector": feat_vec,
        "path": MEMES_COL_FEAT_VEC,
        "k": 20
      }
    }
  },
  {
    "$project": {
      "_id": 0,
      "image_url": 1,
      "meme_id": 1,
      # "title": 1,
      "score": { '$meta': "searchScore" }
    }
  }
]

result = memes_col.aggregate(agg_query)
memes = []
for r in result:
    memes.append(r)


nx = 5
ny = len(memes) // 5

if len(memes) % 5 != 0:
    ny += 1

# nx = len(metrics)
# ny = len(embeddings)
dx=4
dy=4

fig = plt.figure(figsize=(dx*nx,dy*ny))
axs = fig.subplots(nrows=ny,ncols=nx)
axs = axs.reshape(-1)


fig.suptitle(f'index = {index_name} consistency check')
for ax in axs:
    # Hide X and Y axes label marks
    ax.xaxis.set_tick_params(labelbottom=False)
    ax.yaxis.set_tick_params(labelleft=False)
    # Hide X and Y axes tick marks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')

for i,meme in enumerate(memes):
    mid = meme[MEMES_COL_ID]
    img = Image.open(meme[MEMES_COL_IMAGE_URL][MEMES_COL_IMAGE_URL_LOCAL])
    img = img.convert(mode='RGB')
    im = np.array(img)
    axs[i].imshow(im,aspect=im.shape[1]/im.shape[0])
    axs[i].set_title(f'''({mid}) score = {meme['score']:.3f}''')

fig.tight_layout(pad=0.05)
fig.savefig(f'index-check_meme_id={meme_id}_index_name={index_name}.png')
