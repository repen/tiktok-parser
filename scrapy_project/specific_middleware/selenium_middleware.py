# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
# useful for handling different item types with a single interface
from selenium import webdriver
from data_diger.selenium import auth_http_proxy


def make_chrome_driver(config: dict) -> webdriver.Chrome:
    options = Options()

    if config.get('HEADLESS'):
        options.add_argument('--headless=new')

    if config.get("proxy"):
        encoded_extension = auth_http_proxy(
            config["proxy"]["host"],
            config["proxy"]["port"],
            config["proxy"]["username"],
            config["proxy"]["password"],
        )
        options.add_encoded_extension(encoded_extension)

    chrome_prefs = dict()
    if config.get("DISABLE_IMAGE"):
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

    if config.get("LOGGING_PREFS"):
        options.set_capability("goog:loggingPrefs", config.get("LOGGING_PREFS"))

    options.add_experimental_option("prefs", chrome_prefs)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument('--disable-notifications')
    # options.add_argument("start-maximized")

    if config.get("STRATEGY"):
        # Установка pageLoadStrategy на 'eager' или 'none'
        options.page_load_strategy = config.get("STRATEGY")  # или 'none' в зависимости от ваших требований

    if config.get("LANGUAGE"):
        # example en,en_US
        chrome_prefs['intl.accept_languages'] = config.get("LANGUAGE")

    driver = webdriver.Remote(
        command_executor=f"{config.get('COMMAND_EXECUTOR')}/wd/hub",
        options=options
    )
    return driver


class SeleniumDownloaderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        settings = crawler.spider.custom_settings.copy()
        settings.update(crawler.settings)
        target = cls(settings)
        crawler.signals.connect(target.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(target.spider_closed, signal=signals.spider_closed)
        return target

    def __init__(self, settings):
        self.spider_opened = None
        self.driver = make_chrome_driver(settings)

    def process_request(self, request, spider):
        if not request.meta.get("driver"):
            return None

        self.driver.get(request.url)
        if request.meta.get("web_wait"):
            breakpoint()
            raise NotImplemented("web wait")
            # try:
            #     self.render._web_wait(request.meta.get("web_wait"))
            # except TimeoutException as err:
            #     raise IgnoreRequest(f"{err}\n{request.url} not items.")

        # Создайте объект HtmlResponse, чтобы передать его обратно в паук
        response = HtmlResponse(
            url=request.url,
            body=self.driver.page_source,
            encoding='utf-8',
            request=request
        )

        return response

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def spider_closed(self):
        self.driver.quit()
