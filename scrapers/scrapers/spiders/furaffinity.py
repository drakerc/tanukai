from datetime import datetime

import scrapy
from scrapers.items import Image
import config
from img_match.queries.databases import ElasticDatabase
from scrapers.common import was_already_scraped


class FurAffinityScraper(scrapy.Spider):
    name = "furaffinity"
    allowed_domains = ["furaffinity.net"]
    handle_httpstatus_list = [200, 201, 403]
    rating_mapping = {"General": "safe", "Mature": "questionable", "Adult": "explicit"}
    cookies = {"a": config.FURAFFINITY_COOKIE_A, "b": config.FURAFFINITY_COOKIE_B}

    def __init__(self, **kwargs):
        self.param_ignore_scraped = False
        super().__init__(**kwargs)
        self._elasticsearch = ElasticDatabase()

    def start_requests(self):
        url = "https://www.furaffinity.net"
        yield scrapy.Request(
            url=url,
            callback=self.parse_homepage,
            dont_filter=True,
            cookies=self.cookies,
        )

    def parse_homepage(self, response):
        latest_image_id = response.xpath(
            '//section[@id="gallery-frontpage-submissions"]/figure[1]/@id'
        ).get()  # e.g. sid-46458850
        latest_image_id = latest_image_id.split("-")[1]

        yield scrapy.Request(
            url=f"https://www.furaffinity.net/view/{latest_image_id}",
            callback=self.parse_image,
            cookies=self.cookies,
        )

    def parse_image(self, response):
        url = response.url
        source_id = url.split("/")[-1]
        next_image_id = int(source_id) - 1

        if was_already_scraped(self._elasticsearch, source_id, self.name):
            if not self.param_ignore_scraped == "true":
                # end the scraping the first time we see an already scraped image
                return
            yield scrapy.Request(
                url=f"https://www.furaffinity.net/view/{next_image_id}",
                callback=self.parse_image,
                cookies=self.cookies,
            )
            return

        created_at = response.xpath(
            '//div[@class="submission-id-sub-container"]/strong/span[@class="popup_date"]/@title'
        ).get()
        if not created_at:
            # Image does not exist (e.g. system error)
            # TODO: add logging
            yield scrapy.Request(
                url=f"https://www.furaffinity.net/view/{next_image_id}",
                callback=self.parse_image,
                cookies=self.cookies,
            )
            return
        parsed_created_at = datetime.strptime(
            created_at, "%b %d, %Y %I:%M %p"
        )  # Mar 22, 2022 04:53 PM
        tag_list = response.xpath(
            '//div[@class="section-body"]/span[@class="tags"]/a/text()'
        ).getall()
        tags = {"general": tag_list}
        rating = self.rating_mapping.get(
            response.xpath('//div[@class="rating"]/span/text()').get().strip()
        )
        description = response.xpath(
            '//meta[@property="og:description"]/@content'
        ).get()
        image_url = "https:" + response.xpath('//img[@id="submissionImg"]/@src').get()

        image = Image(
            website=self.name,
            url=url,
            id=source_id,
            created_at=parsed_created_at.isoformat(),
            tags=tags,
            rating=rating,
            description=description,
            image_urls=[image_url],
        )
        yield image

        yield scrapy.Request(
            url=f"https://www.furaffinity.net/view/{next_image_id}",
            callback=self.parse_image,
            cookies=self.cookies,
        )
