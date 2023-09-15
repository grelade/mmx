

#default directories
default_datadir = "data"
default_analdir = "anal"

#default date format
default_date_format = "%Y-%m-%d_%H-%M"

#columns found in metadata files
METADATA_COLUMNS = {'id':'id',
                'scrape_time':'time',
                'scrape_source':'source',
                'image_filename':'filename',
                'image_title':'title',
                'image_upvotes':'upvotes',
                'image_publ_date':'publdate',
                'image_url':'imgurl',
				'no_of_comments':'comments',
                'feature_vector':'feature',
                'cluster_id':'cluster',
				'cluster_size':'cluster_size',
                'umap_x_coord':'umap_x',
                'umap_y_coord':'umap_y',
                'tsne_x_coord':'umap_x',
                'tsne_y_coord':'tsne_y'}

# columns making up the multi-index
# METADATA_INDEX_COLUMNS = list(map(METADATA_COLUMNS = {'id':'id',['id','scrape_time','scrape_source']))
METADATA_INDEX_COLUMNS = METADATA_COLUMNS

md_cols = METADATA_INDEX_COLUMNS + [METADATA_COLUMNS['image_filename'],METADATA_COLUMNS['image_title'],metadata_columns['image_upvotes'],metadata_columns['no_of_comments'],metadata_columns['image_publ_date'],metadata_columns['image_url']]
md_feats_cols = METADATA_INDEX_COLUMNS + [METADATA_COLUMNS['feature_vector']]
md_clusters_cols = METADATA_INDEX_COLUMNS + [METADATA_COLUMNS['cluster_id']]

# which image types to scrape
IMAGE_FILETYPES = ['jpg','jpeg','png','gif'] # (!) gifs included
