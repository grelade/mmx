# mongo server
MONGODB_URL = 'mongodb://mongo:27017'
DESCENDING = -1 # pymongo consts
ASCENDING = 1 # pymongo consts
MAIN_DB = 'mmx'
MEMES_COLLECTION = 'memes'
CLUSTERS_COLLECTION = 'clusters'

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

CLUSTERS_COL_SNAPSHOT_CLUSTERS_INFO = 'data_clusters_info'



# REST API server
API_V1_BASE_URL = '/api/v1'
API_PAGE_LIMIT = 50
API_NEXT_URL = 'next_url'



# embed server
FEAT_EXTRACT_API_URL = 'http://embed:8001/embedding'
EMBEDDING_MODEL_PATH = 'mmx/embed_model/mobilenet_v3_small_075_224_embedder.tflite'



# cluster server
CLUSTERING_JOB_INTERVAL = 120
CLUSTERING_MODEL = 'hcluster'
# CLUSTERING_MODEL = 'denstream'
# CLUSTERING_BATCH_SIZE = None
CLUSTERING_BATCH_SIZE = 500

# denstream_clustering algorithm parameters
DENSTREAM_EPS = 12
DENSTREAM_BETA = 0.55
DENSTREAM_MU = 2
DENSTREAM_LAMBDA = 1e-12

# hcluster_clustering algorithm parameters
HCLUSTER_THRESHOLD = 3.0



# scrape server
SCRAPING_JOB_INTERVAL = 60
BASEURL_REDDIT = "https://old.reddit.com/r/"
SUBREDDITS = ['memes','dankmemes','wholesomememes',
              'MemeEconomy','AdviceAnimals','ComedyCemetery',
              'terriblefacebookmemes','funny']
