import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem
from urllib.parse import urlparse


class AgenciaGovSpider(BaseSpider):
    name = "agenciagovspider"
    start_urls = ["https://agenciagov.ebc.com.br/noticias"]
    allowed_domains = ["agenciagov.ebc.com.br"]

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
        },
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "firefox",
    }

    def allow_url(self, url: str) -> bool:
        # Validate domain
        if not url or "agenciagov.ebc.com.br" not in url:
            return False

        p = urlparse(url)
        path = p.path.rstrip("/")

        # Blacklist sections
        blacklist = {
            "/sobre",
            "/ouvidoria",
            "/distribuicao",
            "/sitemap",
            "/login",
            "/RSS",
            "/rss.xml",
            "/atom.xml",
            "/@@search",
        }

        if path in blacklist:
            self.logger.info(f"Blacklisted URL: {url}")
            return False
        
        # Validate news patterns
        if "/noticias/202" not in path:
            return False

        # Validate segments
        segments = [seg for seg in path.split("/") if seg]
        if len(segments) < 3:
            self.logger.info(f"URL with less than 3 segments: {url}")
            return False

        slug = segments[-1]
        # Long slugs by hyphens or by character length
        if slug.count("-") >= 3 or len(slug) > 30:
            return True

        return False

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_goto_kwargs": {"wait_until": "networkidle"},
                },
            )

    def parse(self, response):
        page = response.meta.get("playwright_page")
        if page:
            page.close()

        # Extract all links from page
        links = response.css("a::attr(href)").getall()
        self.logger.info(f"Found {len(links)} links under homepage")

        for raw in links:
            if not raw:
                continue

            # Build absolute URL, then strip fragments/queries
            full = response.urljoin(raw)
            full = full.split("#", 1)[0].split("?", 1)[0]

            if self.allow_url(full):
                yield URLItem(url=full)
