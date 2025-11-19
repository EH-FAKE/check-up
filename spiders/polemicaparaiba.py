import re
from urllib.parse import urljoin, urlparse
from spiders.base import BaseSpider
from spiders.items import URLItem


class PolemicaParaibaSpider(BaseSpider):
    name = "polemicaparaibaspider"
    start_urls = [
        "https://www.polemicaparaiba.com.br/",
        "https://www.polemicaparaiba.com.br/politica/",
        "https://www.polemicaparaiba.com.br/paraiba/",
        "https://www.polemicaparaiba.com.br/brasil/",
        "https://www.polemicaparaiba.com.br/entretenimento/",
    ]

    custom_settings = {
        "DEPTH_LIMIT": 1,
        "DOWNLOAD_DELAY": 1.5,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 400, 403, 404, 408],
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def allow_url(self, url):
        """
        Determina se uma URL deve ser incluída.
        """
        parsed_url = urlparse(url)
        
        # Lista de padrões que devem ser bloqueados
        blocked_patterns = [
            r'/wp-content/',
            r'/wp-admin/',
            r'/wp-json/',
            r'/feed/',
            r'/author/',
            r'/tag/',
            r'/category/',
            r'/page/',
            r'/search/',
            r'\?',
            r'#',
            r'xmlrpc\.php',
            r'\.xml$',
            r'\.pdf$',
            r'\.jpg$',
            r'\.jpeg$',
            r'\.png$',
            r'\.gif$',
            r'\.css$',
            r'\.js$',
            r'\.ico$',
        ]
        
        # Verifica se a URL contém algum padrão bloqueado
        for pattern in blocked_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Verifica se é do domínio polemicaparaiba.com.br
        if not parsed_url.netloc.endswith('polemicaparaiba.com.br'):
            return False
        
        # Verifica se parece ser uma URL de artigo/notícia
        # URLs de artigos geralmente têm uma estrutura específica
        path = parsed_url.path
        
        # Permitir URLs que parecem ser de notícias (com pelo menos 3 segmentos no path)
        path_segments = [seg for seg in path.strip('/').split('/') if seg]
        
        # Permitir páginas principais e de categoria
        if len(path_segments) <= 1:
            return True
            
        # Permitir URLs que parecem ser de artigos
        # (com pelo menos 2 segmentos e não terminando em /)
        if len(path_segments) >= 2 and not path.endswith('/'):
            return True
            
        # Permitir URLs de categorias específicas
        allowed_categories = [
            'politica', 'paraiba', 'brasil', 'entretenimento',
            'esportes', 'economia', 'tecnologia', 'mundo'
        ]
        
        if len(path_segments) >= 1 and path_segments[0] in allowed_categories:
            return True
        
        return False

    def parse(self, response):
        # Extrair todos os links da página
        links = response.css('a::attr(href)').getall()
        
        for link in links:
            if link:
                # Converte links relativos em absolutos
                absolute_url = urljoin(response.url, link)
                
                # Verifica se a URL deve ser incluída
                if self.allow_url(absolute_url):
                    yield URLItem(url=absolute_url)
