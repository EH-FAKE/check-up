import re

import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class FaxajuSpider(BaseSpider):
    name = "faxajuspider"
    start_urls = ["https://www.faxaju.com.br/"]
    allowed_domains = ["faxaju.com.br", "www.faxaju.com.br"]

    BLACKLISTED_SECTIONS = {
       
    }

    def allow_url(self, url: str) -> bool:
        """
        Filtra URLs de matérias do Faxaju de forma genérica.
        """
        if not url:
            return False

        # Remove fragmentos e query string
        url = url.split("#", 1)[0].split("?", 1)[0]

        # Garante que é do domínio alvo
        if not re.match(r"https?://(www\.)?faxaju\.com\.br/", url):
            return False

        path = re.sub(r"https?://[^/]+", "", url)
        segments = [s for s in path.strip("/").split("/") if s]

        # Muito curto normalmente significa home ou seção agregadora
        if len(segments) < 2:
            return False

        # Filtra seções que não são matérias
        blacklist_prefixes = {p.lower() for p in self.BLACKLISTED_SECTIONS}
        for seg in segments:
            seg_low = seg.lower()
            if any(seg_low.startswith(pref) for pref in blacklist_prefixes):
                return False

        slug = segments[-1]

        # Exige slug minimamente descritivo:
        # - termina com .html OU
        # - possui hífens suficientes para parecer título de matéria
        if slug.endswith(".html"):
            base_slug = slug[:-5]
        else:
            base_slug = slug

        return base_slug.count("-") >= 2 and len(base_slug) > 20

    def parse(self, response):
        """
        Coleta URLs de notícias da página inicial (sem crawling recursivo).
        """
        seen = set()

        selectors = [
            "a[href*='faxaju.com.br']",
            "a[href^='/']",
        ]

        for sel in selectors:
            for entry in response.css(sel):
                href = entry.attrib.get("href")
                if not href:
                    continue

                url = response.urljoin(href).split("?", 1)[0].split("#", 1)[0]

                if url in seen:
                    continue

                if self.allow_url(url):
                    seen.add(url)
                    yield URLItem(url=url)

        self.logger.info(
            f"Collected {len(seen)} unique news URLs from Faxaju"
        )

