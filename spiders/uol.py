import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem
from urllib.parse import urlparse


class UOLSpider(BaseSpider):
    name = "uolspider"
    start_urls = ["https://www.uol.com.br/"]
    allowed_domains = ["uol.com.br"]

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

        # Get non-empty path segments
        segments = [seg for seg in path.split('/') if seg]
        if len(segments) < 2:
            self.logger.info(f"URL com menos de 2 segmentos: {url}")
            return False

        # Whitelist de seções conhecidas que contêm notícias
        news_sections = {
            'noticias',
            'economia/noticias',
            'esporte/noticias',
            'esporte/futebol',
            'carros/noticias',
            'economia/agronegocio',
            'economia/mercados',
            'economia/empregos',
            'politica',
            'mundo',
            'tecnologia/noticias',
            'economia/folha',
            'esporte/folha'
        }

        # Verifica se o início do path está na whitelist
        path_start = '/'.join(segments[:2])
        if path_start not in news_sections:
            self.logger.info(f"Seção não está na whitelist: {url}")
            return False

        # Verifica se o último segmento (slug) tem características de notícia
        slug = segments[-1]
        if not (slug.count('-') >= 3 and len(slug) > 20):
            self.logger.info(f"Slug não tem padrão de notícia: {url}")
            return False

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
