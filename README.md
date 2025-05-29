# Check-up
![cover](https://raw.githubusercontent.com/aosfatos/check-up/refs/heads/develop/cover.png)
O Check-up é um projeto que tem como objetivo analisar a presença de desinformação em anúncios publicitários de saúde que circulam em grandes sites de notícias do Brasil.

Este repositório contém o código de uma ferramenta desenvolvida pelo [**Aos Fatos**](https://aosfatos.org) para examinar os anúncios nativos de dez portais (listados abaixo).

A ferramenta tem três módulos: um crawler que coleta links de cada site, um raspador que captura e arquiva anúncios encontrados e um classificador de anúncios por tema que usa um grande modelo de linguagem (LLM).

Apesar de funcionar apenas com os dez sites cobertos pelo projeto, este código pode ser facilmente adaptado para ser usado em outros endereços, como mostramos abaixo.

O código deste projeto pode ser usado apenas para fins não-comerciais e com atribuição de crédito.

## 🚀 CI/CD, Build e Desenvolvimento Local

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

## Portais de notícias
Este repositório inicialmente contempla a coleta de notícias dos seguintes portais:

 - [Estadão](https://www.estadao.com.br)
 - [Folha](https://www.folha.uol.com.br)
 - [Globo](https://oglobo.globo.com/)
 - [IG](https://www.ig.com.br)
 - [Metrópoles](https://www.metropoles.com)
 - [R7](https://www.r7.com)
 - [RBS](https://www.clicrbs.com.br)
 - [Terra](https://www.terra.com.br)
 - [Veja](https://veja.abril.com.br)
 - [UOL](https://www.uol.com.br)

## Execução dos Scripts

### Iniciar os Serviços

Para iniciar os serviços necessários, utilize o comando:

`make start`

Este comando inicia um container docker com um banco de dados
e um container com `shell` com Python instalado.


### 1- Iniciar as tabelas do banco de dados
Para criar as tabelas necessárias, execute:

`make init_db`

As seguintes tabelas serão criadas:

 - Portal: Informações dos portais analisados.
 - Entry: Notícias coletadas de cada portal.
 - Advertisement: Anúncios encontrados nas notícias.
 - URLQueue: Fila de URLs para o processo de scraping.
 - QueueStatus: Status de cada fila de scraping.

**Nota:** mais detalhes sobre a estrutura das tabelas estão disponíveis no arquivo `models.py`.

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