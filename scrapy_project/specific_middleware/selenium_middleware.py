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
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from web_render.base.abstract import SeleniumRender, make_selenium_webdriver
# useful for handling different item types with a single interface
from selenium import webdriver


class SeleniumDownloaderMiddleware:

    @staticmethod
    def make_selenium_webdriver(config: dict):
        co = Options()
        if config.get("PROXY_SERVER"):
            co.add_argument(f"--proxy-server={config['PROXY_SERVER']}")
        co.add_argument('--disable-blink-features=AutomationControlled')
        # co.add_argument('--no-sandbox')
        # co.add_argument('--disable-dev-shm-usage')
        co.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
        co.add_experimental_option("excludeSwitches", ["enable-automation"])
        co.add_experimental_option('useAutomationExtension', False)
        co.add_argument("start-maximized")

        chrome_prefs = {}
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        co.add_experimental_option("prefs", chrome_prefs)

        download_driver = Service(ChromeDriverManager(
            driver_version=config.get('CHROME_DRIVER_VERSION')
        ).install())

        driver = webdriver.Chrome(service=download_driver, options=co)
        return driver

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
        self.render = SeleniumRender(make_selenium_webdriver(settings), timeout_web_wait=20)

    def process_request(self, request, spider):
        if not request.meta.get("web_render"):
            return None

        self.render.browser.get(request.url)
        if request.meta.get("web_wait"):
            try:
                self.render._web_wait(request.meta.get("web_wait"))
            except TimeoutException as err:
                raise IgnoreRequest(f"{err}\n{request.url} not items.")

        # Создайте объект HtmlResponse, чтобы передать его обратно в паук
        response = HtmlResponse(
            url=request.url,
            body=self.render.get_content(),
            encoding='utf-8',
            request=request
        )

        return response

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def spider_closed(self):
        self.render.quit()
