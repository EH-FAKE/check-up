import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class AliadosBrasilSpider(BaseSpider):
    name = "aliadosbrasilspider"
    start_urls = ["https://www.aliadosbrasiloficial.com.br/"]
    allowed_domains = ["aliadosbrasiloficial.com.br"]

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
        for entry in response.css(".col-md-12 > a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
                )