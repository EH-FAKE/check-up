# Check-up

![cover](https://raw.githubusercontent.com/aosfatos/check-up/refs/heads/develop/cover.png)

O Check-up é um projeto de **extração de conteúdo de notícias** de portais brasileiros para análise de desinformação. Este repositório contém ferramentas para coletar e extrair o texto completo de notícias de diversos portais de notícia do Brasil.

## 🎯 Objetivo do Projeto

Este projeto foi adaptado a partir de uma ferramenta original do [**Aos Fatos**](https://aosfatos.org) que analisava anúncios publicitários. Agora, o foco é na **extração de conteúdo de notícias** para posterior análise de fake news por uma equipe especializada.

### 🔄 Adaptação Realizada

- **Antes**: Coletava anúncios publicitários para verificar fake news
- **Agora**: Extrai conteúdo completo de notícias (título, descrição, corpo, tags) para análise de desinformação

### 🏗️ Arquitetura

A ferramenta possui dois módulos principais:

- **Crawler (Spiders)**: Coleta URLs de notícias das páginas iniciais dos portais
- **Extrator (Plays)**: Acessa cada notícia e extrai o conteúdo completo

O código pode ser facilmente adaptado para novos portais de notícia, seguindo os padrões estabelecidos.

**Licença**: Este código pode ser usado apenas para fins não-comerciais e com atribuição de crédito.

## 🚀 Como Rodar o Projeto

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

### 📊 Fluxo de Extração de Notícias

O processo de extração acontece em duas etapas principais:

**🕷️ Etapa 1: Crawling (Coleta de URLs de Notícias)**

Colete URLs de notícias de todos os portais funcionais:

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
make crawl_brasildefato  # Portal Brasil de Fato
```

**📰 Etapa 2: Scraping (Extração de Conteúdo das Notícias)**

Execute a extração de conteúdo de todos os portais:

```bash
make scrape_all_working
```

Ou execute por portal específico:

```bash
make scrape_metropoles     # Extração do Metrópoles
make scrape_maisgoias      # Extração do MaisGoiás
make scrape_aliadosbrasil  # Extração do AliadosBrasil
make scrape_ig             # Extração do IG
make scrape_veja           # Extração da Veja
make scrape_r7             # Extração do R7
make scrape_uol            # Extração do UOL
make scrape_folha          # Extração da Folha
make scrape_brasildefato   # Extração do Brasil de Fato
```

### 📋 Conteúdo Extraído

Para cada notícia, o sistema extrai:

- **Título**: Título principal da notícia
- **Descrição**: Subtítulo ou resumo da notícia
- **Corpo**: Texto completo da matéria
- **Tags**: Categorias e etiquetas associadas à notícia

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
- **Notícias extraídas**: Salvos no banco PostgreSQL (tabela `Entry`) com título, descrição, corpo e tags
- **Arquivos temporários**: Salvos no MinIO (acessível em `http://localhost:9001`)
- **Logs**: Disponíveis via `docker compose logs`

### � Configurações Importantes

**Variáveis de ambiente (arquivo `.env`):**

- Credenciais dos portais (se necessário)
- Configurações do banco PostgreSQL
- Configurações do MinIO para armazenamento
- Configurações de timeout e retry para extração

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
- **[Brasil de Fato](https://www.brasildefato.com.br)** - `make crawl_brasildefato` / `make scrape_brasildefato`

### 🔧 **Em Desenvolvimento**

- **[Estadão](https://www.estadao.com.br)** - Necessita ajustes nos seletores CSS
- **[Globo](https://oglobo.globo.com/)** - Requer configurações específicas de autenticação
- **[RBS](https://www.clicrbs.com.br)** - Spider em desenvolvimento
- **[Terra](https://www.terra.com.br)** - Aguardando implementação

## 🗄️ Estrutura do Banco de Dados

As seguintes tabelas são criadas automaticamente durante o setup:

- **Portal**: Informações dos portais analisados
- **Entry**: Notícias coletadas de cada portal com título, descrição, corpo e tags
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

### 📚 Guias de Contribuição

**⚠️ IMPORTANTE**: Antes de contribuir, leia os tutoriais apropriados:

- **[TUTORIAL_CRIACAO_DO_ZERO.md](./TUTORIAL_CRIACAO_DO_ZERO.md)** - Para criar scrapers completamente novos:

  - Guia passo-a-passo desde a análise do portal
  - Exemplos práticos com código completo
  - Troubleshooting e problemas comuns
  - Testes e validação

- **[TUTORIAL_SPIDERS_PLAYS.md](./TUTORIAL_SPIDERS_PLAYS.md)** - Para adaptar scrapers existentes:
  - Guia para adaptar spiders e plays existentes
  - Checklist de validação para garantir qualidade
  - Exemplos práticos de boas práticas
  - Dicas para identificar seletores atualizados

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

### 4- Extrair Conteúdo das Notícias

Após a coleta das URLs, o próximo passo é extrair o conteúdo completo das notícias. Esse processo utiliza a biblioteca [Playwright](https://playwright.dev/) para simular a navegação em um browser.

Para executar a extração de todas as notícias:

`make scrape`

### 5- Adicionar um Novo Portal

Para adicionar um novo portal, consulte o **[TUTORIAL_SPIDERS_PLAYS.md](./TUTORIAL_SPIDERS_PLAYS.md)** que contém instruções detalhadas sobre:

- Como criar spiders para coleta de URLs
- Como criar plays para extração de conteúdo
- Exemplos práticos e boas práticas
- Checklist de validação

## 💾 Armazenamento de Dados

Os dados extraídos são armazenados no banco PostgreSQL e arquivos temporários no MinIO. Para configurações específicas de armazenamento, consulte o arquivo `.env`.

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

## 🚀 Exemplo de Uso Rápido

```bash
# Setup inicial (só uma vez)
make setup

# Iniciar serviços
make start

# Coletar URLs de um portal específico
make crawl_metropoles  # ou qualquer outro portal de notícias

# Extrair conteúdo das notícias
make scrape_metropoles  # ou qualquer outro portal de notícias

# Parar serviços
make stop

# Limpar serviços
make clean

# Ver todos os comandos disponíveis
make help
```
