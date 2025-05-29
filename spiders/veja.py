import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem
from urllib.parse import urlparse


class VejaSpider(BaseSpider):
    name = "vejaspider"
    start_urls = ["https://veja.abril.com.br/"]
    allowed_domains = ["veja.abril.com.br"]

    def allow_url(self, url: str) -> bool:
        p = urlparse(url)
        path = p.path.rstrip('/')

        # 1) blacklist pure sections
        if path in {"/ofertas", "/videos", "/podcasts", "/fotos", "/especiais", "/colunistas"}:
            self.logger.info(f"Blacklisted URL: {url}")
            return False

        # 2) require at least two non-empty segments (section + slug)
        segments = [seg for seg in path.split('/') if seg]
        if len(segments) < 2:
            self.logger.info(f"Blacklisted URL: {url}")
            return False

        # 3) reject media files
        if "wp-content/uploads" in url:
            self.logger.info(f"Blacklisted URL: {url}")
            return False

        # 4) long slugs by hyphens or by character length
        slug = segments[-1]
        if slug.count('-') >= 3 or len(slug) > 30:
            return True

        return False

    def parse(self, response):
        # grab every <a> in *any* div
        links = response.css('a')
        self.logger.info(f"Found {len(links)} links")

        for link in links:
            raw = link.attrib.get("href")
            if not raw:
                continue

            # build an absolute URL, then strip fragments/queries
            full = response.urljoin(raw)
            full = full.split('#', 1)[0].split('?', 1)[0]

            if self.allow_url(full):
                yield URLItem(url=full)
