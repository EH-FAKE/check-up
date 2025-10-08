import re

import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class AgoraNoValeSpider(BaseSpider):
    name = "agoranovalespider"
    allowed_domains = ["agoranovale.com.br", "www.agoranovale.com.br"]
    start_urls = ["https://agoranovale.com.br/"]

    custom_settings = {
        **BaseSpider.custom_settings,
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 3,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0 Safari/537.36"
            ),
            "Cache-Control": "max-age=0",
        },
        "CONCURRENT_REQUESTS": 4,
    }

    BLACKLISTED_SECTIONS = {
        "/agoranacozinha",
      
    }

    
    def _normalize(self, url: str) -> str:
        return url.split("#", 1)[0].split("?", 1)[0]

    def allow_url(self, url: str) -> bool:
        if not url:
            return False

        url = self._normalize(url)


        path = re.sub(r"^https?://[^/]+", "", url)
        segments = [s for s in path.strip("/").split("/") if s]
        if len(segments) < 2:
            return False  
        
        # blacklist por prefixo 
        bl = {p.lstrip("/").lower() for p in self.BLACKLISTED_SECTIONS}
        for seg in (s.lower() for s in segments):
            if any(seg.startswith(pref) for pref in bl):
                return False

        slug = segments[-1].lower()

       
        # heurística simples de notícia: slug com ao menos 3 hífens ou nome longo
        return slug.count("-") >= 3 or len(slug) >= 20

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
            "a[href*='agoranovale.com.br']",
            "a[href^='/']",
            "article a[href]",
            "main a[href]",
            "h1 a[href], h2 a[href], h3 a[href], .entry-title a[href], .post a[href]",
            "link[rel='canonical'][href]",
        ]

        for sel in selectors:
            for node in response.css(sel):
                href = node.attrib.get("href")
                if not href:
                    continue

                url = self._normalize(response.urljoin(href))
                if url in seen:
                    continue

                if self.allow_url(url):
                    seen.add(url)
                    yield URLItem(url=url)

        self.logger.info(
            f"[AgoraNoVale] Coletadas {len(seen)} URLs únicas de notícia em {response.url}"
        )
