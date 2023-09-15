from pymongo import DESCENDING as desc, ASCENDING as asc

#scraping.scraper_reddit consts
BASEURL_REDDIT = "https://old.reddit.com/r/"
SUBREDDITS = ['memes','dankmemes','wholesomememes','MemeEconomy','AdviceAnimals','ComedyCemetery','terriblefacebookmemes','funny']

#feature extraction module consts
FEAT_EXTRACT_MODEL = 'resnet50'

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
# CLUSTERS_COL_SNAPSHOT_ACTIVE = 'is_active'
CLUSTERS_COL_DENSTREAM_STATE_DICT = 'denstream_state_dict'


#core.mmx_server consts
MONGODB_URL = 'mongodb://localhost:27017'
DESCENDING = desc
ASCENDING = asc
MAIN_DB = 'mmx'
MEMES_COLLECTION = 'memes'
CLUSTERS_COLLECTION = 'clusters'
SNAPSHOTS_COLLECTION = 'snapshots'

# MEME_RATE = 1/500000 # precalculated
# EPS = 5

