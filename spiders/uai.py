import scrapy
from urllib.parse import urlparse
from spiders.base import BaseSpider
from spiders.items import URLItem

class UaiSpider(BaseSpider):
    name = "uaispider"
    start_urls = ["https://www.uai.com.br/"]
    allowed_domains = ["uai.com.br"]

    custom_settings = {
        **BaseSpider.custom_settings,
        "COOKIES_ENABLED": True,
        "DOWNLOAD_DELAY": 2,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
    }

    def allow_url(self, url: str) -> bool:
        if not (url.startswith("https://www.uai.com.br") or 
                url.startswith("https://www.em.com.br") or
                url.startswith("https://www.vrum.com.br") or
                url.startswith("https://aqui.uai.com.br") or
                url.startswith("https://soubh.uai.com.br")):
            return False
            
        p = urlparse(url)
        path = p.path.rstrip('/')
        
        blacklisted_sections = {
            "/videos", "/podcasts", "/programas", "/radio", "/tv",
            "/entretenimento", "/culinaria", "/esporte", "/esportes",
            "/colunistas", "/colunas", "/opiniao", "/blogs",
            "/sobre", "/contato", "/anuncie", "/assine", "/newsletter",
            "/servicos", "/editais", "/politica-de-privacidade",
            "/termos-de-uso", "/busca", "/search", "/galeria",
            "/especiais", "/multimidia", "/horoscopo", "/tempo"
        }
        
        if any(path.startswith(section) for section in blacklisted_sections):
            return False
        
        if "em.com.br" in url:
            if path.endswith('.html') and '/202' in path:
                segments = [seg for seg in path.split('/') if seg]
                if len(segments) >= 4:
                    return True
        
        if "vrum.com.br" in url:
            if path.endswith('.html') and '/202' in path:
                segments = [seg for seg in path.split('/') if seg]
                if len(segments) >= 4:
                    return True
        
        if any(subdomain in url for subdomain in ["aqui.uai.com.br", "soubh.uai.com.br"]):
            if "/noticias/" in path:
                segments = [seg for seg in path.split('/') if seg]
                if len(segments) >= 2:
                    slug = segments[-1] if segments[-1] else segments[-2]
                    if len(slug) > 10 and slug.count('-') >= 2:
                        return True
        
        if "uai.com.br" in url:
            if "/noticias/" in path:
                segments = [seg for seg in path.split('/') if seg]
                if len(segments) >= 3:
                    slug = segments[-1]
                    if len(slug) > 10 and slug.count('-') >= 2:
                        return True
            
            news_indicators = [
                "/brasil/", "/minas/", "/politica/", "/economia/", 
                "/saude/", "/educacao/", "/seguranca/", "/mundo/",
                "/gerais/", "/nacional/"
            ]
            
            if any(indicator in path for indicator in news_indicators):
                segments = [seg for seg in path.split('/') if seg]
                if len(segments) >= 2:
                    last_segment = segments[-1]
                    if len(last_segment) > 15 and last_segment.count('-') >= 3:
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
            "a[href*='em.com.br'][href$='.html']",
            "a[href*='vrum.com.br'][href$='.html']",
            "a[href*='aqui.uai.com.br/noticias/']",
            "a[href*='soubh.uai.com.br/noticias/']",
            "a[href*='/gerais/'][href$='.html']",
            "a[href*='/politica/'][href$='.html']",
            "a[href*='/nacional/'][href$='.html']",
            "a[href*='/noticias/'][href$='.html']",
            "a[href*='uai.com.br/noticias/']",
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
                    
                    if valid_count >= 100:
                        return

    def _is_potential_news_url(self, url: str) -> bool:
        if not (url.startswith("https://www.uai.com.br") or 
                url.startswith("https://www.em.com.br") or
                url.startswith("https://www.vrum.com.br") or
                url.startswith("https://aqui.uai.com.br") or
                url.startswith("https://soubh.uai.com.br")):
            return False
            
        exclude_patterns = [
            "/videos", "/podcasts", "/programas", "/radio", "/tv",
            "/entretenimento", "/culinaria", "/esporte", "/esportes",
            "/colunistas", "/colunas", "/opiniao", "/blogs",
            "/sobre", "/contato", "/anuncie", "/assine", "/newsletter",
            "/servicos", "/editais", "/politica-de-privacidade",
            "/termos-de-uso", "/busca", "/search", "/galeria",
            "/especiais", "/multimidia", "/horoscopo", "/tempo",
            "javascript:", "mailto:", "#", "facebook.com", 
            "instagram.com", "twitter.com", "whatsapp.com"
        ]
        
        for pattern in exclude_patterns:
            if pattern in url.lower():
                return False
        
        include_patterns = [
            "/noticias/", "/brasil/", "/minas/", "/politica/", 
            "/economia/", "/saude/", "/educacao/", "/seguranca/", "/mundo/",
            "/gerais/", "/nacional/", ".html", "/carros/", "/automoveis/"
        ]
        
        for pattern in include_patterns:
            if pattern in url.lower():
                return True
        
        return False
