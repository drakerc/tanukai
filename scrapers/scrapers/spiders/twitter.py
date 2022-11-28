import json
from urllib.parse import urlencode

import scrapy
import arrow
from scrapers.items import Image
from datetime import datetime

import stweet as st

import config
from img_match.queries.databases import ElasticDatabase
from scrapers.common import was_already_scraped

from img_match.queries.image_queries import ImageQueries


class TwitterScraper(scrapy.Spider):
    name = "twitter"
    handle_httpstatus_list = [200, 201, 400, 403, 502]

    custom_settings = {
        "LOG_FILE": "twitter_logs.txt",
    }

    def __init__(self, **kwargs):
        self.param_ignore_scraped = False
        super().__init__(**kwargs)
        if config.INITIALIZE_DBS_IF_NOT_EXIST:
            ImageQueries().initialize_dbs_if_not_exist(self.name)  # kinda breaks the SRP rule
        self._elasticsearch = ElasticDatabase()

    def start_requests(self):
        # This is really stupid
        url_params = {
            "subreddit": "furry",
            "size": "1",
        }
        yield scrapy.Request(
            url="https://api.pushshift.io/reddit/search/submission?" + urlencode(url_params),
            callback=self.start_req,
        )

    def start_req(self, response):
        arrow_start = arrow.utcnow()
        arrow_end = arrow.utcnow().shift(days=-1)
        yield from self.scrape_twitter_items(arrow_start, arrow_end)

    def scrape_twitter_items(self, arrow_start, arrow_end):
        search_tweets_task = st.SearchTweetsTask(
            any_word='#fursuit #fursuitfriday #fursuiter',
            until=arrow_start,
            since=arrow_end,
            # tweets_limit=50
        )
        output_tweets = st.CollectorRawOutput()
        output_users = st.CollectorRawOutput()
        st.TweetSearchRunner(search_tweets_task=search_tweets_task,
                             tweet_raw_data_outputs=[output_tweets],
                             user_raw_data_outputs=[output_users]
                             ).run()
        tweets = output_tweets.get_raw_list()
        yield from self.parse_search_results(tweets, arrow_end)

    def parse_search_results(self, tweets, ended_on):
        if not tweets:
            self.logger.info(f"FINISH: No more images left, ending...")
            return
        lowest_date = None
        for tweet in tweets:
            json_tweet = json.loads(tweet.raw_value)

            created_at = json_tweet["created_at"]  # "Fri Sep 17 14:57:00 +0000 2021"
            parsed_created_at = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            if not lowest_date or parsed_created_at < lowest_date:
                lowest_date = parsed_created_at

            yield from self.parse_tweet(json_tweet)

        arrow_date_start = ended_on
        arrow_date_end = ended_on.shift(days=-1)
        yield from self.scrape_twitter_items(arrow_date_start, arrow_date_end)

    def parse_tweet(self, tweet):
        media_images = tweet.get("entities", {}).get("media", [])
        for media_image in media_images:
            url = media_image["url"]
            image_url = media_image["media_url"]
            source_id = media_image["id_str"]

            if was_already_scraped(self._elasticsearch, source_id, self.name):
                if not self.param_ignore_scraped == "true":
                    self.logger.info(
                        "Duplicate image encountered, ending scraping...", source_id
                    )
                    # end the scraping the first time we see an already scraped image
                    return
                continue

            created_at = tweet["created_at"]  # "Fri Sep 17 14:57:00 +0000 2021"
            parsed_created_at = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            hashtags = tweet.get("entities", {}).get("hashtags", [])
            tags = [hashtag["text"] for hashtag in hashtags]

            author_name = media_image.get("expanded_url", "").split('/')[3]
            description = tweet.get("full_text")
            is_sensitive = tweet.get("possibly_sensitive", False)
            rating = "explicit" if is_sensitive else "safe"

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
            self.logger.info(f"ADD: Adding image {url}")
