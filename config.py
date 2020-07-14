import os
from dotenv import load_dotenv
load_dotenv()

elasticsearch_host = [os.getenv('elasticsearch_host')]
elasticsearch_verify_certs = os.getenv('elasticsearch_verify_certs') == 'True'

elasticsearch_index = os.getenv('elasticsearch_index')
elasticsearch_shards = int(os.getenv('elasticsearch_shards'))
elasticsearch_replicas = int(os.getenv('elasticsearch_replicas'))

milvus_host = os.getenv('milvus_host')
milvus_port = os.getenv('milvus_port')
milvus_pool_size = int(os.getenv('milvus_pool_size'))
milvus_collection_name = os.getenv('milvus_collection_name')

phash_size = int(os.getenv('phash_size'))
phash_size_result = int(os.getenv('phash_size_result'))

images_path = os.getenv('images_path')
short_path = os.getenv('short_path')

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_ROOT_PASSWORD = os.getenv('MYSQL_ROOT_PASSWORD')
