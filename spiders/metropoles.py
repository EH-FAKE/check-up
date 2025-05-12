import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class MetropolesSpider(BaseSpider):
    name = "metropolesspider"
    start_urls = ["https://www.metropoles.com/"]
    allowed_domains = ["metropoles.com"]

    custom_settings = {
        **BaseSpider.custom_settings,
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 3,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cache-Control": "max-age=0",
        }
    }

    def allow_url(self, entry_url):
        return True

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
            )

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css(".noticia__titulo > a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
                )
