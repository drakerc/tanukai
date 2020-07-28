import abc
from elasticsearch import Elasticsearch
from milvus import Milvus, IndexType
import redis
import config

class Database(abc.ABC):

    @property
    @abc.abstractmethod
    def database(self):
        pass


class ElasticDatabase(Database):

    def __init__(self):
        self._database = Elasticsearch(
            config.elasticsearch_host,
            verify_certs=config.elasticsearch_verify_certs
        )

    @property
    def database(self):
        return self._database


class MilvusDatabase(Database):

    def __init__(self):
        self._database = Milvus(config.milvus_host, config.milvus_port, pool_size=config.milvus_pool_size)

    @property
    def database(self):
        return self._database

    def create_index(self):
        index_param = {
            'nlist': 16384
        }
        status = self.database.create_index(config.milvus_collection_name, IndexType.IVF_SQ8, index_param)
        if status.OK():
            return True


class RedisDatabase(Database):

    def __init__(self):
        self._database = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            charset="utf-8",
            decode_responses=True
        )

    @property
    def database(self):
        return self._database
