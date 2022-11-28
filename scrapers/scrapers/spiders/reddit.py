import json
from urllib.parse import urlencode

import scrapy
from helpers.imgur_downloader import imgur_downloader
from scrapers.items import Image
from datetime import datetime
import config
from img_match.queries.databases import ElasticDatabase
from scrapers.common import was_already_scraped

from img_match.queries.image_queries import ImageQueries


class RedditScraper(scrapy.Spider):
    name = "reddit"
    handle_httpstatus_list = [200, 201, 400, 403, 502]

    custom_settings = {
        "LOG_FILE": "reddit_logs.txt",
    }

    def __init__(self, **kwargs):
        self.param_ignore_scraped = False
        super().__init__(**kwargs)
        if config.INITIALIZE_DBS_IF_NOT_EXIST:
            ImageQueries().initialize_dbs_if_not_exist(self.name)  # kinda breaks the SRP rule
        self._elasticsearch = ElasticDatabase()

    def start_requests(self):
        if not hasattr(self, "param_subreddit"):
            self.param_subreddit = "fursuit"

        url_params = {
            "subreddit": self.param_subreddit,
            "size": "500"
        }

        yield scrapy.Request(
            url="https://api.pushshift.io/reddit/search/submission?" + urlencode(url_params),
            callback=self.parse_search_results,
        )

    def parse_search_results(self, response):
        json_response = json.loads(response.text)
        posts = json_response["data"]

        if not posts:
            self.logger.info("No more images found, ending scraping...")
            return

        for post in posts:
            source_id = post["id"]
            if was_already_scraped(self._elasticsearch, source_id, self.name):
                # self.logger.info("Image ID: %s already scraped.", source_id)
                if not self.param_ignore_scraped == "true":
                    self.logger.info(
                        "Duplicate image encountered, ending scraping...", source_id
                    )
                    # end the scraping the first time we see an already scraped image
                    return
                continue
            yield from self.parse_post(post)

        last_post_timestamp = post["created_utc"]
        last_timestamp_string = datetime.fromtimestamp(last_post_timestamp).strftime("%Y-%m-%d")
        self.logger.info(f"Scraping posts before {last_timestamp_string}")

        url_params = {
            "subreddit": self.param_subreddit,
            "size": "500",
            "before": last_post_timestamp
        }

        yield scrapy.Request(
            url="https://api.pushshift.io/reddit/search/submission?" + urlencode(url_params),
            callback=self.parse_search_results,
        )

    def parse_post(self, post):
        url = post["full_link"]
        source_id = post["id"]

        created_at = post["created_utc"]
        parsed_created_at = datetime.fromtimestamp(created_at)
        flair = post.get("link_flair_text")
        tags = [flair] if flair else []
        rating = "explicit" if post["over_18"] else "safe"
        description = post["title"]
        author_name = post["author"]

        media_metadata = post.get("media_metadata", [])
        if media_metadata:
            for media_item in media_metadata.values():  # Reddit gallery
                image_urls = media_item.get('p', [])
                if not image_urls:
                    continue
                high_quality_image_url = image_urls[-1]["u"].replace("amp;", '')
                image = Image(
                    website=self.name,
                    url=url,
                    id=source_id,
                    created_at=parsed_created_at.isoformat(),
                    tags=tags,
                    rating=rating,
                    description=description,
                    image_urls=[high_quality_image_url],
                    author_name=author_name
                )
                yield image
                self.logger.info(f"ADD: Adding image {high_quality_image_url}")
            return  # return

        preview_images = post.get("preview", {}).get("images", [])
        if preview_images:
            for preview_image in preview_images:  # New single images
                image_url = preview_image["source"]["url"].replace("amp;", '')
                image = Image(
                    website=self.name,
                    url=url,
                    id=source_id,
                    created_at=parsed_created_at.isoformat(),
                    tags=tags,
                    rating=rating,
                    description=description,
                    image_urls=[image_url],
                    author_name=author_name
                )
                yield image
                self.logger.info(f"ADD: Adding image {image_url}")
            return  # return

        is_reddit_media_domain = post.get("is_reddit_media_domain", False)
        if is_reddit_media_domain:
            image_url = post["url"].replace("amp;", '')
            image = Image(
                website=self.name,
                url=url,
                id=source_id,
                created_at=parsed_created_at.isoformat(),
                tags=tags,
                rating=rating,
                description=description,
                image_urls=[image_url],
                author_name=author_name
            )
            yield image
            self.logger.info(f"ADD: Adding image {image_url}")
        domain = post.get("domain")
        if "imgur" in domain:
            image_url = post["url"].replace("amp;", '')
            self.logger.info(f"IMGUR: Adding image {image_url}")

            imgur_links = imgur_downloader(image_url, True)
            for imgur_link in imgur_links:
                image = Image(
                    website=self.name,
                    url=url,
                    id=source_id,
                    created_at=parsed_created_at.isoformat(),
                    tags=tags,
                    rating=rating,
                    description=description,
                    image_urls=[imgur_link],
                    author_name=author_name
                )
                yield image
                self.logger.info(f"ADD: Adding image {image_url}")
