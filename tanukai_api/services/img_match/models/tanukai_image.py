from elasticsearch_dsl import Keyword, Text, Date, Object
import config
from img_match.models.image import Image

hash_object = Object(
    properties={f"hash_{i}": Keyword() for i in range(config.phash_size_result)}
)


class TanukaiImage(Image):
    source_website = Keyword()
    source_url = Keyword()
    source_id = Keyword()
    source_created_at = Date()
    source_tags = Keyword(multi=True)
    source_rating = Keyword()
    source_description = Text()
    source_image_url = Keyword()
    source_category = Keyword()
    source_species = Keyword()
    source_gender = Keyword()
    source_author_url = Keyword()
    source_author_name = Keyword()
