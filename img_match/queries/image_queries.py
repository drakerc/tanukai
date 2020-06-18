from copy import deepcopy
from datetime import datetime
from typing import Callable
from elasticsearch_dsl import Q
import numpy as np
import config
from img_match.models.image import Image
from img_match.queries.databases import ElasticDatabase, MilvusDatabase


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
            **image_kwargs
    ) -> str:
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

    def get_partitions(self):
        status, partitions = self._milvus.database.list_partitions(collection_name=config.milvus_collection_name)
        status, stats = self._milvus.database.get_collection_stats(config.milvus_collection_name)
        partition_data = {i['tag']: i['row_count'] for i in stats['partitions']}
        return partition_data

    def remove_duplicates(self):
        # TODO: drawsearch specific, move
        elastic_search = Image.search(using=self._elasticsearch.database,
                                      index=config.elasticsearch_index)
        for number, result in enumerate(elastic_search.scan()):
            print(f'Processing {number}')
            source_id = result.source_id
            source_search = Image.search(using=self._elasticsearch.database, index=config.elasticsearch_index).query('term', source_id=source_id)
            response = source_search.execute()
            if len(response) > 1:
                img_to_delete = response[1]
                img_to_delete_id = img_to_delete.meta.id
                print(f'Deleting {img_to_delete_id}')
                img_to_delete.delete(using=self._elasticsearch.database)
                status = self._milvus.database.delete_entity_by_id(config.milvus_collection_name, [int(img_to_delete_id)])
                if not status.OK():
                    raise Exception(
                        f'Could not remove from Milvus because of an error: {status.message}.')
        print('Done')
        return

    def move_to_partition(self):
        from milvus import MetricType
        import time
        # Image.init(using=self._elasticsearch.database)
        status = self._milvus.database.drop_collection('images')
        time.sleep(5)
        param = {
            'collection_name': 'images',
            'dimension': 1024,
            'index_file_size': 256,  # optional
            'metric_type': MetricType.L2  # optional
        }
        self._milvus.database.create_collection(param)
        status = self._milvus.database.create_partition(
            collection_name='images',
            partition_tag='e621'
        )
        elastic_search = Image.search(using=self._elasticsearch.database, index=config.elasticsearch_index)
        for number, result in enumerate(elastic_search.scan()):
            print(f'Processing {number}')
            image_id = result.meta.id
            status, vectors = self._milvus.database.get_entity_by_id(config.milvus_collection_name, [int(image_id)])
            status, ids = self._milvus.database.insert(
                collection_name='images',
                partition_tag='e621',
                records=vectors
            )
            result_with_new_id = deepcopy(result)
            result_with_new_id.meta.id = ids[0]
            result_with_new_id.meta.index = 'images'
            new_image_result = result_with_new_id.save(
                using=self._elasticsearch.database,
                doc_type='_doc',
                refresh=False
            )
            # status = result.delete()

        print('Done')
        return

    def rename_source_website(self):
        elastic_search = Image.search(using=self._elasticsearch.database, index=config.elasticsearch_index).source(False)
        for number, result in enumerate(elastic_search.scan()):
            print(f'Processing {number}')
            result.update(
                using=self._elasticsearch.database,
                refresh=False,
                source_website='e621'
            )

    def create_index(self):
        from milvus import IndexType
        index_param = {
            'nlist': 16384
        }
        status = self._milvus.database.create_index(config.milvus_collection_name, IndexType.IVF_SQ8, index_param)
        if status.OK():
            return True

    def create_partition(self, partition_tag: str):
        status = self._milvus.database.create_partition(
            collection_name='images',
            partition_tag=partition_tag
        )
