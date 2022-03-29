from elasticsearch_dsl import Document, Keyword, Date, Object
import config

hash_object = Object(
    properties={f"hash_{i}": Keyword() for i in range(config.phash_size_result)}
)


class Image(Document):
    image_path = Keyword()
    timestamp = Date()
    hash = hash_object

    class Index:
        name = config.elasticsearch_index
        settings = {
            "number_of_shards": config.elasticsearch_shards,
            "number_of_replicas": config.elasticsearch_replicas,
        }
        type = "_doc"
