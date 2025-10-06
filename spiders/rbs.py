import scrapy
from urllib.parse import urlparse
from spiders.base import BaseSpider
from spiders.items import URLItem


class RBSSpider(BaseSpider):
    name = "rbsspider"
    start_urls = ["https://www.clicrbs.com.br/"]
    allowed_domains = ["clicrbs.com.br"]

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
        """
        Filtra URLs para coletar apenas notícias válidas do ClicRBS/GauchaZH
        """
        p = urlparse(url)
        path = p.path.rstrip('/')

        # 1) blacklist pure sections
        blacklisted_sections = {
            "/videos", "/podcasts", "/newsletter", "/esportes", "/entretenimento",
            "/especiais", "/multimidia", "/radio", "/tv", "/opiniao", "/contato",
            "/sobre", "/anuncie", "/classificados", "/guia", "/clima"
        }
        
        if path in blacklisted_sections:
            self.logger.info(f"Blacklisted URL: {url}")
            return False

        # 2) require at least two non-empty segments (section + slug)
        segments = [seg for seg in path.split('/') if seg]
        if len(segments) < 2:
            self.logger.info(f"URL too short: {url}")
            return False

        # 3) must be from gauchazh subdomain (main news portal)
        if not url.startswith("https://gauchazh.clicrbs.com.br"):
            return False

        slug = segments[-1]
        # 4) long slugs by hyphens or by character length (indicating real articles)
        if slug.count('-') >= 3 or len(slug) > 30:
            return True

        return False

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
            )

    def parse(self, response):
        """
        Coleta URLs de notícias apenas da página inicial
        """
        # Buscar todos os links na página
        links = response.css("a")
        self.logger.info(f"Found {len(links)} total links on page")
        
        seen = set()
        valid_count = 0
        
        for link in links:
            raw_url = link.attrib.get("href")
            if not raw_url:
                continue

            # Construir URL absoluta e limpar fragmentos/queries
            full_url = response.urljoin(raw_url)
            full_url = full_url.split('#', 1)[0].split('?', 1)[0]
            
            # Evitar duplicatas
            if full_url in seen:
                continue
            seen.add(full_url)

            if self.allow_url(full_url):
                valid_count += 1
                yield URLItem(url=full_url)

        self.logger.info(f"Collected {valid_count} valid news URLs from RBS/GauchaZH")
