import scrapy
from urllib.parse import urlparse

from spiders.base import BaseSpider
from spiders.items import URLItem


class CartaCapitalSpider(BaseSpider):
    name = "cartacapitalspider"
    allowed_domains = ["www.cartacapital.com.br", "cartacapital.com.br"]
    start_urls = [
        "https://www.cartacapital.com.br/",
        "https://www.cartacapital.com.br/mais-recentes/",
    ]

    custom_settings = {
        **BaseSpider.custom_settings,
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 1.5,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0 Safari/537.36"
            ),
        },
    }

    def allow_url(self, url: str) -> bool:
        p = urlparse(url)

        if p.netloc not in ("www.cartacapital.com.br", "cartacapital.com.br"):
            return False

        path = p.path.rstrip("/") or "/"

        if path == "/":
            return False

        blacklist_prefixes = (
            "/tag/",
            "/tags/",
            "/author/",
            "/autores/",
            "/assine",
            "/manifesto",
            "/princípios",
            "/principios",
            "/expediente",
            "/sobre-nos",
            "/media-kit",
            "/newsletter",
            "/wp-content",
            "/wp-json",
            "/wp-admin",
            "/central-de-ajuda",
        )
        if any(path.startswith(prefix) for prefix in blacklist_prefixes):
            return False

        if path.endswith(".pdf"):
            return False

        segments = [seg for seg in path.split("/") if seg]
        if len(segments) < 2:
            return False

        slug = segments[-1]
        if slug.count("-") < 2 and len(slug) < 15:
            return False

        return True

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                meta={
                    "dont_redirect": True,
                    "handle_httpstatus_list": [403, 404],
                },
            )

    def parse(self, response: scrapy.http.Response):
        seen_urls: set[str] = set()

        selectors = [
            "a.h-education__item::attr(href)",
            "main a[href*='cartacapital.com.br']::attr(href)",
            "article a[href]::attr(href)",
            "h2 a[href]::attr(href)",
            "h3 a[href]::attr(href)",
        ]

        for selector in selectors:
            for href in response.css(selector).getall():
                if not href:
                    continue

                full_url = response.urljoin(href)
                full_url = full_url.split("#", 1)[0].split("?", 1)[0]

                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)

                if self.allow_url(full_url):
                    yield URLItem(url=full_url)
