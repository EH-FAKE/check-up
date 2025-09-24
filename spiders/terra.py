import re

import scrapy
from scrapy_playwright.page import PageMethod

from spiders.base import BaseSpider
from spiders.items import URLItem


class TerraSpider(BaseSpider):
    name = "terraspider"
    start_urls = ["https://www.terra.com.br/"]
    allowed_domains = ["terra.com.br", "www.terra.com.br"]

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
        # Ativa o Playwright para scrollar e carregar conteúdo dinâmico
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "firefox",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60 * 1000,
        "PLAYWRIGHT_ABORT_RESOURCE_TYPES": ["image", "media", "font", "stylesheet"],
        "CONCURRENT_REQUESTS": 4,
    }
    
    #  Seções que não são notícias
    BLACKLISTED_SECTIONS = {
        "videos", "podcast", "podcasts", "blogs", "colunas", "especiais", "ao-vivo", "story", "amp"
    }

    def allow_url(self, url: str) -> bool:
        """
        Filtragem melhorada para URLs de notícias do Terra.
        """
        if not url:
            return False
        url = url.split('#', 1)[0]

        # Normaliza e filtra padrões comuns de matéria do Terra, ex.:
        # https://www.terra.com.br/noticias/brasil/...
        if not re.match(r"https?://(www\.)?terra\.com\.br/", url):
            return False
        
        # Evita áreas que não são notícias
        path = re.sub(r"https?://[^/]+", "", url)
        first = (path.strip("/").split("/") or [""])[0]
        if first in self.BLACKLISTED_SECTIONS:
            return False
        
        # Require pelo menos dois segmentos (seção + slug da notícia)
        segments = [s for s in path.split('/') if s]
        if len(segments) < 2:
            return False
        
        slug = segments[-1]

        # Heurística de slug de notícia
        if slug.count('-') >= 3 or len(slug) > 30 or slug.endswith('.html'):
            return True
        return False

    def _block_ads(self, route, request):
        try:
            
            blocked_domains = (
                "doubleclick.net",
                "googlesyndication.com",
                "google-analytics.com",
                "analytics.google.com",
                "clarity.ms",
                "tailtarget.com",
                "flashtalking.com",
                "googletagmanager.com",
            )
            if request.resource_type in {"image", "media", "font", "stylesheet"}:
                return route.abort()
            if any(d in request.url for d in blocked_domains):
                return route.abort()
            return route.continue_()
        except Exception:
            return route.continue_()

    def start_requests(self):
        for url in self.start_urls:
            methods = [
                PageMethod("route", "**/*", self._block_ads),
                PageMethod("wait_for_load_state", "domcontentloaded"),
            ]
            for _ in range(12):
                methods.append(PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"))
                methods.append(PageMethod("wait_for_timeout", 700))

            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                meta={
                    "playwright": True,
                    "playwright_page_goto_kwargs": {"wait_until": "domcontentloaded", "timeout": 60_000},
                    "playwright_page_methods": methods,
                },
            )
    def parse(self, response):
        """
        Extrai apenas URLs da página inicial, sem crawling recursivo
        """
        seen = set()
        selectors = [
            "a[href*='terra.com.br/noticias']",
            "a[href*='terra.com.br/economia']",
            "a[href*='terra.com.br/esportes']",
            "a[href*='terra.com.br/vida-e-estilo']",
            "a[href*='terra.com.br/']",
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
                    
        self.logger.info(f"Collected {len(seen)} unique news URLs from Terra")
