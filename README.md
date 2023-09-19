## What is memsEX?
<a href="">AI-powered meme analysis tool</a>. Consists of two main parts:

- **scraping module**: Continously scans and extracts memes from the most popular subreddits.
- **clustering AI module**: Finds meme clusters using DBSCAN algorithm with feature extraction based on a pretrained neural network.

Both modules run independently through server-like apps. Data is stored in mongodb database and can be extracted via REST API.

## How to run it:
1. You need to setup the mongodb database by running the script:

python setup.py

You need to have the mongodb database setup beforehand. The script will ask for database address, your db name. If mongodb is found at the address, it will initialize the db and run some tests.

2. Run the scraping module:

python server_scrape.py

3. Run the clustering AI module:

python server_cluster.py

4. Run the REST API server:

flask --app server_api run

## Based on:
* [clustering alg](https://github.com/zegami/image-similarity-clustering)
* [memescraper](https://github.com/Salil-Jain/memescraper)
* []
