import json
import scrapy
from urllib.parse import urlencode
from scrapers.items import Image
import config
from img_match.queries.databases import ElasticDatabase
from img_match.models.image import Image as ImgMatchImage


class E621Scraper(scrapy.Spider):
    name = "e621"
    allowed_domains = ["e621.net"]
    handle_httpstatus_list = [200, 201, 403]
    rating_mapping = {
        's': 'safe',
        'q': 'questionable',
        'e': 'explicit'
    }

    def __init__(self):
        self._elasticsearch = ElasticDatabase()

    def start_requests(self):
        headers = {
            'User-Agent': 'ImgSearch (e621 user: drakerc)'
        }
        query = {
            'limit': 120,
        }
        encoded_query = urlencode(query)
        url = f'https://e621.net/posts.json?{encoded_query}'
        yield scrapy.Request(url=url, callback=self.parse, headers=headers, dont_filter=True)

        query = {
            'limit': 120,
            'page': f'b1747786'
        }
        encoded_query = urlencode(query)
        url = f'https://e621.net/posts.json?{encoded_query}'
        yield scrapy.Request(url=url, callback=self.parse, headers=headers, dont_filter=False)

    def parse(self, response):
        data_json = json.loads(response.body_as_unicode())
        posts = data_json.get('posts')
        first_post_id = posts[0].get('id')

        if 'page' not in response.url:
            self.state['highest_id'] = first_post_id
        for data in data_json.get('posts'):
            source_id = data.get('id')

            first_id = self.state.get('first_id')
            if first_id and source_id == first_id:
                self.state['first_id'] = self.state['highest_id']
                print('Reached the last previously scraped item!')
                return

            was_already_scraped = self._was_already_scraped(source_id)
            if was_already_scraped:
                print('was already scraped!')
                return
            created_at = data.get('created_at')
            tags = data.get('tags')
            rating = self.rating_mapping.get(data.get('rating'))
            description = data.get('description')
            image_url = data.get('file').get('url')
            if not image_url or '.webm' in image_url or '.swf' in image_url:
                continue
            image_urls = [image_url]

            image = Image(
                website='e621',
                url=f'https://e621.net/posts/{source_id}',
                id=source_id,
                created_at=created_at,
                tags=tags,
                rating=rating,
                description=description,
                image_urls=image_urls
            )
            yield image

        if not self.state.get('first_id') and 'page' not in response.url:
            self.state['first_id'] = first_post_id  # set the highest ID on the first scrape ever

        headers = {
            'User-Agent': 'ImgSearch (e621 user: drakerc)'
        }
        last_item_url = posts[-1].get('id')
        query = {
            'limit': 120,
            'page': f'b{last_item_url}'
        }
        encoded_query = urlencode(query)
        url = f'https://e621.net/posts.json?{encoded_query}'
        yield scrapy.Request(url=url, callback=self.parse, headers=headers, dont_filter=False)

    def _was_already_scraped(self, source_id):
        elastic_search = ImgMatchImage.search(using=self._elasticsearch.database,
                                              index=config.elasticsearch_index) \
            .query('term', source_id=source_id)
        count = elastic_search.count()
        return count >= 1
