from elasticsearch_dsl import Document, Keyword, Text, Date, Object
import config

hash_object = Object(properties={f'hash_{i}': Keyword() for i in range(config.phash_size_result)})


class Image(Document):
    image_path = Keyword()
    timestamp = Date()
    hash = hash_object

    # source_website = Keyword()
    # source_url = Keyword()
    # source_id = Keyword()
    # source_created_at = Date()
    # source_tags = Object()
    # source_rating = Keyword()
    # source_description = Text()
    # source_image_url = Keyword()

    class Index:
        name = config.elasticsearch_index
        settings = {
            'number_of_shards': config.elasticsearch_shards,
            'number_of_replicas': config.elasticsearch_replicas
        }
        type = '_doc'
