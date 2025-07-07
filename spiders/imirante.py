import scrapy
import logging

from spiders.base import BaseSpider
from spiders.items import URLItem


class ImiranteSpider(BaseSpider):
    name = "imirantespider"
    start_urls = ["https://imirante.com"]
    allowed_domains = ["imirante.com"]
    max_urls = 70
    _urls_collected = 0

    def allow_url(self, entry_url):
        return True

    def start_requests(self):
        self._urls_collected = 0
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
            )

    def parse(self, response):
        if self._urls_collected >= self.max_urls:
            logging.info(f"Limite de {self.max_urls} URLs atingido. Parando coleta.")
            return

        url_item = URLItem()
        for entry in response.css("a[href*='/noticias/']"):
            if self._urls_collected >= self.max_urls:
                return

            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                self._urls_collected += 1
                logging.info(f"URL coletada {self._urls_collected}/{self.max_urls}: {url}")
                url_item["url"] = url
                yield url_item
                
                if self._urls_collected < self.max_urls:
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse,
                        meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
                    )