import pandas as pd

sorted_all = pd.read_csv('images_clusters.tsv',sep='\t')

print('memes')
print(sorted_all.drop_duplicates(subset=['cluster'])[{'cluster','image'}])
vc = sorted_all['cluster'].value_counts()
print('meme rank:')
print(vc)
