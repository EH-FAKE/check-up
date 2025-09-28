import scrapy
from urllib.parse import urlparse
from spiders.base import BaseSpider
from spiders.items import URLItem


class BrasilDeFatoSpider(BaseSpider):
    name = "brasildefato"
    start_urls = ["https://www.brasildefato.com.br/"]
    allowed_domains = ["brasildefato.com.br"]

    custom_settings = {
        **BaseSpider.custom_settings,
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 2,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
    }

    def allow_url(self, url: str) -> bool:
        p = urlparse(url)
        path = p.path.rstrip('/')

        # 1) blacklist sections that are not news
        blacklist = {
            "/quem-somos", "/publicidade", "/contato", "/politica-privacidade",
            "/feed", "/tv-brasil-de-fato", "/radioagencia", "/artes", "/colunistas",
            "/programas", "/podcast", "/apoie"
        }

        if "/podcast/" in path:
            return False

        for blocked in blacklist:
            if path.startswith(blocked):
                return False

        # 2) require date pattern: YYYY/MM/DD/slug
        segments = [seg for seg in path.split('/') if seg]

        if len(segments) >= 5:
            # regional pattern: /state/YYYY/MM/DD/slug
            try:
                estado, year, month, day = segments[0], segments[1], segments[2], segments[3]
                if (len(year) == 4 and year.isdigit() and
                    len(month) == 2 and month.isdigit() and
                    len(day) == 2 and day.isdigit() and
                        len(segments) >= 5):
                    slug = segments[4]
                    if slug.count('-') >= 1 and len(slug) > 10:
                        return True
            except (IndexError, ValueError):
                pass

        if len(segments) >= 4:
            # national pattern: YYYY/MM/DD/slug
            try:
                year, month, day = segments[0], segments[1], segments[2]
                if (len(year) == 4 and year.isdigit() and
                    len(month) == 2 and month.isdigit() and
                        len(day) == 2 and day.isdigit()):
                    slug = segments[3]
                    if slug.count('-') >= 1 and len(slug) > 10:
                        return True
            except (IndexError, ValueError):
                pass

        return False

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
            )

    def parse(self, response):
        import re

        # Handle XML/RSS feeds
        if response.url.endswith('.xml') or 'xml' in response.headers.get('content-type', b'').decode():
            links = response.xpath('//loc/text()').getall()
            links.extend(response.xpath('//url/text()').getall())
            links.extend(response.xpath('//link/text()').getall())
            for link in links:
                if link and self.allow_url(link):
                    yield URLItem(url=link)
            return

        # Extract URLs from HTML content
        urls = response.css('a::attr(href)').getall()
        for url in urls:
            if url:
                full_url = response.urljoin(url).split('#')[0].split('?')[0]
                if self.allow_url(full_url):
                    yield URLItem(url=full_url)

        # Extract URLs using regex patterns
        patterns = [
            r'"(https?://(?:www\.)?brasildefato\.com\.br/20\d{2}/\d{2}/\d{2}/[^"]+)"',
            r'"(/20\d{2}/\d{2}/\d{2}/[^"]+)"',
            r'href="(/20\d{2}/\d{2}/\d{2}/[^"]+)"',
            r'href="(https?://(?:www\.)?brasildefato\.com\.br/20\d{2}/\d{2}/\d{2}/[^"]+)"'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response.text)
            for match in matches:
                full_url = response.urljoin(match) if match.startswith('/') else match
                full_url = full_url.split('#')[0].split('?')[0]
                if self.allow_url(full_url):
                    yield URLItem(url=full_url)