## memsEX
tool for meme popularity analysis

## based on:
* [clustering alg](https://github.com/zegami/image-similarity-clustering)
* [memescraper](https://github.com/Salil-Jain/memescraper)

## scrape:

To scrape use
```
python scrape_batch.py
```
which should create directory *data* and store memes,dankmemes and wholesomememes.

## analyze:
To analyze scraped dat use
```
python analyzer.py --metadatas LIST_OF_METADATAS
```
creates *anal* directory with analyses. outputs a scatter plot with umap and clustering encoded through colors.

## view online:
