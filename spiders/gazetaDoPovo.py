import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem
from urllib.parse import urlparse



class GazetaDoPovoSpider(BaseSpider):
    name = "gazetadopovospider"
    start_urls = ["https://www.gazetadopovo.com.br/"]
    allowed_domains = ["gazetadopovo.com.br"]

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

    def allow_url(self, url: str) -> bool:
        p = urlparse(url)
        path = p.path.rstrip('/')

        # 1) blacklist pure sections
        if path in {"/videos", "/vozes", "/podcasts", "/newsletter", "/ebooks"}:
            self.logger.info(f"Blacklisted URL: {url}")
            return False

        # 2) require at least two non-empty segments (section + slug)
        segments = [seg for seg in path.split('/') if seg]
        if len(segments) < 2:
            self.logger.info(f"Blacklisted URL: {url}")
            return False

        slug = segments[-1]
        # 3a) long slugs by hyphens or 3b) by character length
        if slug.count('-') >= 3 or len(slug) > 30:
            return True

        return False

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
            )

    def parse(self, response):
        # grab every <a> in *any* div sibling after the header
        links = response.xpath(
            '//div[@id="pianoUnderHeader"]/following-sibling::div//a'
        )
        self.logger.info(f"Found {len(links)} links under pianoUnderHeader")

        for link in links:
            raw = link.attrib.get("href")
            if not raw:
                continue

            # build an absolute URL, then strip fragments/queries
            full = response.urljoin(raw)
            full = full.split('#', 1)[0].split('?', 1)[0]

            if self.allow_url(full):
                yield URLItem(url=full)
