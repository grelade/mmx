
# mongodb
DESCENDING = -1 # hardcoded pymongo consts
ASCENDING = 1 # hardcoded pymongo consts
MAIN_DB = 'mmx'
MEMES_COLLECTION = 'memes_test'
CLUSTERS_COLLECTION = 'clusters'

# memes collection
MEMES_COL_ID = 'meme_id'
MEMES_COL_IMAGE_URL = 'image_url'
MEMES_COL_TITLE = 'title'
MEMES_COL_PUBL_TIMESTAMP = 'publ_timestamp'
MEMES_COL_FEAT_VEC = 'feat_vec'
MEMES_COL_SUBREDDIT = 'subreddit'
MEMES_COL_SNAPSHOT = 'snapshots'
MEMES_COL_SNAPSHOT_TIMESTAMP = 'timestamp'
MEMES_COL_SNAPSHOT_UPVOTES = 'upvotes'
MEMES_COL_SNAPSHOT_COMMENTS = 'comments'



# clusters collection
CLUSTERS_COL_SNAPSHOT = 'snapshot'
CLUSTERS_COL_SNAPSHOT_TIMESTAMP = 'timestamp'
CLUSTERS_COL_SNAPSHOT_NTOTAL = 'data_total'
CLUSTERS_COL_SNAPSHOT_HASH = 'data_hash'
CLUSTERS_COL_INFO = 'clusters_info'
CLUSTERS_COL_INFO_IDS = 'meme_ids'
CLUSTERS_COL_INFO_EXAMPLE_IMAGE = 'example_image_url'
CLUSTERS_COL_INFO_NMEMES = 'num_memes'
CLUSTERS_COL_INFO_TOTAL_COMMENTS = 'total_comments'
CLUSTERS_COL_INFO_TOTAL_UPVOTES = 'total_upvotes'
CLUSTERS_COL_CLUSTERING_STATE_DICT = 'state_dict'


# api server
API_V1_BASE_URL = '/api/v1'
API_PAGE_LIMIT = 50
API_NEXT_URL = 'next_url'


# embed server
FEAT_EXTRACT_API_URL = 'http://embed:8001/embedding'
# EMBEDDING_MODEL = 'mobilenet_v3'
EMBEDDING_MODEL = 'resnet50'


# cluster server
CLUSTERING_MODEL = 'hcluster'
# CLUSTERING_MODEL = 'denstream'
CLUSTERING_MIN_CLUSTER_SIZE = 3

# denstream_clustering algorithm parameters
DENSTREAM_EPS = 12
DENSTREAM_BETA = 0.55
DENSTREAM_MU = 2
DENSTREAM_LAMBDA = 1e-12

# hcluster_clustering algorithm parameters
HCLUSTER_THRESHOLD = 6.4


# scrape server
SCRAPING_JOB_INTERVAL = 60
BASEURL_REDDIT = "https://old.reddit.com/r/"
SUBREDDITS = ['memes','dankmemes','wholesomememes',
              'MemeEconomy','AdviceAnimals','ComedyCemetery',
              'terriblefacebookmemes','funny']
# SUBREDDITS = ['memes']
