import scrapy
from dateutil import relativedelta
from scrapers.items import Image
from datetime import datetime
import config
from img_match.queries.databases import ElasticDatabase
from scrapers.common import was_already_scraped

from img_match.queries.image_queries import ImageQueries

FA_MAXIMUM_RESULTS = 5000
FA_RESULTS_PER_PAGE = 48
LAST_POSSIBLE_PAGE = int(FA_MAXIMUM_RESULTS / FA_RESULTS_PER_PAGE)
REQUESTS_START_DATE = datetime(2010, 1, 1)


class FurAffinityScraper(scrapy.Spider):
    name = "furaffinity"
    allowed_domains = ["furaffinity.net"]
    handle_httpstatus_list = [200, 201, 400, 403, 502]
    rating_mapping = {"General": "safe", "Mature": "questionable", "Adult": "explicit"}
    cookies = {"a": config.FURAFFINITY_COOKIE_A, "b": config.FURAFFINITY_COOKIE_B}

    custom_settings = {
        "LOG_FILE": "furaffinity_logs.txt",
    }

    def __init__(self, **kwargs):
        self.param_ignore_scraped = False
        super().__init__(**kwargs)
        if config.INITIALIZE_DBS_IF_NOT_EXIST:
            ImageQueries().initialize_dbs_if_not_exist(self.name)  # kinda breaks the SRP rule
        self._elasticsearch = ElasticDatabase()

    def start_requests(self):
        end_date = REQUESTS_START_DATE + relativedelta.relativedelta(months=1)

        yield self._get_new_month_request(REQUESTS_START_DATE, end_date)

    def _get_new_month_request(self, start_date: datetime, end_date: datetime, scrape_next_month: bool = True):
        post_params = {
            "reset_page": "1",
            "page": "1",
            "order-by": "date",
            "order-direction": "desc",
            "range": "manual",
            "range_from": start_date.strftime("%Y-%m-%d"),
            "range_to": end_date.strftime("%Y-%m-%d"),
            "rating-general": "1",
            "rating-mature": "1",
            "rating-adult": "1",
            "type-art": "1",
            "type-photo": "1",
            "mode": "extended",
            "q": "fursuit | fursuiter | fursuiting",
            "do_search": "Search"
        }
        return scrapy.FormRequest(
            url="https://www.furaffinity.net/search/",
            method="POST",
            callback=self.parse_search_results,
            formdata=post_params,
            cookies=self.cookies,
            meta={'start_date': start_date, 'end_date': end_date, 'page': 0, 'scrape_next_month': scrape_next_month}
        )

    def parse_search_results(self, response):
        start_date = response.meta["start_date"]
        end_date = response.meta["end_date"]

        current_date = datetime.now()
        if start_date > current_date:
            # If our start date is in the future, FA will start returning all results. So we stop
            # here
            self.logger.info(f"NEXT MONTH: Scraping ends on Start Date: {start_date}")
            return

        self.logger.info(
            f"PAGE: Scraping page {response.meta['page']} between {start_date.strftime('%Y-%m-%d')}"
            f" and {end_date.strftime('%Y-%m-%d')}"
        )

        scrape_next_month = response.meta.get('scrape_next_month', True)
        query_stats = response.xpath('//div[@id="query-stats"]/text()').getall()[-1]
        query_stats_total = int(query_stats.split()[4][:-2])
        if query_stats_total > FA_MAXIMUM_RESULTS and response.meta["page"] == LAST_POSSIBLE_PAGE and scrape_next_month:
            # This is hacky. FA does not return more than 5000 results. So in order to get all
            # of them, we will run another scrape from the middle of the month to the end of the
            # month (so we will limit the amount of results) and hope for the best
            next_start_date = start_date + relativedelta.relativedelta(days=15)
            next_end_date = end_date

            self.logger.info(f"OVERFLOW: Scraping month {next_start_date} to {next_end_date}."
                             f" Total results: {query_stats_total}")
            yield self._get_new_month_request(next_start_date, next_end_date, False)

        image_urls = response.xpath(
            '//section[@id="gallery-search-results"]/figure/b/u/a/@href'
        ).getall()

        for link in image_urls:
            source_id = link.split("/")[-2]
            if was_already_scraped(self._elasticsearch, source_id, self.name):
                # self.logger.info("Image ID: %s already scraped.", source_id)
                if not self.param_ignore_scraped == "true":
                    self.logger.info(
                        "Duplicate image encountered, ending scraping...", source_id
                    )
                    # end the scraping the first time we see an already scraped image
                    return
                continue
            yield scrapy.Request(
                url=f"https://www.furaffinity.net/view/{source_id}",
                callback=self.parse_image,
                    cookies=self.cookies,
                )

        next_results_button = response.xpath(
            '//button[@name="next_page"]/@class'
        ).get()
        no_more_results = False
        if len(image_urls) == 0 or (next_results_button and "disabled" in next_results_button):
            no_more_results = True

        if no_more_results and scrape_next_month:
            # go to the next month
            next_start_date = start_date + relativedelta.relativedelta(months=1)
            next_end_date = next_start_date + relativedelta.relativedelta(months=1)

            self.logger.info(f"NEXT MONTH: Scraping month {next_start_date} to {next_end_date}")
            yield self._get_new_month_request(next_start_date, next_end_date)
            return

        next_page = response.meta["page"] + 1
        if next_page > LAST_POSSIBLE_PAGE:
            return

        post_params = {
            "page": str(next_page),
            "next_page": "Next",
            "q": "fursuit | fursuiter | fursuiting | suit",
            "order-by": "date",
            "order-direction": "desc",
            "range": "manual",
            "range_from": start_date.strftime("%Y-%m-%d"),
            "range_to": end_date.strftime("%Y-%m-%d"),
            "rating-general": "1",
            "rating-mature": "1",
            "rating-adult": "1",
            "type-art": "1",
            "type-photo": "1",
            "mode": "extended",
        }

        yield scrapy.FormRequest(
            url="https://www.furaffinity.net/search/",
            method="POST",
            callback=self.parse_search_results,
            formdata=post_params,
            cookies=self.cookies,
            meta={'start_date': start_date, 'end_date': end_date, 'page': next_page}
        )

    def parse_image(self, response):
        url = response.url
        source_id = url.split("/")[-1]
        if response.status != 200:
            self.logger.warn(
                "Scraper returned non-200 code: %s for page: %s",
                response.status,
                response.url,
            )
            # FA sometimes returns 404/400/502 on missing images. Then we will continue to the next one
            return

        created_at = response.xpath(
            '//div[@class="submission-id-sub-container"]/strong/span[@class="popup_date"]/@title'
        ).get()
        if not created_at:
            # Image does not exist (e.g. system error)
            self.logger.warn(
                "Image %s does not have created_at, ignoring...", source_id
            )
            return
        parsed_created_at = datetime.strptime(
            created_at, "%b %d, %Y %I:%M %p"
        )  # Mar 22, 2022 04:53 PM
        tag_list = response.xpath(
            '//div[@class="section-body"]/span[@class="tags"]/a/text()'
        ).getall()
        tags = tag_list
        rating = self.rating_mapping.get(
            response.xpath('//div[@class="rating"]/span/text()').get().strip()
        )
        description = response.xpath(
            '//meta[@property="og:description"]/@content'
        ).get()
        image_url = "https:" + response.xpath('//img[@id="submissionImg"]/@src').get()

        category_main = response.xpath(
            '//span[@class="category-name"]/text()'
        ).get()
        category_secondary = response.xpath(
            '//span[@class="type-name"]/text()'
        ).get()

        category_string = f"{category_main} > {category_secondary}"
        if "art" in category_string.lower():
            return

        species = response.xpath(
            "//strong[@class='highlight' and ./text()='Species']/parent::div/span/text()"
        ).get()

        gender = response.xpath(
            "//strong[@class='highlight' and ./text()='Gender']/parent::div/span/text()"
        ).get()

        author_url = response.xpath(
            "//div[@class='submission-id-avatar']/a/@href"
        ).get()
        author_name = response.xpath(
            "//div[@class='submission-id-sub-container']/a/strong/text()"
        ).get()

        image = Image(
            website=self.name,
            url=url,
            id=source_id,
            created_at=parsed_created_at.isoformat(),
            tags=tags,
            rating=rating,
            description=description,
            image_urls=[image_url],
            category=category_string,
            species=species,
            gender=gender,
            author_url=f"https://www.furaffinity.net{author_url}",
            author_name=author_name
        )
        self.logger.info(f"ADD: Adding image {image_url}")

        yield image
