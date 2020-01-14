import pandas as pd
import torch

# meme similarity measure
def dist(x,y):
    return torch.norm(torch.tensor(x)-torch.tensor(y))

names = pd.read_csv('images.tsv',sep='\t')
features =pd.read_csv('images_features.tsv',sep='\t')

# map 'features' col from str to list
features['features'] = features['features'].apply(lambda x:list(map(float,x.split(','))))


sorted_all = pd.DataFrame(columns=['id','cluster'])

# similarity threshold
th = 25

# find and cluster similar images
i = 1
while features.shape[0]>0:
    point = features.iloc[0]
    sorted_temp = pd.DataFrame(columns=['id','features'])
    #print('id =',point['id'])
    sorted_temp = sorted_temp.append(point)
    data = features.shift(-1)
    t0 = data[data['features'].map(lambda x: dist(point['features'],x).numpy()) < th]
    sorted_temp = sorted_temp.append(t0)
    #print('sorted0.shape[0] =',sorted_temp.shape[0])
    #print('sorted0[\'id\'] =',sorted_temp['id'])
    features = pd.concat([features,sorted_temp]).drop_duplicates(subset=['id'],keep=False)
    sorted_temp['cluster'] = i
    i+=1
    sorted_all = sorted_all.append(sorted_temp[{'id','cluster'}])
    #print('features.shape[0] =',features.shape[0])
    #print('features =',features)
    #print('=====================================')

# append names
sorted_all = sorted_all.join(names,on='id',how='right',lsuffix='0',sort=False).drop('id',axis=1)

# export
sorted_all.to_csv('images_clusters.tsv',sep='\t')

#print(sorted_all.value_counts())
