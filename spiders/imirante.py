import scrapy
from urllib.parse import urlparse
from spiders.base import BaseSpider
from spiders.items import URLItem

class ImiranteSpider(BaseSpider):
    name = "imirantespider"
    start_urls = ["https://imirante.com/"]
    allowed_domains = ["imirante.com"]

    custom_settings = {
        **BaseSpider.custom_settings,
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 2,
        "COMPRESSION_ENABLED": False,
        "HTTPCOMPRESSION_ENABLED": False,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    }

    def allow_url(self, url: str) -> bool:
        if not url.startswith("https://imirante.com"):
            return False
            
        p = urlparse(url)
        path = p.path.rstrip('/')
        
        blacklisted_sections = {
            "/videos", "/podcasts", "/programas", "/mirantefm", "/mirantenews",
            "/entretenimento", "/culinaria", "/esporte", "/colunas", "/maranhao",
            "/namira", "/agenda", "/sobre", "/contato", "/anuncie",
            "/servicos", "/editais", "/25anos", "/politica-de-cookies",
            "/politica-de-privacidade"
        }
        
        if any(path.startswith(section) for section in blacklisted_sections):
            return False
        
        if "/noticias/" in path:
            segments = [seg for seg in path.split('/') if seg]
            if len(segments) >= 6:
                try:
                    year = int(segments[2])
                    month = int(segments[3]) 
                    day = int(segments[4])
                    if 2020 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                        slug = segments[5]
                        if len(slug) > 5 and slug.count('-') >= 1:
                            return True
                except (ValueError, IndexError):
                    pass
        
        news_indicators = [
            "ipolitica", "brasil", "maranhao", "sao-luis", "economia", 
            "politica", "/2025/", "/2024/"
        ]
        
        if any(indicator in url.lower() for indicator in news_indicators):
            segments = [seg for seg in path.split('/') if seg]
            if len(segments) >= 2:
                last_segment = segments[-1]
                if len(last_segment) > 10 and last_segment.count('-') >= 2:
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
        if not response.text.strip().startswith('<'):
            return
        
        selectors = [
            "a[href*='/noticias/']",
            "a[href*='/esporte/']",
            "a[href*='ipolitica']",
            "a[href*='/2025/']",
            "a[href*='/2024/']",
        ]
        
        seen_urls = set()
        valid_count = 0
        
        for selector in selectors:
            links = response.css(selector)
            
            for link in links:
                url = link.attrib.get("href")
                if not url:
                    continue
                
                full_url = response.urljoin(url)
                full_url = full_url.split('#', 1)[0].split('?', 1)[0]
                
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                
                if self._is_potential_news_url(full_url) and self.allow_url(full_url):
                    yield URLItem(url=full_url)
                    valid_count += 1
                    
                    if valid_count >= 50:
                        break
            
            if valid_count > 0:
                break

    def _is_potential_news_url(self, url: str) -> bool:
        if not url.startswith("https://imirante.com"):
            return False
            
        exclude_patterns = [
            "/videos", "/programas", "/mirantefm", "/mirantenews",
            "/culinaria", "/esporte", "/entretenimento", "/colunas",
            "/politica-de-privacidade", "/contato", "/sobre", "/anuncie",
            "/servicos", "/editais", "/25anos", "javascript:", "mailto:",
            "#", "facebook.com", "instagram.com", "twitter.com", "whatsapp.com"
        ]
        
        for pattern in exclude_patterns:
            if pattern in url.lower():
                return False
        
        include_patterns = [
            "/noticias/", "/2025/", "/2024/", "ipolitica", "brasil", 
            "maranhao", "sao-luis", "economia", "politica"
        ]
        
        for pattern in include_patterns:
            if pattern in url.lower():
                return True
        
        return False
