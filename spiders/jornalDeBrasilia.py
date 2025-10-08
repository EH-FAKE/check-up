import scrapy
from urllib.parse import urlparse
from spiders.base import BaseSpider
from spiders.items import URLItem

class JornalDeBrasiliaSpider(BaseSpider):
    name = "jornaldebrasiliaspider"
    start_urls = ["https://jornaldebrasilia.com.br/"]
    allowed_domains = ["jornaldebrasilia.com.br"]

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
        """
        Filtra apenas URLs de notícias válidas
        """
        p = urlparse(url)
        path = p.path.rstrip('/')
        
        # Blacklist de seções que não são notícias
        blacklist = {
            "/videos", "/podcasts", "/newsletter", "/contato", 
            "/sobre", "/anuncie", "/assine", "/busca"
        }
        
        if path in blacklist:
            return False
        
        # Requer pelo menos 2 segmentos (seção + slug)
        segments = [seg for seg in path.split('/') if seg]
        if len(segments) < 2:
            return False
        
        # Verificar se é uma notícia (slug longo com hífens)
        slug = segments[-1]
        if slug.count('-') >= 2 or len(slug) > 20:
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
        Extrai URLs de notícias da página inicial
        """
        selectors = [
            "article a[href]", 
            ".news-item a[href]", 
            ".headline a[href]",  
            "h2 a[href], h3 a[href]",  
        ]
        
        seen_urls = set()
        
        for selector in selectors:
            links = response.css(selector)
            
            for link in links:
                url = link.attrib.get("href")
                if not url:
                    continue
                
                # Construir URL absoluta
                full_url = response.urljoin(url)
                full_url = full_url.split('#', 1)[0].split('?', 1)[0]
                
                # Evitar duplicatas
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                
                # Filtrar URLs válidos
                if self.allow_url(full_url):
                    yield URLItem(url=full_url)
