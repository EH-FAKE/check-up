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

        # 1) blacklist pure sections and non-article pages
        blacklist = {
            "/ofertas", "/videos", "/podcasts", "/fotos", "/especiais", "/colunistas",
            "/autor", "/categoria", "/tag", "/busca", "/newsletter", "/assine",
            "/institucional", "/fale-conosco", "/termos-de-uso", "/politica-de-privacidade"
        }
        if path in blacklist or any(segment in blacklist for segment in path.split('/')):
            self.logger.info(f"Blacklisted section URL: {url}")
            return False

        # 2) require at least two non-empty segments (section + slug)
        segments = [seg for seg in path.split('/') if seg]
        if len(segments) < 2:
            self.logger.info(f"Too few segments URL: {url}")
            return False

        # 3) reject media files and special pages
        if any(x in url.lower() for x in ["wp-content/uploads", "wp-json", "feed", "rss", "xml", "pdf"]):
            self.logger.info(f"Blacklisted media/special URL: {url}")
            return False

        # 4) require URL pattern typical of news articles
        # - must have a section (like 'brasil', 'economia', etc)
        # - must have a descriptive slug with hyphens
        slug = segments[-1]
        if not (3 <= slug.count('-') <= 10 and 20 <= len(slug) <= 150):
            self.logger.info(f"Invalid slug pattern URL: {url}")
            return False

        # 5) reject URLs with query parameters or fragments
        if '?' in url or '#' in url:
            self.logger.info(f"URL with query/fragment: {url}")
            return False

        return True

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
