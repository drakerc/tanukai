from datetime import datetime
from typing import Callable
from elasticsearch_dsl import Q
import numpy as np
import config
from img_match.models.image import Image
from img_match.queries.databases import ElasticDatabase, MilvusDatabase
from milvus import IndexType, MetricType


class ImageQueries:

    def __init__(self):
        self._elasticsearch = ElasticDatabase()
        self._milvus = MilvusDatabase()

    def save(
            self,
            vectors: np.ndarray,
            image_path: str,
            phash: str = None,
            refresh_index: bool = False,
            partition_tag: str = None,
            image_model: Callable = Image,
            initialize_dbs_if_not_exist: bool = False,
            **image_kwargs
    ) -> str:
        if initialize_dbs_if_not_exist:
            self.initialize_dbs_if_not_exist(partition_tag)  # kinda breaks the SRP rule
        status, ids = self._milvus.database.insert(
            collection_name=config.milvus_collection_name,
            records=vectors,
            partition_tag=partition_tag
        )
        if not status.OK():
            raise Exception(f'Could not add to Milvus because of an error: {status.message}.')
        image_id = ids[0]
        image_record = image_model(
            _id=image_id,
            image_path=image_path,
            timestamp=datetime.now()
        )
        for index, value in image_kwargs.items():
            image_record[index] = value
        if phash:
            hash_object = {f'hash_{index}': value for index, value in enumerate(phash)}
            image_record['hash'] = hash_object

        result = image_record.save(
            using=self._elasticsearch.database,
            doc_type='_doc',
            refresh=refresh_index
        )
        if not result:
            raise Exception('Could not add the image to Elasticsearch.')
        return image_id

    def find(self, vectors: np.ndarray, pagination_from: int = 0, pagination_size: int = 10, partition_tags: list = None) -> dict:
        search_param = {
            "nprobe": 32  # TODO: make it as a param
        }

        # TODO: Currently Milvus does not support pagination. This is an inefficient "pagination"
        # TODO: hack: we fetch more results than needed and then discard the unneeded ones
        param = {
            'collection_name': config.milvus_collection_name,
            'query_records': vectors,
            'top_k': pagination_from + pagination_size,
            'params': search_param,
            'partition_tags': partition_tags
        }

        status, results = self._milvus.database.search(**param)
        if status.OK():
            elastic_ids = []
            similar_results = {}
            for res in results[0][pagination_from:]:
                similar_results[str(res.id)] = {
                    'distance': res.distance,
                    'id': res.id
                }
                elastic_ids.append(res.id)
            elastic_search = Image.search(using=self._elasticsearch.database,
                                          index=config.elasticsearch_index) \
                .query('ids', values=elastic_ids)
            response = elastic_search[0:pagination_size].execute()
            for img in response:
                similar_results[img.meta.id]['data'] = img  # TODO: use defaultdict
                similar_results[img.meta.id]['path'] = f'{config.short_path}/full/{img.image_path}'
                similar_results[img.meta.id]['thumbnail_path'] = f'{config.short_path}/thumbs/verybig/{img.image_path}'
            return similar_results  # TODO: return as list

    def find_by_phash(
            self,
            phash: str,
            minimum_should_match='10%',
            pagination_from: int = 0,
            pagination_size: int = 10
    ) -> dict:
        should_query = [Q('term', **{f'hash.hash_{index}': value}) for index, value in enumerate(phash)]
        q = Q('bool', should=should_query, minimum_should_match=minimum_should_match)
        similar_results = {}
        elastic_search = Image.search(using=self._elasticsearch.database,
                                      index=config.elasticsearch_index).query(q)
        response = elastic_search[pagination_from:pagination_from + pagination_size].execute()
        for img in response:
            similar_results[img.meta.id] = {
                'distance': img.meta.score,  # TODO: normalize distance
                'data': img,
                'path': f'{config.short_path}/full/{img.image_path}',
                'thumbnail_path': f'{config.short_path}/thumbs/verybig/{img.image_path}'
            }
        return similar_results

    def find_by_id(self, image_id: str, pagination_from: int = 0, pagination_size: int = 10, partition_tags: list = None):
        status, vector = self._milvus.database.get_entity_by_id(collection_name=config.milvus_collection_name, ids=[image_id])
        return self.find(vector, pagination_from, pagination_size, partition_tags)

    def count(self):
        elastic_search = Image.search(using=self._elasticsearch.database,
                                      index=config.elasticsearch_index)
        count = elastic_search.count()
        return count

    def initialize_dbs_if_not_exist(self, partition_tag: str):
        # TODO: pretty slow, maybe try EAFP instead
        if not self.elastic_index_exists():
            self.create_elastic_index()
        if not self.milvus_collection_exists():
            self.create_milvus_collection()
        if partition_tag:
            if not self.milvus_partition_exists(partition_tag):
                self.create_milvus_partition(partition_tag)

    def create_elastic_index(self):
        Image.init(using=self._elasticsearch.database)

    def create_milvus_collection(self):
        param = {
            'collection_name': config.milvus_collection_name,
            'dimension': 1024,
            'index_file_size': 256,  # optional
            'metric_type': MetricType.L2  # optional
        }
        status = self._milvus.database.create_collection(param)
        if status.OK():
            return True
        raise Exception(f'Could not create a collection because of an error: {status.message}.')

    def create_milvus_index(self):
        """
        Indexes are not necessary, but speed things up. Shouldn't be called too often.
        """
        index_param = {
            'nlist': 16384
        }
        status = self._milvus.database.create_index(
            config.milvus_collection_name,
            IndexType.IVF_SQ8,
            index_param
        )
        if status.OK():
            return True
        raise Exception(f'Could not create an index because of an error: {status.message}.')

    def create_milvus_partition(self, partition_tag: str) -> bool:
        status = self._milvus.database.create_partition(
            collection_name=config.milvus_collection_name,
            partition_tag=partition_tag
        )
        if status.OK():
            return True
        raise Exception(f'Could not create a partition because of an error: {status.message}.')

    def get_partitions(self) -> dict:
        """
        Returns dict with Milvus partition data (partition_tag and count)
        :return: dict, e.g. {'ebay': 5213, 'etsy': 1233}
        """
        status, stats = self._milvus.database.get_collection_stats(config.milvus_collection_name)
        partition_data = {i['tag']: i['row_count'] for i in stats['partitions']}
        return partition_data

    def elastic_index_exists(self) -> bool:
        return Image.index.exists()

    def milvus_collection_exists(self) -> bool:
        status, has_collection = self._milvus.database.has_collection(config.milvus_collection_name)
        return has_collection

    def milvus_partition_exists(self, partition_tag: str) -> bool:
        status, has_partition = self._milvus.database.has_partition(partition_tag)
        return has_partition
