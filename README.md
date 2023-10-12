## What is mmx?
<a href="">**MMX** - a simple AI-powered meme analysis tool</a>.

- Scrapes memes periodically and builds time-resolved meme database:
    * reddit.com module

- Offers API endpoints with meme analytics:
    * lists most popular memes with highest level of engagement
    * clusters similar memes using ML techniques (cosine similarity + feature extraction)
    * finds trends

## Requirements
Before building mmx, ensure you have:
* docker
* git-lfs
* a working ATLAS MONGODB database (you can create a free db [https://mongodb.com](here)); important: ATLAS MONGODB is required to run the clustering algorithm)

## How to start your own mmx?

To start **mmx**,
Clone the repo.

Run the build script in development mode:
```
./build.sh dev
```

which creates **mongodb_url** - a file where the mongodb database url is stored. You need to add your database here.

Start the containers:
```
./run.sh all
```
Three containers are created:
- api (serves the webAPI to http://localhost:20410/api/v1/ via werkzeug)
- scrape (handles the scraping)
- feat_extract (handles the ML part)

## Production
Starting mmx in production mode
```
./build.sh prod
```
gives an additional *nginx* docker serving as a reverse-proxy. Gunicorn is the WSGI server of the api docker.
