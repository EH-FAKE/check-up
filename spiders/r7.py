import re
import scrapy
from spiders.base import BaseSpider
from spiders.items import URLItem


class R7Spider(BaseSpider):
    name = "r7spider"
    start_urls = ["https://www.r7.com/"]
    allowed_domains = ["r7.com"]

    def allow_url(self, entry_url):
        return (
            entry_url.startswith("https://")
            and len(entry_url) > 100
            and re.match(
                r"https://(entretenimento|esportes|record|noticias)\.r7\.com", entry_url
            )
        )

    def parse(self, response):
        seen = set()
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if url and url not in seen and self.allow_url(url):
                seen.add(url)
                yield URLItem(url=url)
                yield scrapy.Request(url=url, callback=self.parse)

