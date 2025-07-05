import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class RBSSpider(BaseSpider):
    name = "rbsspider"
    start_urls = [
        "https://www.clicrbs.com.br/",
        "https://gauchazh.clicrbs.com.br/"
    ]
    allowed_domains = ["clicrbs.com.br", "gauchazh.clicrbs.com.br"]
    
    custom_settings = {
        **BaseSpider.custom_settings,
        "DOWNLOAD_DELAY": 2,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
    }

    def allow_url(self, entry_url):
        """Filtrar URLs que são artigos/notícias válidas."""
        if not entry_url or not isinstance(entry_url, str):
            return False
            
        # Verificar se é URL interna
        if "clicrbs.com.br" not in entry_url:
            return False
            
        # Padrões de URLs de conteúdo
        content_indicators = [
            "/noticia/", "/esportes/", "/economia/", 
            "/politica/", "/cultura/", "/donna/", "/ge/",
            "/ultimas-noticias/", "/mundo/", "/colunistas/",
            "/opiniao/", "/videos/", "/fotos/"
        ]
        
        return any(indicator in entry_url for indicator in content_indicators)

    def parse(self, response):
        url_item = URLItem()
        
        # Seletores para links de notícias
        selectors = [
            "article a::attr(href)",
            ".news-title a::attr(href)", 
            ".article-title a::attr(href)",
            "h1 a::attr(href)", "h2 a::attr(href)", "h3 a::attr(href)",
            "a.headline::attr(href)",
            "a::attr(href)"
        ]
        
        for selector in selectors:
            for href in response.css(selector).getall():
                if not href or href.startswith("#") or href.startswith("javascript:"):
                    continue
                    
                url = response.urljoin(href.strip())
                
                if url and self.allow_url(url):
                    url_item["url"] = url
                    yield url_item
                    yield scrapy.Request(
                        url=url, 
                        callback=self.parse,
                        meta={"dont_redirect": True, "handle_httpstatus_list": [403]}
                    )
