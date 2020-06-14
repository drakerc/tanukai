# elasticsearch_host = 'http://localhost'
# milvus_host = '127.0.0.1'
# milvus_port = '19530'

milvus_host = 'localhost'
# milvus_host = 'image_search_milvus'
milvus_port = '19530'
milvus_pool_size = 10
milvus_collection_name = 'images_'

# elasticsearch_host = ['image_search_elastic:9200']
elasticsearch_host = ['http://localhost:9200']
elasticsearch_verify_certs = False

elasticsearch_index = 'images_sis'
elasticsearch_shards = 5
elasticsearch_replicas = 0

phash_size = 16
phash_size_result = 64

images_path = '/home/kkosinski/sis/static/images'
short_path = 'static/images'
