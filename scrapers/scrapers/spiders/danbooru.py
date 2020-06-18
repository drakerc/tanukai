import json
import scrapy
from urllib.parse import urlencode
from scrapers.items import Image
from img_match.queries.databases import ElasticDatabase


class DanbooruScraper(scrapy.Spider):
    name = "danbooru"
    allowed_domains = ["danbooru.donmai.us"]
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
            'User-Agent': 'ImgSearch (drakeapp@gmail.com)'
        }
        query = {
            'limit': 120,
        }
        encoded_query = urlencode(query)
        url = f'https://danbooru.donmai.us/posts.json?{encoded_query}'
        yield scrapy.Request(url=url, callback=self.parse, headers=headers, dont_filter=True)

    def parse(self, response):
        posts = json.loads(response.body_as_unicode())
        first_post_id = posts[0].get('id')

        if 'page' not in response.url:
            self.state['highest_id'] = first_post_id
        for data in posts:
            source_id = data.get('id')

            first_id = self.state.get('first_id')
            if first_id and source_id == first_id:
                self.state['first_id'] = self.state['highest_id']
                print('Reached the last previously scraped item!')
                return

            created_at = data.get('created_at')
            tags = data.get('tag_string').split()
            authors = data.get('tag_string_artist').split()
            es_tags = {
                'general': tags,
                'artist': authors
            }
            rating = self.rating_mapping.get(data.get('rating'))
            image_url = data.get('large_file_url')
            if not image_url or '.webm' in image_url or '.swf' in image_url:
                continue
            image_urls = [image_url]

            image = Image(
                website='danbooru',
                url=f'https://danbooru.donmai.us/posts/{source_id}',
                id=source_id,
                created_at=created_at,
                tags=es_tags,
                rating=rating,
                image_urls=image_urls
            )
            yield image

        if not self.state.get('first_id') and 'page' not in response.url:
            self.state['first_id'] = first_post_id  # set the highest ID on the first scrape ever

        headers = {
            'User-Agent': 'ImgSearch (drakeapp@gmail.com)'
        }
        last_item_url = posts[-1].get('id')
        query = {
            'limit': 120,
            'page': f'b{last_item_url}'
        }
        encoded_query = urlencode(query)
        url = f'https://danbooru.donmai.us/posts.json?{encoded_query}'
        yield scrapy.Request(url=url, callback=self.parse, headers=headers, dont_filter=False)
