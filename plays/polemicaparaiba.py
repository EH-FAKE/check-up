import requests
import re
from urllib.parse import urljoin, urlparse
from plays.base import BasePlay
from plays.items import URLItem


class PolemicaParaibaPlay(BasePlay):
    """
    Play para extrair URLs do site polemicaparaiba.com.br
    """
    
    name = "polemicaparaiba"
    start_urls = [
        "https://www.polemicaparaiba.com.br/",
        "https://www.polemicaparaiba.com.br/politica/",
        "https://www.polemicaparaiba.com.br/paraiba/",
        "https://www.polemicaparaiba.com.br/brasil/",
        "https://www.polemicaparaiba.com.br/entretenimento/",
    ]
    
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
        path = parsed_url.path
        
        # Permitir URLs que parecem ser de notícias
        path_segments = [seg for seg in path.strip('/').split('/') if seg]
        
        # Permitir páginas principais e de categoria
        if len(path_segments) <= 1:
            return True
            
        # Permitir URLs que parecem ser de artigos
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
    
    def extract_urls_from_content(self, content, base_url):
        """
        Extrai URLs do conteúdo HTML.
        """
        urls = set()
        
        # Padrão para encontrar links href
        href_pattern = r'href=["\']([^"\'>]+)["\']'
        matches = re.findall(href_pattern, content, re.IGNORECASE)
        
        for match in matches:
            # Converte links relativos em absolutos
            absolute_url = urljoin(base_url, match)
            
            # Verifica se a URL deve ser incluída
            if self.allow_url(absolute_url):
                urls.add(absolute_url)
        
        return list(urls)
    
    def run(self):
        """
        Executa o play para extrair URLs.
        """
        all_urls = set()
        
        for start_url in self.start_urls:
            try:
                print(f"Processando: {start_url}")
                
                # Faz a requisição
                response = requests.get(
                    start_url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Extrai URLs do conteúdo
                    urls = self.extract_urls_from_content(response.text, start_url)
                    all_urls.update(urls)
                    print(f"Encontradas {len(urls)} URLs em {start_url}")
                else:
                    print(f"Erro {response.status_code} ao acessar {start_url}")
                    
            except Exception as e:
                print(f"Erro ao processar {start_url}: {e}")
        
        # Converte para lista de URLItem
        url_items = [URLItem(url=url) for url in sorted(all_urls)]
        
        print(f"\nTotal de URLs extraídas: {len(url_items)}")
        
        return url_items
