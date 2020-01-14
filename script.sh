#!/bin/sh

# run scraper
rm -r memescraper/memes
mkdir memescraper/memes
cd memescraper/memes
#echo "`ls`"
python2 ../scrap.py

#copy memes
cd ../..
mv memescraper/memes image-similarity-clustering


cd image-similarity-clustering
mv memes images

#run linker : creates images.tsv
python linker.py

#run feature extractor : creates images_features.tsv
python extract.py images.tsv

#determine clusters : creates images_clusters.tsv
python cluster.py

#run statistics
python stats.py
