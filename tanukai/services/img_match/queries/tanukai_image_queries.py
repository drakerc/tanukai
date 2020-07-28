from copy import deepcopy
import config
from img_match.models.image import Image
from img_match.queries.databases import RedisDatabase
from img_match.queries.image_queries import ImageQueries


# TODO: these are just some helpful methods to start/delete partitions. Needs to be rewritten

class TanukaiImageQueries(ImageQueries):

    REDIS_PARTITIONS_KEY = 'partition_counts'
    REDIS_PARTITIONS_EXPIRATION_TIME = 3600  # seconds, 1 hour

    def __init__(self):
        super().__init__()
        self._redis = RedisDatabase()

    def remove_duplicates(self):
        elastic_search = Image.search(using=self._elasticsearch.database,
                                      index=config.elasticsearch_index)
        for number, result in enumerate(elastic_search.scan()):
            print(f'Processing {number}')
            source_id = result.source_id
            source_search = Image.search(using=self._elasticsearch.database,
                                         index=config.elasticsearch_index).query('term',
                                                                                 source_id=source_id)
            response = source_search.execute()
            if len(response) > 1:
                img_to_delete = response[1]
                img_to_delete_id = img_to_delete.meta.id
                print(f'Deleting {img_to_delete_id}')
                img_to_delete.delete(using=self._elasticsearch.database)
                status = self._milvus.database.delete_entity_by_id(config.milvus_collection_name,
                                                                   [int(img_to_delete_id)])
                if not status.OK():
                    raise Exception(
                        f'Could not remove from Milvus because of an error: {status.message}.')
        print('Done')
        return

    def move_to_partition(self):
        from milvus import MetricType
        import time
        # Image.init(using=self._elasticsearch.database)
        # status = self._milvus.database.drop_collection('images')
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
        elastic_search = Image.search(using=self._elasticsearch.database,
                                      index=config.elasticsearch_index)
        for number, result in enumerate(elastic_search.scan()):
            print(f'Processing {number}')
            image_id = result.meta.id
            status, vectors = self._milvus.database.get_entity_by_id(config.milvus_collection_name,
                                                                     [int(image_id)])
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
        elastic_search = Image.search(using=self._elasticsearch.database,
                                      index=config.elasticsearch_index).source(False)
        for number, result in enumerate(elastic_search.scan()):
            print(f'Processing {number}')
            result.update(
                using=self._elasticsearch.database,
                refresh=False,
                source_website='e621'
            )

    def get_partitions(self) -> dict:
        """
        Returns a dict with cached partition data (or sets it) using Redis (partition_tag and count)
        :return: dict, e.g. {'ebay': 5213, 'etsy': 1233}
        """
        cached_partitions = self._redis.database.hgetall(self.REDIS_PARTITIONS_KEY)
        if cached_partitions:
            return cached_partitions
        status, stats = self._milvus.database.get_collection_stats(config.milvus_collection_name)
        partitions = {i['tag']: i['row_count'] for i in stats['partitions'] if i['row_count'] > 0}
        self._add_partitions_to_cache(partitions)
        return partitions

    def _add_partitions_to_cache(self, partitions: dict) -> dict:
        self._redis.database.hmset(self.REDIS_PARTITIONS_KEY, partitions)
        self._redis.database.expire(
            self.REDIS_PARTITIONS_KEY,
            self.REDIS_PARTITIONS_EXPIRATION_TIME
        )
        return partitions
