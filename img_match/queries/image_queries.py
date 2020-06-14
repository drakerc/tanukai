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
            image_model: Callable = Image,
            **image_kwargs
    ) -> str:
        status, ids = self._milvus.database.insert(
            collection_name=config.milvus_collection_name,
            records=vectors
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

    def find(self, vectors: np.ndarray, pagination_from: int = 0, pagination_size: int = 10) -> dict:
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

    def count(self):
        elastic_search = Image.search(using=self._elasticsearch.database,
                                      index=config.elasticsearch_index)
        count = elastic_search.count()
        return count
