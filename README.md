# Check-up
![cover](https://raw.githubusercontent.com/aosfatos/check-up/refs/heads/develop/cover.png)
O Check-up é um projeto que tem como objetivo analisar a presença de desinformação em anúncios publicitários de saúde que circulam em grandes sites de notícias do Brasil.

Este repositório contém o código de uma ferramenta desenvolvida pelo [**Aos Fatos**](https://aosfatos.org) para examinar os anúncios nativos de dez portais (listados abaixo).

A ferramenta tem três módulos: um crawler que coleta links de cada site, um raspador que captura e arquiva anúncios encontrados e um classificador de anúncios por tema que usa um grande modelo de linguagem (LLM).

Apesar de funcionar apenas com os dez sites cobertos pelo projeto, este código pode ser facilmente adaptado para ser usado em outros endereços, como mostramos abaixo.

O código deste projeto pode ser usado apenas para fins não-comerciais e com atribuição de crédito.

## 🚀 Como Rodar o Projeto

### 📋 Visão Geral do Fluxo de Desenvolvimento
- **Build Docker otimizado:** O `Dockerfile` foi estruturado para build multi-stage, cache eficiente e instalação automática dos browsers do Playwright. Agora o build funciona de forma confiável em qualquer ambiente.
- **Makefile completo:** O novo `Makefile` centraliza todos os comandos de setup, build, testes, coleta de dados, pipelines de desenvolvimento e produção, além de targets para CI/CD local e integração com o GitHub Actions.
- **Workflows CI/CD:** O repositório inclui `.github/workflows/ci.yml` para CI completo (lint, build, testes, compose) e `.github/workflows/local-ci.yml` para rodar checagens rápidas localmente usando [act](https://github.com/nektos/act).
- **Testes otimizados:** Testes unitários, de scraping, integração e infraestrutura podem ser executados facilmente via Makefile ou workflows.
- **Ambiente isolado:** Uso de Docker Compose para orquestrar banco, MinIO, scraper e ferramentas auxiliares.

### ⚡ Comandos Rápidos (Makefile)
```bash
# Setup completo do ambiente (inclui build, browsers, banco, migrações)
make setup

# Setup rápido (reaproveita browsers já instalados)
make setup-fast

# Build da imagem Docker (multi-stage, cache, playwright)
make build

# Iniciar/Parar serviços
make start
make stop

# Limpeza total do ambiente
make clean

# Executar todos os testes (unitários, scraping, integração)
make test

# Testes específicos
make test_rbs
make test_base
make test_integration
make test_scrape-no-openai

# Lint e formatação
make lint
make format

# Pipeline de desenvolvimento (lint, testes rápidos, scraping)
make dev-pipeline

# Pipeline de produção (lint, segurança, build, push)
make prod-pipeline
```

### 🧪 Testes Locais e CI
- **Testes locais rápidos:**
  - `make test` — executa todos os testes
  - `make test_fast` — executa apenas testes rápidos
  - `make test_coverage` — executa testes com relatório de cobertura
- **CI Local com Act:**
  - Instale o [act](https://github.com/nektos/act): `brew install act`
  - Rode o workflow local:
    ```bash
    make ci-act-local      # Workflow local rápido (lint, docker, compose)
    make ci-act-local-lint # Apenas lint local
    make ci-act-local-docker # Teste rápido de build Docker
    ```
  - O workflow local simula `.github/workflows/ci.yml` e garante que o build e os testes funcionarão no CI do GitHub.

### 🐳 Build Docker e Troubleshooting
- O `Dockerfile` agora está multi-stage, instala browsers do Playwright, e faz healthcheck do ambiente.
- Para build manual:
  ```bash
  docker build -t check-up:latest .
  ```
- Para rodar comandos dentro do container:
  ```bash
  make bash
  ```
- Se precisar reinstalar browsers:
  ```bash
  make install-browsers
  ```

### 🗃️ Banco de Dados e MinIO
- O ambiente já sobe PostgreSQL e MinIO via Compose.
- Variáveis `.env` controlam acesso e credenciais.
- Os resultados de scraping são salvos no banco e no MinIO automaticamente.

### 🕸️ Estrutura de Spiders e Plays
- Cada portal tem um spider Scrapy (`spiders/`) e um script Playwright (`plays/`).
- Para adicionar novo portal, siga o modelo dos arquivos existentes e veja exemplos no README.
- O scraping pode ser executado com ou sem classificação LLM, e agora aceita argumentos de timeout e plataforma via CLI:
  ```bash
  make scrape-no-ai TIMEOUT=900 PLATFORM=firefox
  ```

### 🧑‍💻 Contribuição e Fluxo de Branch/Commit
- Siga o guia de contribuição (ver [política de branches](https://eh-fake.github.io/docs/guia-de-contribuicao/politica-de-branches/), [guia de commits](https://eh-fake.github.io/docs/guia-de-contribuicao/guia-de-commits/)).
- Use Conventional Commits e Git Flow para branch/PR.
- Nunca faça push direto para `main` ou `develop`.
- Sempre rode os testes e o lint antes de abrir PR.

---

### 📋 Pré-requisitos
- Docker e Docker Compose instalados
- Make (disponível por padrão no macOS e Linux)

### 🔧 Configuração Inicial

**1. Setup completo do ambiente:**
```bash
make setup
```
Este comando faz toda a configuração inicial:
- Cria o arquivo `.env` a partir do `env.example`
- Inicia os serviços Docker (PostgreSQL, MinIO, scraper)
- Aguarda o banco de dados ficar pronto
- Cria as tabelas necessárias
- Executa as migrações

### 📊 Fluxo de Coleta de Dados

O processo de coleta acontece em duas etapas principais:

**🕷️ Etapa 1: Crawling (Coleta de URLs)**

Colete URLs de todos os portais funcionais:
```bash
make crawl_all_working
```

Ou execute individualmente:
```bash
make crawl_metropoles    # Portal Metrópoles
make crawl_veja         # Portal Veja  
make crawl_r7           # Portal R7
make crawl_uol          # Portal UOL
make crawl_maisgoias    # Portal MaisGoiás
make crawl_aliadosBrasil # Portal AliadosBrasil
make crawl_ig           # Portal IG
make crawl_folha        # Portal Folha
```

**📰 Etapa 2: Scraping (Extração de Anúncios)**

Execute o scraping de todos os portais:
```bash
make scrape_all_working
```

Ou execute por portal específico:
```bash
make scrape_metropoles     # Scraping do Metrópoles
make scrape_maisgoias      # Scraping do MaisGoiás
make scrape_aliadosbrasil  # Scraping do AliadosBrasil
make scrape_ig             # Scraping do IG
make scrape_veja           # Scraping da Veja
make scrape_r7             # Scraping do R7
make scrape_uol            # Scraping do UOL
make scrape_folha          # Scraping da Folha
```

### ⚡ Workflows Automatizados

**Pipeline completo (crawl + scraping):**
```bash
make pipeline_complete
```

**Coleta otimizada:**
```bash
make collect_working
```

### 🛠️ Comandos Úteis

**Acessar o container:**
```bash
make bash
```

**Ver logs dos serviços:**
```bash
docker compose logs -f
```

**Parar serviços:**
```bash
make stop
```

**Ver todos os comandos disponíveis:**
```bash
make help
```

### � Onde os Dados São Salvos

- **URLs coletadas**: Salvos no banco PostgreSQL (tabela `URLQueue`)
- **Anúncios extraídos**: Salvos no banco PostgreSQL (tabela `Advertisement`) 
- **Screenshots e arquivos**: Salvos no MinIO (acessível em `http://localhost:9001`)
- **Logs**: Disponíveis via `docker compose logs`

### � Configurações Importantes

**Variáveis de ambiente (arquivo `.env`):**
- Credenciais dos portais (se necessário)
- Configurações do banco PostgreSQL
- Configurações do MinIO para armazenamento
- Chave da API OpenAI (opcional, para classificação)

---

## 📊 Portais de Notícias Suportados

Este projeto coleta dados dos seguintes portais brasileiros:

### ✅ **Portais Funcionais** (Totalmente operacionais)
- **[Metrópoles](https://www.metropoles.com)** - `make crawl_metropoles` / `make scrape_metropoles`
- **[IG](https://www.ig.com.br)** - `make crawl_ig` / `make scrape_ig`  
- **[MaisGoiás](https://www.maisgoias.com.br)** - `make crawl_maisgoias` / `make scrape_maisgoias`
- **[AliadosBrasil](https://www.aliadosbrasiloficial.com.br)** - `make crawl_aliadosBrasil` / `make scrape_aliadosbrasil`
- **[Veja](https://veja.abril.com.br)** - `make crawl_veja` / `make scrape_veja`
- **[R7](https://www.r7.com)** - `make crawl_r7` / `make scrape_r7`
- **[UOL](https://www.uol.com.br)** - `make crawl_uol` / `make scrape_uol`
- **[Folha](https://www.folha.uol.com.br)** - `make crawl_folha` / `make scrape_folha`

### 🔧 **Em Desenvolvimento**
- **[Estadão](https://www.estadao.com.br)** - Necessita ajustes nos seletores CSS
- **[Globo](https://oglobo.globo.com/)** - Requer configurações específicas de autenticação
- **[RBS](https://www.clicrbs.com.br)** - Spider em desenvolvimento
- **[Terra](https://www.terra.com.br)** - Aguardando implementação

## 🗄️ Estrutura do Banco de Dados

As seguintes tabelas são criadas automaticamente durante o setup:

- **Portal**: Informações dos portais analisados
- **Entry**: Notícias coletadas de cada portal  
- **Advertisement**: Anúncios encontrados nas notícias
- **URLQueue**: Fila de URLs para o processo de scraping
- **QueueStatus**: Status de cada fila de scraping

**Nota:** Mais detalhes sobre a estrutura das tabelas estão disponíveis no arquivo `models.py`.

## 🧑‍💻 Desenvolvimento e Contribuição

### 🐳 Build Docker e Troubleshooting
- O `Dockerfile` usa multi-stage build com instalação automática dos browsers do Playwright
- Para build manual: `docker build -t check-up:latest .`
- Para acessar o container: `make bash`

### 🧪 Estrutura de Spiders e Plays
- Cada portal tem um spider Scrapy (`spiders/`) e um script Playwright (`plays/`)
- Para adicionar novo portal, siga o modelo dos arquivos existentes
- O scraping aceita argumentos de timeout e plataforma via CLI

### 📝 Fluxo de Contribuição
- Siga as políticas de branches e commits do projeto
- Use Conventional Commits e Git Flow
- Sempre rode os testes antes de abrir PR
- Nunca faça push direto para `main` ou `develop`

## 🚨 Troubleshooting

### Problemas Comuns

**1. Erro "Playwright browsers not installed"**
```bash
# Se o IG spider falhar, reconstrua a imagem Docker:
docker compose down
docker compose build --no-cache
make start
```

**2. Container não conecta ao banco**
```bash
# Aguarde o banco ficar pronto:
make wait-for-db
# Ou reinicie os serviços:
make stop && make start
```

**3. MinIO não acessível**
```bash
# Verifique se o MinIO está rodando:
docker compose ps
# Acesse: http://localhost:9001 (admin: minioadmin/minioadmin)
```

**4. Containers órfãos**
```bash
# Limpe containers órfãos:
docker compose down --remove-orphans
make prune
```

### 💡 Exemplos Práticos

**Coleta rápida de um portal específico:**
```bash
# Setup inicial (só uma vez)
make setup

# Coleta do Metrópoles (exemplo)
make crawl_metropoles
make scrape_metropoles
```

**Pipeline completo para produção:**
```bash
# Coleta de todos os portais funcionais
make pipeline_complete
```

**Monitoramento em tempo real:**
```bash
# Terminal 1 - Execute a coleta
make crawl_all_working

# Terminal 2 - Monitore os logs  
docker compose logs -f scraper
```

**Acesso aos dados coletados:**
```bash
# Via container
make bash
python -c "
from models import *
print('URLs coletadas:', URLQueue.select().count())
print('Anúncios encontrados:', Advertisement.select().count())
"

# Via MinIO Console
open http://localhost:9001
```

### 2- Executar as migrações do banco de dados
Para executar as migrações do banco de dados, utilize:

`make migrate_db`

Este comando irá aplicar todas as migrações pendentes no banco de dados.

### 3- Coletar URL de notícias
O primeiro passo é coletar URLs de notícias nas páginas iniciais dos portais. Cada portal possui um "spider" implementado com a biblioteca Scrapy, localizado no diretório `spiders/`.

Exemplo de script para a [Folha]("https://www.folha.uol.com.br"): `spiders/folha.py`.

Para executar a coleta de todos os portais, utilize:

`make crawl`

### 4- Coletar Informações dos anúncios 

Após a coleta das notícias, o próximo passo é raspar os anúncios presentes nas páginas das notícias. Esse processo utiliza a biblioteca [Playwright](https://playwright.dev/), para simular a navegação em um browser.

Para executar a coleta de todos os anúncios basta executar o comando:

`make scrape`

### 5- Adicionar um novo portal

##### 5.1 - Adicionar novo portal ao Banco de Dados
Para adicionar um novo portal as coletas, como por exemplo [Correio Braziliense](https://www.correiobraziliense.com.br/), insira as informações do portal no Banco de Dados:

```
make bash

python add_portal.py "Correio Braziliense" "https://www.correiobraziliense.com.br/"
```

##### 5.2 - Criar o spider
Crie um arquivo `spiders/correio.py` com o seguinte conteúdo:

```python
import scrapy

from spiders.base import BaseSpider
from spiders.items import URLItem


class CorreioBrazilienseSpider(BaseSpider):
    name = "correiobraziliensespider"
    start_urls = ["https://www.correiobraziliense.com.br/"]
    allowed_domains = ["correiobraziliense.com.br"]

    def allow_url(self, entry_url):
        return "https://correiobraziliense.com.br" in entry_url

    def parse(self, response):
        url_item = URLItem()
        for entry in response.css('a[title][data-tb-link]::attr(href)')
            url = entry.attrib.get("href")
            if url and self.allow_url(url):
                url_item["url"] = url
                yield url_item
                yield scrapy.Request(url=url, callback=self.parse)
```

Este script irá buscar novas notícias publicadas na página inicial do Correio Braziliense.

##### 5.3 - Criar o Script Playwright
Também será necessário criar um script Playwright correspondente ao novo portal para coletar anúncios. Crie um arquivo em `plays/correio.py` com o seguinte código:

```python
import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger


class CorreioBraziliensePlay(BasePlay):
    name = "correiobraziliense"
    n_expected_ads = 10  # Add the minimum amount of expected ads

    @classmethod
    def match(cls, url):
        return "correiobraziliense.com.br" in url

    def find_items(self, html_content) -> AdItem:
        return AdItem(
            title=get_or_none(r'title="(.*?)"', html_content),
            url=get_or_none(r'href="(.*?)"', html_content),
            thumbnail_url=get_or_none(r'url\(&quot;(.*?)&quot;\)', html_content),
            tag=get_or_none(r'<span class="branding-inner".*?>(.*?)<\/span>', html_content),
        )

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            logger.info(f"[{self.name}] Searching for ads...")
            page.locator("#taboola-below-article-thumbnails").scroll_into_view_if_needed()

            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)
            entry_title = page.locator("title").inner_text()
            time.sleep(self.wait_time * 2)

            elements = page.locator(".videoCube")
            ad_items = []
            visible_elements = []
            for i in range(elements.count()):
                element = elements.nth(i)
                if not element.is_visible():
                    continue
                visible_elements.append(element)
                content = element.inner_html()
                ad_item = self.find_items(content)
                ad_items.append(ad_item)

            return EntryItem(
                title=entry_title,
                ads=ad_items,
                url=self.url,
                screenshot_path=entry_screenshot_path,
            )
```

Este script irá procurar por anúncios nativos em cada umas das notícias coletadas no
portal Correio Braziliense.

**Nota:** o método `run` é responsavel por procurar os anúncios na estrutura HTML do site. Ele
deve ser desenvolvido de acordo com estrutura de cada portal.

## Classificação dos anúncios com LLM
Cada anúncio coletado é classificado em uma das 45 categorias descritas em `llm/categories.py`.
Esta classificação é opcional, para ativá-la basta adicionar sua chave de API da OpenAI à variável `OPENAI_API_KEY`.
Para mais informações acesse o site da [OpenAI](https://platform.openai.com/docs/api-reference/api-keys).

## Armazenamento de arquivos
Durante a coleta de anúncios, o script que simula o navegador irá registrar capturas de tela (`screenshots`) das páginas de notícias dos portais e das páginas dos anúncios.

Para armazenar essas imagens, é necessário configurar um [Bucket S3](https://aws.amazon.com/pt/s3/) na Amazon Web Services (AWS) e atualizar as credenciais de acesso no arquivo `.env` com os seguintes parâmetros:

- **AWS_ACCESS_KEY_ID**
- **AWS_SECRET_ACCESS_KEY**
- **AWS_S3_REGION_NAME**
- **AWS_BUCKET_NAME**

Os endereços S3 das imagens serão registrados no banco de dados do projeto, enquanto os arquivos das imagens serão armazenados no bucket configurado.

## Importante
Os scripts dependem da estrutura HTML dos portais e podem precisar de ajustes após atualizações nos sites.


## Executando um spider específico

Para executar apenas um spider específico, você pode passar o nome do spider como argumento:

```
    docker compose run scraper python crawl.py metropolesspider   
```

Para verificar o banco de dados, você pode executar o seguinte comando:

```
    docker compose run scraper python check_db.py
```

## Para nosso caso de uso

```
make setup
```

```
make start
```

```
make crawl_metropoles # ou qualquer outro portal de notícias.
```

```
make scrape_no_openai # ou qualquer outro portal de notícias.
```

```
make stop # para parar os serviços.
```

```
make clean # para limpar os serviços.
```

```
make help # para ver todos os comandos disponíveis.
```