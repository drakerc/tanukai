import json

import scrapy
from urllib.parse import urlencode
from scrapers.items import Image
from scrapy import Request
from scrapy.http import TextResponse

from img_match.queries.databases import ElasticDatabase
from scrapers.common import was_already_scraped


class E621Scraper(scrapy.Spider):
    name = "e621"
    allowed_domains = ["e621.net"]
    handle_httpstatus_list = [200, 201, 403]
    rating_mapping = {"s": "safe", "q": "questionable", "e": "explicit"}
    headers = {
        "User-Agent": "Tanukai.com Furry Scraper v0.1 (drakepp at gmail dot com) (user: drakerc)",
        "Content-Type": "application/json",
    }
    custom_settings = {
        "LOG_FILE": "e621_logs.txt",
    }

    def __init__(self, **kwargs):
        self.param_ignore_scraped = False
        super().__init__(**kwargs)
        self._elasticsearch = ElasticDatabase()

    def start_requests(self):
        query = {
            "limit": 120,
        }
        encoded_query = urlencode(query)
        url = f"https://e621.net/posts.json?{encoded_query}"
        yield scrapy.Request(
            url=url, callback=self.parse, headers=self.headers, dont_filter=True
        )

    def parse(self, response: TextResponse, **kwargs):
        data_json = json.loads(response.text)
        posts = data_json.get("posts", [])
        if not posts:
            self.logger.info(
                "Scraper returned empty results list for URL.", response.url
            )
            return

        last_post_id = posts[-1].get("id")

        for data in data_json.get("posts"):
            source_id = data.get("id")

            if was_already_scraped(self._elasticsearch, source_id, self.name):
                self.logger.info("Image ID: %s already scraped.", source_id)
                if not self.param_ignore_scraped == "true":
                    self.logger.info(
                        "Duplicate image encountered, ending scraping...", source_id
                    )
                    # end the scraping the first time we see an already scraped image
                    return
                yield self._request_next_page(last_post_id)
                return
            created_at = data.get("created_at")
            tags = data.get("tags")
            rating = self.rating_mapping.get(data.get("rating"))
            description = data.get("description")
            image_url = data.get("file").get("url")
            if not image_url or ".webm" in image_url or ".swf" in image_url:
                self.logger.warn(
                    "Image %s in not allowed format, URL: %s, ignoring...",
                    source_id,
                    image_url,
                )
                continue
            image_urls = [image_url]

            image = Image(
                website=self.name,
                url=f"https://e621.net/posts/{source_id}",
                id=source_id,
                created_at=created_at,
                tags=tags,
                rating=rating,
                description=description,
                image_urls=image_urls,
            )
            yield image

        yield self._request_next_page(last_post_id)

    def _request_next_page(self, image_id: int) -> Request:
        query = {"limit": 120, "page": f"b{image_id}"}
        encoded_query = urlencode(query)
        url = f"https://e621.net/posts.json?{encoded_query}"

        return scrapy.Request(url=url, headers=self.headers, callback=self.parse)
