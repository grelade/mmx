from pymongo import DESCENDING as desc, ASCENDING as asc

# core.mmx_server consts
MONGODB_URL = ''
DESCENDING = desc
ASCENDING = asc
MAIN_DB = 'mmx'
MEMES_COLLECTION = 'memes'
CLUSTERS_COLLECTION = 'clusters'
FEAT_EXTRACT_MODEL = 'resnet18'
# CLUSTERING_MODEL = 'denstream'
CLUSTERING_MODEL = 'hcluster'

# clustering parameters
# CLUSTERING_BATCH_SIZE = None
CLUSTERING_BATCH_SIZE = 500

# denstream_clustering algorithm parameters
DENSTREAM_EPS = 12
DENSTREAM_BETA = 0.55
DENSTREAM_MU = 2
DENSTREAM_LAMBDA = 1e-12

# hcluster_clustering algorithm parameters
HCLUSTER_THRESHOLD = 5.5

# server_cluster
CLUSTERING_JOB_INTERVAL = 120
SCRAPING_JOB_INTERVAL = 60

#scraping.scraper_reddit consts
BASEURL_REDDIT = "https://old.reddit.com/r/"
SUBREDDITS = ['memes','dankmemes','wholesomememes',
              'MemeEconomy','AdviceAnimals','ComedyCemetery',
              'terriblefacebookmemes','funny']

# memes collection
MEMES_COL_ID = 'id'
MEMES_COL_IMAGE_URL = 'image_url'
MEMES_COL_TITLE = 'title'
MEMES_COL_UPVOTES = 'upvotes'
MEMES_COL_COMMENTS = 'comments'
MEMES_COL_PUBL_TIMESTAMP = 'publ_timestamp'
MEMES_COL_FEAT_VEC = 'feat_vec'
MEMES_COL_SUBREDDIT = 'subreddit'

# clusters collection
CLUSTERS_COL_SNAPSHOT = 'snapshot'
CLUSTERS_COL_SNAPSHOT_TIMESTAMP = 'timestamp'
CLUSTERS_COL_SNAPSHOT_NTOTAL = 'data_total'
CLUSTERS_COL_SNAPSHOT_HASH = 'data_hash'
CLUSTERS_COL_CLUSTERED_IDS = 'data_clustered_ids'
CLUSTERS_COL_CLUSTERING_STATE_DICT = 'state_dict'
