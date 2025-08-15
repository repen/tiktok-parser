import json

import scrapy

import scrapy_project.spiders.user_detail.settings as settings
from scrapy_project.common.utils import load_settings


# Импортируем настройки как словарь
settings_dict = load_settings(settings)


class UserDetailSpider(scrapy.Spider):
    name = "user_detail"
    allowed_domains = ["tiktok.com"]
    start_urls = ["https://tiktok.com"]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {},
        'FEED_EXPORT_FIELDS': [],
        'ROBOTSTXT_OBEY': False,
        'DEFAULT_REQUEST_HEADERS': {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "https://www.google.com/",
        }
    }

    custom_settings.update(settings_dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input = self.__dict__.get("input")
        if self.input is None:
            raise ValueError("input cannot be None")
        self._items = [x.strip() for x in self.input.split(',')]

    def start_requests(self):
        for item in self._items:
            yield scrapy.Request(
                f"https://tiktok.com/{item}", callback=self.parse,
            )

    def parse(self, response):
        script = response.css('script#__UNIVERSAL_DATA_FOR_REHYDRATION__::text')
        data = json.loads(script.get())
        user_detail = data["__DEFAULT_SCOPE__"]["webapp.user-detail"]
        yield user_detail
