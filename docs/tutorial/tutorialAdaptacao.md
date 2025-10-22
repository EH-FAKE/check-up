# Tutorial: Como Alterar/Criar Spiders e Plays

## Contexto do Projeto

O projeto foi modificado para focar na **extração de conteúdo de notícias** em vez de anúncios. O objetivo agora é extrair o texto das notícias para posterior análise de fake news por uma LLM.

### 🔄 **Campos que PRECISAM ser revisados:**
- **Título**: Seletores podem ter mudado
- **Corpo**: Estrutura de conteúdo pode ter mudado  
- **Description**: NOVO campo - precisa ser identificado
- **Tags**: NOVO campo - precisa ser identificado

### ✅ **Processo de atualização:**
1. **RE-INSPECIONAR** cada portal no navegador atual
2. **COMPARAR** seletores antigos vs estrutura atual
3. **IDENTIFICAR** novos seletores para description e tags
4. **TESTAR** extração com URLs reais atuais

## 🕷️ SPIDERS - Coleta de URLs

### Função dos Spiders
Os spiders são responsáveis por navegar na página inicial dos portais de notícia e coletar URLs de artigos/notícias válidos.

### ⚠️ Alterações Necessárias nos Spiders Existentes

#### 1. Melhorar Filtragem de URLs
Muitos spiders não filtram adequadamente os URLs. Use o **gazetaDoPovo** como referência de boa filtragem:

**❌ Exemplo de filtragem ruim (r7.py):**
```python
def allow_url(self, entry_url):
    return (
        entry_url.startswith("https://")
        and len(entry_url) > 100
        and re.match(
            r"https://(entretenimento|esportes|record|noticias)\.r7\.com", entry_url
        )
    )
```

**✅ Exemplo de filtragem boa (gazetaDoPovo.py):**
```python
def allow_url(self, url: str) -> bool:
    p = urlparse(url)
    path = p.path.rstrip('/')

    # 1) blacklist pure sections
    if path in {"/videos", "/vozes", "/podcasts", "/newsletter", "/ebooks"}:
        self.logger.info(f"Blacklisted URL: {url}")
        return False

    # 2) require at least two non-empty segments (section + slug)
    segments = [seg for seg in path.split('/') if seg]
    if len(segments) < 2:
        self.logger.info(f"Blacklisted URL: {url}")
        return False

    slug = segments[-1]
    # 3a) long slugs by hyphens or 3b) by character length
    if slug.count('-') >= 3 or len(slug) > 30:
        return True

    return False
```

#### 2. Remover yield scrapy.Request Recursivos
**Queremos apenas as notícias da página inicial**, então remova os `yield scrapy.Request` que fazem crawling recursivo:

**❌ Remover:**
```python
def parse(self, response):
    seen = set()
    for entry in response.css("a"):
        url = entry.attrib.get("href")
        if url and url not in seen and self.allow_url(url):
            seen.add(url)
            yield URLItem(url=url)
            yield scrapy.Request(url=url, callback=self.parse)  # ← REMOVER ESTA LINHA
```

**✅ Manter apenas:**
```python
def parse(self, response):
    seen = set()
    for entry in response.css("a"):
        url = entry.attrib.get("href")
        if url and url not in seen and self.allow_url(url):
            seen.add(url)
            yield URLItem(url=url)  # ← MANTER APENAS ISTO
```

### 🆕 Criando um Novo Spider

**Estrutura base para um novo spider:**

```python
import scrapy
from spiders.base import BaseSpider
from spiders.items import URLItem
from urllib.parse import urlparse

class NovoPortalSpider(BaseSpider):
    name = "novoportalspider"
    start_urls = ["https://www.novoportal.com.br/"]
    allowed_domains = ["novoportal.com.br"]

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
        Implementar lógica específica do portal para filtrar apenas URLs de notícias
        """
        p = urlparse(url)
        path = p.path.rstrip('/')
        
        # Exemplo de filtragem - adaptar para cada portal
        segments = [seg for seg in path.split('/') if seg]
        if len(segments) < 2:
            return False
            
        # Verificar se é uma notícia real (slug longo, múltiplos hífens, etc.)
        slug = segments[-1]
        return slug.count('-') >= 2 or len(slug) > 20

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                meta={"dont_redirect": True, "handle_httpstatus_list": [403]},
            )

    def parse(self, response):
        # Adaptar seletor CSS/XPath para o portal específico
        links = response.css("a")  # ou response.xpath("//a")
        
        for link in links:
            url = link.attrib.get("href")
            if not url:
                continue
                
            # Construir URL absoluta
            full_url = response.urljoin(url)
            full_url = full_url.split('#', 1)[0].split('?', 1)[0]  # Remove fragmentos e query params
            
            if self.allow_url(full_url):
                yield URLItem(url=full_url)
```

## 🎭 PLAYS - Extração de Conteúdo

### Função dos Plays
Os plays são responsáveis por acessar cada URL de notícia e extrair o conteúdo: **título, descrição, corpo da matéria e tags**.

### ⚠️ Alterações Necessárias nos Plays Existentes

#### 1. Remover take_screenshot
**Não precisamos mais de screenshots**, apenas do texto. Remover todas as chamadas para `take_screenshot`:

**❌ Remover:**
```python
entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)

# E na criação do EntryItem:
return EntryItem(
    title=entry_title,
    ads=ad_items,
    url=self.url,
    screenshot_path=entry_screenshot_path,  # ← REMOVER
)
```

#### 2. Atualizar TODOS os Seletores
**⚠️ IMPORTANTE**: Portais de notícia frequentemente alteram sua estrutura HTML. **TODOS os seletores precisam ser revisados e atualizados**:

- **Seletores existentes** (título, corpo) podem estar desatualizados
- **Novos seletores** são necessários para description e tags

#### 3. Focar na Extração de Conteúdo
**Remover todo código relacionado a anúncios** e focar na extração de:
- **title**: Título da notícia *(REVISAR seletores existentes)*
- **description**: Subtítulo/resumo da notícia *(NOVO campo - identificar seletores)*
- **body**: Corpo completo da notícia *(REVISAR seletores existentes)*
- **tags**: Tags/categorias da notícia *(NOVO campo - identificar seletores)*

#### 4. Remover Código de Anúncios (opcional)
**Remover:**
- Métodos `find_items`
- Variáveis `n_expected_ads`
- Locators para elementos de anúncio (`.videoCube`, `#taboola-*`, etc.)

### 🆕 Criando um Novo Play

**Estrutura base para um novo play:**

```python
import time
from playwright.sync_api import sync_playwright
from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger

class NovoPortalPlay(BasePlay):
    name = "novoportal"

    @classmethod
    def match(cls, url):
        return "novoportal.com.br" in url

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            
            # Aguardar carregamento do conteúdo principal
            page.wait_for_selector("h1", timeout=30000)
            
            # 1. EXTRAIR TÍTULO
            entry_title = ""
            try:
                # Adaptar seletor para o portal específico
                entry_title = page.locator("h1").first.inner_text()
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract title: {str(e)}")
            
            # 2. EXTRAIR DESCRIÇÃO (quando disponível)
            description = ""
            try:
                # Exemplos de seletores comuns para descrição/subtítulo
                selectors = [
                    ".subtitle",
                    ".description", 
                    ".lead",
                    ".summary",
                    "h2",
                    ".article-subtitle"
                ]
                
                for selector in selectors:
                    try:
                        desc_element = page.locator(selector)
                        if desc_element.count() > 0:
                            description = desc_element.inner_text()
                            if description.strip():
                                break
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract description: {str(e)}")
            
            # 3. EXTRAIR CORPO DA NOTÍCIA
            body = ""
            try:
                # Exemplos de seletores comuns para o corpo da matéria
                selectors = [
                    ".article-content",
                    ".post-content", 
                    ".entry-content",
                    ".content",
                    "article",
                    ".text",
                    ".article-body"
                ]
                
                for selector in selectors:
                    try:
                        content_element = page.locator(selector)
                        if content_element.count() > 0:
                            body = content_element.inner_text()
                            if body.strip():
                                logger.info(f"[{self.name}] Successfully extracted body using: {selector}")
                                break
                    except Exception:
                        continue
                        
                if not body.strip():
                    logger.warning(f"[{self.name}] Failed to extract article body")
                    
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract article body: {str(e)}")
            
            # 4. EXTRAIR TAGS (quando disponível)
            tags = []
            try:
                # Exemplos de seletores comuns para tags
                tag_selectors = [
                    ".tags a",
                    ".categories a", 
                    ".post-tags a",
                    ".article-tags a",
                    "[rel='tag']"
                ]
                
                for selector in tag_selectors:
                    try:
                        tag_elements = page.locator(selector)
                        if tag_elements.count() > 0:
                            for i in range(tag_elements.count()):
                                tag_text = tag_elements.nth(i).inner_text().strip()
                                if tag_text:
                                    tags.append(tag_text)
                            if tags:
                                break
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract tags: {str(e)}")

            return EntryItem(
                title=entry_title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )
```

## 📋 Exemplos de Referência

### ✅ Bons Exemplos para Seguir:

1. **gazetaDoPovo.py** (spider + play) - Boa filtragem de URLs e extração de conteúdo
2. **metropoles.py** (play) - Extração completa com título, descrição, corpo e tags

### ❌ Exemplos que Precisam ser Atualizados:

Todos os outros plays que ainda usam:

- `take_screenshot`
- Código para extração de anúncios (opcional)
- `yield scrapy.Request` recursivo nos spiders

## 🔍 Dicas para Desenvolver

### Para Spiders:
1. **Inspecionar a página inicial** do portal no navegador
2. **Identificar os links de notícias** (geralmente têm URLs com slugs longos)
3. **Criar filtros específicos** para separar notícias de outras páginas
4. **Testar a filtragem** para garantir que só coleta URLs válidos

### Para Plays:
1. **⚠️ SEMPRE inspecionar NOVAMENTE** cada portal - estruturas HTML mudam frequentemente
2. **Identificar seletores para TODOS os 4 campos**:
   - **Título**: Pode ter mudado desde a última versão
   - **Descrição**: NOVO campo - encontrar subtítulo/resumo
   - **Corpo**: Pode ter mudado desde a última versão  
   - **Tags**: NOVO campo - encontrar categorias/etiquetas
3. **Testar múltiplos seletores** como fallback (sites podem ter variações)
4. **Validar na página real** - não confiar apenas no código antigo

### 🛠️ Processo de Identificação de Seletores:

#### 1. Para campos EXISTENTES (título, corpo):
- **Não assumir** que seletores antigos ainda funcionam
- **Re-inspecionar** elementos na página atual
- **Comparar** seletores antigos vs novos

#### 2. Para campos NOVOS (description, tags):
- **Procurar** por subtítulos, resumos, leads
- **Identificar** seções de tags, categorias, etiquetas
- **Testar** se elementos existem em diferentes tipos de notícia

### Ferramentas Úteis:
- **Inspetor do navegador** (F12) para identificar seletores atualizados
- **Console do navegador** para testar seletores CSS em tempo real

## 🚀 Próximos Passos

1. **Atualizar spiders existentes** removendo `yield scrapy.Request` recursivo
2. **Melhorar filtragem de URLs** seguindo o padrão do gazetaDoPovo
3. **⚠️ RE-INSPECIONAR todos os portais** - estruturas HTML podem ter mudado
4. **Atualizar TODOS os seletores existentes** (título, corpo) - não assumir que ainda funcionam
5. **Identificar seletores para campos novos** (description, tags)
6. **Atualizar plays existentes** removendo `take_screenshot` e código de anúncios
7. **Implementar extração completa** (título, descrição, corpo, tags)
8. **Testar cada portal individualmente** com URLs reais atuais
9. **Validar extração** - verificar se todos os 4 campos são capturados corretamente

## 📝 Checklist de Validação

### Spider:
- [ ] Remove `yield scrapy.Request` recursivo
- [ ] Implementa `allow_url()` com boa filtragem
- [ ] Coleta apenas URLs da página inicial
- [ ] URLs coletados são realmente de notícias

### Play:
- [ ] **RE-INSPECIONA** o portal no navegador atual
- [ ] **ATUALIZA seletores existentes** (título, corpo) - não usar código antigo cegamente
- [ ] **IDENTIFICA seletores novos** para description e tags
- [ ] Remove `take_screenshot()` e variáveis relacionadas
- [ ] **TESTA extração** de título com seletores atualizados
- [ ] **IMPLEMENTA extração** de descrição (NOVO campo)
- [ ] **TESTA extração** de corpo com seletores atualizados
- [ ] **IMPLEMENTA extração** de tags (NOVO campo)
- [ ] **VALIDA** que todos os 4 campos são extraídos corretamente
- [ ] Retorna `EntryItem` com os dados corretos
- [ ] **TESTA com URLs reais** do portal atual 