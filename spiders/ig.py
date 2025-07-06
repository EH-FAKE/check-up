import scrapy
from scrapy_playwright.page import PageMethod

from scrapy_playwright.page import PageMethod
from spiders.base import BaseSpider
from spiders.items import URLItem


class IGSpider(BaseSpider):
    name = "igspider"
    start_urls = ["https://www.ig.com.br/"]
    allowed_domains = ["ig.com.br"]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "firefox",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60 * 1000,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 4,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    "playwright": True,
                    "playwright_page_coroutines": [
                        PageMethod("wait_for_load_state", "load")
                    ],
                },
                dont_filter=True,
            )

    def parse(self, response):
        self.logger.info(f"Visitando: {response.url}")

        for entry in response.css("a.title"):
            url = entry.attrib.get("href")
            if url:
                url = response.urljoin(url)

                yield URLItem(url=url)
