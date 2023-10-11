
# mongodb
DESCENDING = -1 # hardcoded pymongo consts
ASCENDING = 1 # hardcoded pymongo consts
MAIN_DB = 'mmx'
# MEMES_COLLECTION = 'memes_mobilenet_small'
# MEMES_COLLECTION = 'memes_mobilenet_large'
# MEMES_COLLECTION = 'memes_resnet'
# MEMES_COLLECTION = 'memes_efficientnet'
MEMES_COLLECTION = 'memes'
LOCAL_IMG_STORAGE = './img'

# search index
MEMES_COL_SEARCH_INDEX = 'fvindex-efficientnet'
MEMES_COL_SEARCH_SCORE = 'index_score'
MEMES_COL_SEARCH_LIMIT = 20
MEMES_COL_SEARCH_THRESHOLD = 0.9
COMMENTS_TO_UPVOTES_FACTOR = 50 # used in popularity score calculation; 1 comment ~ 50 upvotes

# trends parameters
TREND_SNAPSHOT_BIN_WIDTH = 60 # gather snapshots into bins (in minutes)
TREND_SNAPSHOT_NUM_BINS = 48 # how many bins to include in trend estimation
TREND_STRONG_INCREASE = 2
TREND_WEAK_INCREASE = 1
TREND_NO_CHANGE = 0
TREND_WEAK_DECREASE = -1
TREND_STRONG_DECREASE = -2

# memes collection
MEMES_COL_ID = 'meme_id'
MEMES_COL_IMAGE_URL = 'image_url'
MEMES_COL_IMAGE_URL_SOURCE = 'source'
MEMES_COL_IMAGE_URL_LOCAL = 'local'
MEMES_COL_IMAGE_URL_ALTER = 'alter'
MEMES_COL_TITLE = 'title'
MEMES_COL_PUBL_TIMESTAMP = 'publ_timestamp'
MEMES_COL_FEAT_VEC = 'feat_vec'
MEMES_COL_FEAT_VEC_MODEL = 'feat_vec_model'
MEMES_COL_SUBREDDIT = 'subreddit'
MEMES_COL_SNAPSHOT = 'snapshots'
MEMES_COL_SNAPSHOT_TIMESTAMP = 'timestamp'
MEMES_COL_SNAPSHOT_UPVOTES = 'upvotes'
MEMES_COL_SNAPSHOT_COMMENTS = 'comments'
MEMES_COL_LAST_SNAPSHOT = 'last_snapshot'
MEMES_COL_POPULARITY_SCORE = 'pop_score'

# api server
API_V1_BASE_URL = '/api/v1'
API_PAGE_LIMIT = 50
API_NEXT_URL = 'next_url'

# embed server
EMBEDDING_API_URL = 'http://embed:8001/embedding'
# EMBEDDING_MODEL = 'mobilenet_v3_small'
# EMBEDDING_MODEL = 'mobilenet_v3_large'
# EMBEDDING_MODEL = 'resnet_v1_50'
EMBEDDING_MODEL = 'efficientnet_v2_m'

# scrape server
SCRAPING_JOB_INTERVAL = 60
BASEURL_REDDIT = "https://old.reddit.com/r/"
SUBREDDITS = ['memes','dankmemes','wholesomememes',
              'MemeEconomy','AdviceAnimals','ComedyCemetery',
              'terriblefacebookmemes','funny']
# SUBREDDITS = ['funny']
