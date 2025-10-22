# Tutorial: Criando Spiders e Plays do Zero

## 🎯 Objetivo

Este tutorial ensina como criar **spiders** e **plays** completamente novos para portais de notícias que ainda não estão presentes no projeto. É um guia passo-a-passo desde a análise inicial até a implementação completa.

## 📋 Pré-requisitos

- Conhecimento básico de Python
- Familiaridade com HTML/CSS
- Docker instalado e funcionando
- Projeto Check-up configurado (`make setup`)

## 🚀 Visão Geral do Processo

1. **Análise do Portal** - Entender a estrutura do site
2. **Adicionar ao Banco** - Registrar o portal no sistema
3. **Criar Spider** - Implementar coleta de URLs
4. **Criar Play** - Implementar extração de conteúdo
5. **Adicionar Comandos** - Integrar ao Makefile
6. **Testar e Validar** - Garantir funcionamento correto

---

## 🔍 Etapa 1: Análise do Portal

### 1.1 Escolher o Portal

Vamos usar o **Correio Braziliense** como exemplo:
- **URL**: https://www.correiobraziliense.com.br
- **Tipo**: Portal de notícias regional/nacional

### 1.2 Analisar a Página Inicial

**Passo 1**: Abra o portal no navegador
**Passo 2**: Inspecione a estrutura (F12)
**Passo 3**: Identifique onde estão os links das notícias

#### 🔍 O que procurar:
- **Seção principal de notícias** (geralmente no centro da página)
- **Links de notícias** (elementos `<a>` com URLs de artigos)
- **Padrão das URLs** (como são estruturadas)

#### 📝 Exemplo de análise:
```html
<!-- Estrutura típica encontrada -->
<div class="news-section">
  <article class="news-item">
    <a href="/brasil/politica/noticia-exemplo-123456.html">
      <h2>Título da Notícia</h2>
    </a>
  </article>
</div>
```

### 1.3 Analisar Páginas de Notícia

**Passo 1**: Clique em uma notícia
**Passo 2**: Inspecione os elementos (F12)
**Passo 3**: Identifique seletores para cada campo

#### 🎯 Campos a identificar:
- **Título**: `<h1>`, `.title`, `.headline`
- **Descrição**: `.subtitle`, `.lead`, `.summary`
- **Corpo**: `.content`, `.article-body`, `.text`
- **Tags**: `.tags`, `.categories`, `.keywords`

#### 📝 Exemplo de análise:
```html
<!-- Estrutura típica de uma notícia -->
<article class="article">
  <header>
    <h1 class="title">Título Principal da Notícia</h1>
    <p class="subtitle">Subtítulo ou resumo da notícia</p>
  </header>
  
  <div class="content">
    <p>Primeiro parágrafo...</p>
    <p>Segundo parágrafo...</p>
    <!-- Conteúdo completo -->
  </div>
  
  <footer class="tags">
    <a href="/tag/politica">Política</a>
    <a href="/tag/brasilia">Brasília</a>
  </footer>
</article>
```

---

## 🗄️ Etapa 2: Adicionar Portal ao Banco de Dados

### 2.1 Executar Comando

```bash
# Acessar o container
make bash

# Adicionar portal ao banco
python add_portal.py "Correio Braziliense" "https://www.correiobraziliense.com.br"
```

### 2.2 Verificar Adição

```bash
# Verificar se foi adicionado
python -c "
from models import Portal
portals = Portal.select()
for p in portals:
    print(f'{p.id}: {p.name} - {p.url}')
"
```

---

## 🕷️ Etapa 3: Criar o Spider

### 3.1 Estrutura Base

Crie o arquivo `spiders/correio.py`:

```python
import scrapy
from urllib.parse import urlparse
from spiders.base import BaseSpider
from spiders.items import URLItem

class CorreioSpider(BaseSpider):
    name = "correio"
    start_urls = ["https://www.correiobraziliense.com.br/"]
    allowed_domains = ["correiobraziliense.com.br"]

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
        # Seletores específicos do Correio Braziliense
        selectors = [
            "article a[href]",  # Links dentro de artigos
            ".news-item a[href]",  # Links em itens de notícia
            ".headline a[href]",  # Links em manchetes
            "h2 a[href], h3 a[href]",  # Links em títulos
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
```

### 3.2 Testar o Spider

```bash
# Testar coleta de URLs
make bash
python crawl.py correio

# Verificar URLs coletados
python -c "
from models import URLQueue
urls = URLQueue.select().where(URLQueue.portal_id == 1).limit(10)
for url in urls:
    print(url.url)
"
```

---

## 🎭 Etapa 4: Criar o Play

### 4.1 Estrutura Base

Crie o arquivo `plays/correio.py`:

```python
import time
from playwright.sync_api import sync_playwright
from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger

class CorreioPlay(BasePlay):
    name = "correio"

    @classmethod
    def match(cls, url):
        """Identifica se a URL é do Correio Braziliense"""
        return "correiobraziliense.com.br" in url

    def pre_run(self):
        """Configurações antes da execução"""
        pass

    def run(self) -> EntryItem:
        """Extrai conteúdo da notícia"""
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()
            
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            
            # Aguardar carregamento
            page.wait_for_selector("h1", timeout=30000)
            
            # 1. EXTRAIR TÍTULO
            title = self._extract_title(page)
            
            # 2. EXTRAIR DESCRIÇÃO
            description = self._extract_description(page)
            
            # 3. EXTRAIR CORPO
            body = self._extract_body(page)
            
            # 4. EXTRAIR TAGS
            tags = self._extract_tags(page)
            
            return EntryItem(
                title=title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )

    def _extract_title(self, page):
        """Extrai o título da notícia"""
        selectors = [
            "h1.title",
            "h1.headline", 
            "h1",
            ".article-title h1",
            ".post-title h1"
        ]
        
        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    title = element.first.inner_text().strip()
                    if title:
                        logger.info(f"[{self.name}] Title extracted: {title[:50]}...")
                        return title
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract title with {selector}: {str(e)}")
                continue
        
        logger.error(f"[{self.name}] Failed to extract title")
        return ""

    def _extract_description(self, page):
        """Extrai a descrição/subtítulo da notícia"""
        selectors = [
            ".subtitle",
            ".lead",
            ".summary", 
            ".article-subtitle",
            "h2.subtitle",
            ".excerpt"
        ]
        
        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    description = element.first.inner_text().strip()
                    if description and len(description) > 10:
                        logger.info(f"[{self.name}] Description extracted: {description[:50]}...")
                        return description
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract description with {selector}: {str(e)}")
                continue
        
        logger.info(f"[{self.name}] No description found")
        return ""

    def _extract_body(self, page):
        """Extrai o corpo da notícia"""
        selectors = [
            ".article-content",
            ".post-content",
            ".content",
            ".article-body",
            ".text",
            "article .content",
            ".entry-content"
        ]
        
        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    # Remover elementos indesejados
                    element.locator("script, style, .ad, .advertisement").evaluate_all("el => el.remove()")
                    
                    body = element.inner_text().strip()
                    if body and len(body) > 100:  # Garantir que tem conteúdo substancial
                        logger.info(f"[{self.name}] Body extracted ({len(body)} chars)")
                        return body
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract body with {selector}: {str(e)}")
                continue
        
        logger.error(f"[{self.name}] Failed to extract body")
        return ""

    def _extract_tags(self, page):
        """Extrai as tags da notícia"""
        selectors = [
            ".tags a",
            ".categories a",
            ".post-tags a", 
            ".article-tags a",
            ".keywords a",
            "[rel='tag']"
        ]
        
        tags = []
        
        for selector in selectors:
            try:
                elements = page.locator(selector)
                if elements.count() > 0:
                    for i in range(elements.count()):
                        tag_text = elements.nth(i).inner_text().strip()
                        if tag_text and tag_text not in tags:
                            tags.append(tag_text)
                    
                    if tags:
                        logger.info(f"[{self.name}] Tags extracted: {tags}")
                        break
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract tags with {selector}: {str(e)}")
                continue
        
        return tags
```

### 4.2 Testar o Play

```bash
# Testar extração de uma URL específica
make bash
python -c "
from plays.correio import CorreioPlay
play = CorreioPlay('https://www.correiobraziliense.com.br/brasil/politica/exemplo.html')
result = play.run()
print(f'Título: {result.title}')
print(f'Descrição: {result.description}')
print(f'Corpo: {result.body[:100]}...')
print(f'Tags: {result.tags}')
"
```

---

## ⚙️ Etapa 5: Adicionar Comandos ao Makefile

### 5.1 Adicionar Comandos

Edite o `Makefile` e adicione:

```makefile
# Correio Braziliense
crawl_correio:
	docker compose run scraper python crawl.py correio

scrape_correio:
	docker compose run scraper python scrape.py correio

# Adicionar ao comando de crawl geral
crawl_all_working: crawl_metropoles crawl_veja crawl_r7 crawl_uol crawl_maisgoias crawl_aliadosBrasil crawl_ig crawl_folha crawl_correio

# Adicionar ao comando de scrape geral  
scrape_all_working: scrape_metropoles scrape_maisgoias scrape_aliadosbrasil scrape_ig scrape_veja scrape_r7 scrape_uol scrape_folha scrape_correio
```

### 5.2 Testar Comandos

```bash
# Testar coleta de URLs
make crawl_correio

# Testar extração de conteúdo
make scrape_correio

# Testar pipeline completo
make crawl_correio && make scrape_correio
```

---

## 🧪 Etapa 6: Testes e Validação

### 6.1 Checklist de Validação

#### ✅ Spider
- [ ] Coleta URLs apenas da página inicial
- [ ] URLs coletados são realmente de notícias
- [ ] Não coleta URLs de outras seções (vídeos, contato, etc.)
- [ ] Filtragem funciona corretamente
- [ ] Não há crawling recursivo desnecessário

#### ✅ Play
- [ ] Extrai título corretamente
- [ ] Extrai descrição quando disponível
- [ ] Extrai corpo completo da notícia
- [ ] Extrai tags quando disponível
- [ ] Não há erros de timeout
- [ ] Funciona com diferentes tipos de notícia

#### ✅ Integração
- [ ] Pipeline completo funciona
- [ ] Dados são salvos no banco PostgreSQL
- [ ] Logs não mostram erros críticos
- [ ] Comandos Makefile funcionam

### 6.2 Testes com URLs Diversas

```bash
# Testar com diferentes tipos de notícia
URLS_TESTE=(
    "https://www.correiobraziliense.com.br/brasil/politica/exemplo1.html"
    "https://www.correiobraziliense.com.br/brasil/economia/exemplo2.html"
    "https://www.correiobraziliense.com.br/brasil/esportes/exemplo3.html"
    "https://www.correiobraziliense.com.br/brasil/cultura/exemplo4.html"
)

for url in "${URLS_TESTE[@]}"; do
    echo "Testando: $url"
    python -c "
from plays.correio import CorreioPlay
play = CorreioPlay('$url')
result = play.run()
print(f'Título: {result.title[:50]}...')
print(f'Corpo: {len(result.body)} caracteres')
print('---')
"
done
```

---

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Spider não coleta URLs
**Sintomas**: Nenhum URL é coletado
**Soluções**:
- Verificar se os seletores CSS estão corretos
- Testar seletores no console do navegador
- Verificar se `allow_url()` não está muito restritivo
- Adicionar logs para debug

```python
def parse(self, response):
    # Adicionar debug
    self.logger.info(f"Parsing URL: {response.url}")
    links = response.css("article a[href]")
    self.logger.info(f"Found {links.__len__()} links")
    # ... resto do código
```

#### 2. Play não extrai conteúdo
**Sintomas**: Campos vazios ou erros de timeout
**Soluções**:
- Verificar se seletores existem na página
- Adicionar `wait_for_selector` antes de extrair
- Testar seletores manualmente no navegador
- Aumentar timeout se necessário

```python
def _extract_title(self, page):
    # Aguardar elemento aparecer
    page.wait_for_selector("h1", timeout=10000)
    # ... resto do código
```

#### 3. URLs inválidos sendo coletados
**Sintomas**: URLs de vídeos, contato, etc. sendo coletados
**Soluções**:
- Melhorar função `allow_url()`
- Adicionar mais itens à blacklist
- Verificar padrão das URLs de notícias

```python
def allow_url(self, url: str) -> bool:
    # Blacklist mais abrangente
    blacklist = {
        "/videos", "/podcasts", "/newsletter", "/contato", 
        "/sobre", "/anuncie", "/assine", "/busca", "/galeria",
        "/especiais", "/multimidia", "/radio", "/tv"
    }
    # ... resto do código
```

#### 4. Erros de timeout
**Sintomas**: Timeout ao carregar páginas
**Soluções**:
- Aumentar timeout no `page.goto()`
- Adicionar `wait_for_selector` mais específico
- Verificar se a página carrega corretamente

```python
def run(self) -> EntryItem:
    # Aumentar timeout
    page.goto(self.url, timeout=300_000)  # 5 minutos
    # Aguardar elemento específico
    page.wait_for_selector("h1", timeout=60000)
    # ... resto do código
```

### Debug Avançado

#### 1. Logs Detalhados
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. Screenshots para Debug
```python
def run(self) -> EntryItem:
    # ... código existente ...
    
    # Screenshot para debug (remover depois)
    page.screenshot(path=f"debug_{self.name}.png")
    
    # ... resto do código ...
```

#### 3. Teste de Seletores
```python
def _extract_title(self, page):
    # Testar múltiplos seletores
    selectors = ["h1", ".title", ".headline"]
    
    for selector in selectors:
        try:
            count = page.locator(selector).count()
            print(f"Seletor '{selector}': {count} elementos encontrados")
            
            if count > 0:
                text = page.locator(selector).first.inner_text()
                print(f"Texto encontrado: {text[:50]}...")
        except Exception as e:
            print(f"Erro com seletor '{selector}': {e}")
```

---

## 📚 Exemplos Práticos

### Exemplo 1: Portal Simples
```python
# Para portais com estrutura simples
class PortalSimplesSpider(BaseSpider):
    def parse(self, response):
        # Seletores básicos
        for link in response.css("a[href]"):
            url = link.attrib.get("href")
            if url and self.allow_url(url):
                yield URLItem(url=response.urljoin(url))
```

### Exemplo 2: Portal com JavaScript
```python
# Para portais que precisam de JavaScript
class PortalJSPlay(BasePlay):
    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            
            # Aguardar JavaScript carregar
            page.goto(self.url, wait_until="networkidle")
            page.wait_for_selector(".content", timeout=30000)
            
            # ... extração ...
```

### Exemplo 3: Portal com Autenticação
```python
# Para portais que precisam de login
class PortalAuthPlay(BasePlay):
    def pre_run(self):
        # Configurar autenticação se necessário
        pass
    
    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            
            # Login se necessário
            # page.goto("https://portal.com/login")
            # page.fill("#username", "user")
            # page.fill("#password", "pass")
            # page.click("#login")
            
            # ... resto da extração ...
```

---

## 🎯 Próximos Passos

1. **Testar com URLs reais** do portal escolhido
2. **Refinar seletores** baseado nos testes
3. **Otimizar performance** se necessário
4. **Adicionar tratamento de erros** robusto
5. **Documentar seletores** para futuras manutenções
6. **Criar testes automatizados** se possível

---

## 📖 Recursos Adicionais

- **Tutorial de Adaptação**: [Clique Aqui](./tutorialAdaptacao.md)
- **Documentação Scrapy**: https://docs.scrapy.org/
- **Documentação Playwright**: https://playwright.dev/python/
- **Exemplos de Referência**: `gazetaDoPovo.py`, `metropoles.py`

---

**💡 Dica**: Sempre teste com URLs reais e atuais do portal. Estruturas HTML mudam frequentemente, então é importante validar os seletores regularmente.