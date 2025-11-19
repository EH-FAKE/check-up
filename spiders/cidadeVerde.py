import re

import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class CidadeVerdeSpider(BaseSpider):
    name = "cidadeverdespider"
    start_urls = ["https://cidadeverde.com/"]
    allowed_domains = ["cidadeverde.com", "www.cidadeverde.com"]

    # Seções claramente não relacionadas a notícias ou que tendem a ser utilitários
    BLACKLISTED_SECTIONS = {
      "cvplay"
    }

    def allow_url(self, url: str) -> bool:
        """
        Filtra URLs de matérias do Cidade Verde.
        A estratégia é bem genérica para funcionar sem depender de layout específico.
        """
        if not url:
            return False

        # Remove fragmentos e query string
        url = url.split("#", 1)[0].split("?", 1)[0]

        # Garante que é do domínio alvo
        if not re.match(r"https?://(www\.)?cidadeverde\.com/", url):
            return False

        # Extrai path
        path = re.sub(r"https?://[^/]+", "", url)
        segments = [s for s in path.strip("/").split("/") if s]

        # Muito curto normalmente significa home ou seção agregadora
        if len(segments) < 2:
            return False

        # Normaliza para verificar seções indesejadas
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

        # Seletores genéricos; se o site tiver CSS específico, podemos refinar depois.
        selectors = [
            "a[href*='cidadeverde.com']",
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
            f"Collected {len(seen)} unique news URLs from Cidade Verde"
        )

