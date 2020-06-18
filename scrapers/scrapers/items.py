import scrapy
from scrapy.loader.processors import MapCompose
from w3lib.html import remove_tags


def is_empty(value):
    if value:
        return value
    return None


def strip(value):
    if isinstance(value, str):
        value = value.strip()
    return value


def remove_html_tags(value):
    if isinstance(value, str):
        value = remove_tags(value)
    return value


class Image(scrapy.Item):
    website = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    created_at = scrapy.Field()
    tags = scrapy.Field()
    rating = scrapy.Field()
    description = scrapy.Field(input_processor=MapCompose(strip, remove_html_tags, is_empty))
    image_urls = scrapy.Field()
    images = scrapy.Field()
