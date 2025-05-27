import re
from urllib.parse import urljoin

import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


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

    def allow_url(self, entry_url):
        # Verifica se é uma URL do UOL
        if not any(domain in entry_url for domain in [
            "noticias.uol.com.br",
            "esporte.uol.com.br",
            "economia.uol.com.br",
            "www.uol.com.br"
        ]):
            return False

        # Rejeita URLs de mídia
        if any(ext in entry_url for ext in [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3"]):
            return False

        # Rejeita URLs de seções especiais
        if any(section in entry_url for section in ["/ultimas/", "/ao-vivo/", "/videos/", "/fotos/", "/especiais/"]):
            return False

        # Rejeita URLs muito curtas (provavelmente são páginas de categoria)
        if len(entry_url) < 80:
            return False

        # Verifica se a URL tem um formato típico de notícia
        # Ex: noticias.uol.com.br/2023/05/27/titulo-da-noticia.htm
        if not re.search(r'\d{4}/\d{2}/\d{2}', entry_url):
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
        url_item = URLItem()
        for entry in response.css("a"):
            url = entry.attrib.get("href")
            if not url or url.startswith('#'):
                continue
                
            # Converte URLs relativas em absolutas
            absolute_url = urljoin(response.url, url)
            
            if self.allow_url(absolute_url):
                url_item["url"] = absolute_url
                yield url_item
                yield scrapy.Request(
                    url=absolute_url,
                    callback=self.parse,
                    meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
                )
