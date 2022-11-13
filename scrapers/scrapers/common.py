from img_match.models.image import Image as ImgMatchImage
import config
from img_match.queries.databases import ElasticDatabase


def was_already_scraped(
    elasticsearch: ElasticDatabase, source_id: str, source_website: str
) -> bool:
    elastic_search = (
        ImgMatchImage.search(
            using=elasticsearch.database, index=config.elasticsearch_index
        )
        .query("term", source_website=source_website)
        .query("term", source_id=source_id)
    )
    count = elastic_search.count()
    return count >= 1
