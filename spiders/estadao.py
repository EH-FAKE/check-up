import scrapy
from scrapy.http import Request
from spiders.base import BaseSpider
from spiders.items import URLItem

class EstadaoSpider(BaseSpider):
    name = "estadaospider"
    start_urls = ["https://www.estadao.com.br/"]
    allowed_domains = ["estadao.com.br"]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
    }

    def allow_url(self, entry_url):
        # TODO: remover www.estadao.com.br/recomenda/
        # TODO: remover web-stories
        return entry_url.startswith("https://www.estadao.com.br") and len(entry_url) > 100

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)
