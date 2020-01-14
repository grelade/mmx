import pandas as pd
import os

imlist = os.listdir('images')
df = pd.DataFrame({'image':imlist})
df.index.name = 'id'
df.to_csv('images.tsv',sep='\t')
