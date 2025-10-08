import re

import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class AgoraNoValeSpider(BaseSpider):
    name = "agoranovalespider"
    start_urls = ["https://agoranovale.com.br/"]
    allowed_domains = ["agoranovale.com.br", "www.agoranovale.com.br"]

    custom_settings = {
        **BaseSpider.custom_settings,
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36",
        },
        "CONCURRENT_REQUESTS": 4,
    }

    BLACKLISTED_SECTIONS = {
        
    }

    def allow_url(self, url: str) -> bool:
        if not url:
            return False

        # Normaliza URL, remove fragmentos e query
        url = url.split('#', 1)[0].split('?', 1)[0]

        # Considera apenas links do domínio agoranovale.com.br
        if not re.match(r"https?://(www\.)?agoranovale\.com\.br/", url):
            return False

        path = re.sub(r"https?://[^/]+", "", url)
        segments_norm = [s.lower() for s in path.strip("/").split("/") if s]

        # Blacklist por prefixo em qualquer segmento
        blacklist_prefixes = {p.lstrip('/').lower() for p in self.BLACKLISTED_SECTIONS}
        for seg in segments_norm:
            if any(seg.startswith(pref) for pref in blacklist_prefixes):
                return False

        # Exige ao menos dois segmentos (seção + slug)
        segments = [s for s in path.split('/') if s]
        if len(segments) < 2:
            return False

        slug = segments[-1]

        # Aceita slugs de notícia com ao menos 3 hífens
        return slug.count('-') >= 3

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
            )

    def parse(self, response):
        seen = set()
        selectors = [
            "a[href*='agoranovale.com.br/']",
            "a[href^='/']",
        ]

        for sel in selectors:
            for entry in response.css(sel):
                href = entry.attrib.get("href")
                if not href:
                    continue

                url = response.urljoin(href).split('?', 1)[0].split('#', 1)[0]
                if url in seen:
                    continue

                if self.allow_url(url):
                    seen.add(url)
                    yield URLItem(url=url)

        self.logger.info(f"Collected {len(seen)} unique news URLs from Agora no Vale")
