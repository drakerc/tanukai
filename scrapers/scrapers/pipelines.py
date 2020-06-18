# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib

from PIL import Image

from drawsearch.drawsearch_image import DrawsearchImage
from img_match.img_match import ImgMatch
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes
from io import BytesIO
import config


class ProcessingPipeline:
    image_match = None

    def open_spider(self, spider):
        self.image_match = ImgMatch()

    def process_item(self, item, spider):
        image = item.get('images')[0]
        full_path = image['path']
        image_path = full_path[len('full/'):]  # without full
        pil_image = Image.open(f"{config.images_path}/full/{image_path}")
        self.image_match.add_image(
            path=image_path,
            img=pil_image,
            partition_tag=item.get('website'),
            image_model=DrawsearchImage,
            source_website=item.get('website'),
            source_url=item.get('url'),
            source_id=item.get('id'),
            source_created_at=item.get('created_at'),
            source_tags=item.get('tags'),
            source_rating=item.get('rating'),
            source_description=item.get('description'),
            source_image_url=image['url']
        )
        return item

    def close_spider(self, spider):
        pass


class CustomImagesPipeline(ImagesPipeline):

    quality = 80
    max_height = 4000
    max_width = 4000

    def convert_image(self, image, size=None):
        if image.format == 'PNG' and image.mode == 'RGBA':
            background = Image.new('RGBA', image.size, (255, 255, 255))
            background.paste(image, image)
            image = background.convert('RGB')
        elif image.mode == 'P':
            image = image.convert("RGBA")
            background = Image.new('RGBA', image.size, (255, 255, 255))
            background.paste(image, image)
            image = background.convert('RGB')
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        img_width, img_height = image.size
        if img_width > self.max_width or img_height > self.max_height:
            size = (self.max_width, self.max_height)
        if size:
            image = image.copy()
            image.thumbnail(size, Image.ANTIALIAS)

        buf = BytesIO()
        image.save(buf, 'JPEG', quality=self.quality)
        return image, buf

    def file_path(self, request, response=None, info=None):
        spider_name = info.spider.name
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return 'full/%s/%s/%s/%s.jpg' % (spider_name, image_guid[0:2], image_guid[2:4], image_guid)

    def thumb_path(self, request, thumb_id, response=None, info=None):
        spider_name = info.spider.name
        thumb_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return 'thumbs/%s/%s/%s/%s/%s.jpg' % (thumb_id, spider_name, thumb_guid[0:2], thumb_guid[2:4], thumb_guid)
