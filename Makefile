# =========================================================================
# Check-up - Ferramenta de análise de anúncios de saúde
# =========================================================================

# Variáveis para reutilização
DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_CI = docker compose -f compose.ci.yml
SCRAPER_RUN = $(DOCKER_COMPOSE) run --rm scraper python
SCRAPER_EXEC = $(DOCKER_COMPOSE) exec scraper
DB_TIMEOUT = 60

# CI/CD Variables
IMAGE_NAME = check-up
IMAGE_TAG = test
REGISTRY = ghcr.io
FULL_IMAGE_NAME = $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

# Act variables
ACT_PLATFORM = --platform ubuntu-latest=catthehacker/ubuntu:act-latest
ACT_ARCH = --container-architecture linux/amd64
ACT_COMMON = $(ACT_PLATFORM) $(ACT_ARCH)
ACT_WITH_TOKEN = $(ACT_COMMON) --secret GITHUB_TOKEN=$$(gh auth token 2>/dev/null || echo "mock_token")

# =========================================================================
# Targets Phony
# =========================================================================
.PHONY: help setup env start stop clean
.PHONY: init_db migrate_db wait-for-db
.PHONY: crawl scrape collect
.PHONY: bash install-browsers check-browsers
.PHONY: test test_rbs test_base test_integration test_ci
.PHONY: build build-cache push pull
.PHONY: ci-setup ci-test ci-clean ci-act
.PHONY: lint format security
.PHONY: data-dirs

# Target padrão
all: help

# =========================================================================
# Configuração do Ambiente
# =========================================================================
env:
	@if [ ! -f .env ]; then \
		echo "📝 Criando arquivo .env a partir do env.example..."; \
		cp env.example .env; \
		echo "✅ Arquivo .env criado. Configure as variáveis conforme necessário."; \
	else \
		echo "ℹ️  Arquivo .env já existe."; \
	fi

# Criar diretórios de dados necessários
data-dirs:
	@echo "📁 Criando diretórios de dados..."
	@mkdir -p data/postgres data/minio screenshots sessions logs
	@chmod 755 data/postgres data/minio screenshots sessions logs
	@echo "✅ Diretórios criados!"

# Instalação dos browsers do Playwright
install-browsers:
	@echo "📦 Instalando browsers do Playwright..."
	@echo "⚠️  Normalmente não é necessário - browsers são instalados durante o build"
	$(SCRAPER_EXEC) playwright install firefox
	@echo "✅ Browsers instalados com sucesso!"

# Verificação se browsers estão instalados
check-browsers:
	@echo "🔍 Verificando browsers do Playwright..."
	@$(SCRAPER_EXEC) python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('✅ Playwright configurado corretamente'); p.stop()" 2>/dev/null || \
	(echo "❌ Browsers não instalados. Execute 'make install-browsers'" && exit 1)

setup: env data-dirs start wait-for-db check-browsers init_db migrate_db
	@echo "✅ Ambiente configurado com sucesso!"

# Setup rápido (sem reinstalar browsers se já existirem)
setup-fast: env data-dirs start wait-for-db check-browsers init_db migrate_db
	@echo "✅ Ambiente configurado rapidamente!"

# =========================================================================
# Docker Build & Registry
# =========================================================================
build:
	@echo "🐳 Building Docker image..."
	docker build \
		--tag $(IMAGE_NAME):$(IMAGE_TAG) \
		--tag $(IMAGE_NAME):latest \
		--cache-from $(IMAGE_NAME):latest \
		--build-arg BUILDKIT_INLINE_CACHE=1 \
		.
	@echo "✅ Docker image built successfully!"

build-cache:
	@echo "🐳 Building Docker image with enhanced caching..."
	DOCKER_BUILDKIT=1 docker build \
		--tag $(IMAGE_NAME):$(IMAGE_TAG) \
		--tag $(IMAGE_NAME):latest \
		--cache-from $(FULL_IMAGE_NAME) \
		--cache-from $(IMAGE_NAME):latest \
		--build-arg BUILDKIT_INLINE_CACHE=1 \
		--progress=plain \
		.
	@echo "✅ Docker image built with cache!"

push:
	@echo "📤 Pushing image to registry..."
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(FULL_IMAGE_NAME)
	docker push $(FULL_IMAGE_NAME)
	@echo "✅ Image pushed successfully!"

pull:
	@echo "📥 Pulling image from registry..."
	docker pull $(FULL_IMAGE_NAME) || true
	docker tag $(FULL_IMAGE_NAME) $(IMAGE_NAME):$(IMAGE_TAG) || true
	@echo "✅ Image pulled successfully!"

# =========================================================================
# Gerenciamento de Containers
# =========================================================================
start: env data-dirs
	$(DOCKER_COMPOSE) up -d --remove-orphans
	@echo "✅ Serviços iniciados. Use 'docker compose logs -f' para logs."

stop:
	$(DOCKER_COMPOSE) down --remove-orphans
	@echo "✅ Serviços parados."

restart: stop start
	@echo "✅ Serviços reiniciados."

clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f
	@echo "✅ Ambiente limpo completamente."

clean-all: clean
	@echo "🧹 Limpeza completa (incluindo imagens)..."
	docker image prune -af
	docker volume prune -f
	docker network prune -f
	@echo "✅ Limpeza completa finalizada!"

bash:
	$(DOCKER_COMPOSE) exec -it scraper bash

logs:
	$(DOCKER_COMPOSE) logs -f

# =========================================================================
# Banco de Dados
# =========================================================================
wait-for-db:
	@echo "⏳ Aguardando PostgreSQL..."
	@$(DOCKER_COMPOSE) exec db sh -c 'until pg_isready -U postgres -h localhost; do sleep 1; done'
	@echo "✅ PostgreSQL pronto!"

# Crawling específico por portal
crawl-veja: check-browsers
	$(SCRAPER_RUN) crawl.py vejaspider

crawl-r7: check-browsers
	$(SCRAPER_RUN) crawl.py r7spider

crawl-uol: check-browsers
	$(SCRAPER_RUN) crawl.py uolspider

crawl-maisgoias: check-browsers
	$(SCRAPER_RUN) crawl.py maisgoiasspider

crawl-aliadosbrasil: check-browsers
	$(SCRAPER_RUN) crawl.py aliadosbrasilspider

crawl-ig: check-browsers
	$(SCRAPER_RUN) crawl.py igspider

crawl-folha: check-browsers
	$(SCRAPER_RUN) crawl.py folhaspider

# Scraping específico por portal (sem OpenAI)
scrape-metropoles: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py --platform metropoles.com

scrape-maisgoias: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py --platform maisgoias.com.br

scrape-aliadosbrasil: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py --platform aliadosbrasiloficial.com.br

scrape-ig: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py --platform ig.com.br

scrape-veja: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py --platform veja.abril.com.br

scrape-r7: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py --platform r7.com

scrape-uol: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py --platform uol.com.br

scrape-folha: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py --platform folha.uol.com.br

# Workflows de coleta por grupos
crawl-all-portals: crawl-metropoles crawl-veja crawl-r7 crawl-uol crawl-maisgoias crawl-aliadosbrasil crawl-ig crawl-folha crawl-rbs
	@echo "✅ Crawl de todos os portais concluído!"

scrape-all-portals: scrape-metropoles scrape-maisgoias scrape-aliadosbrasil scrape-ig scrape-veja scrape-r7 scrape-uol scrape-folha scrape-rbs
	@echo "✅ Scraping de todos os portais concluído!"

# Pipeline completo: crawl + scrape
pipeline-complete: crawl-all-portals scrape-all-portals
	@echo "✅ Pipeline completo concluído!"

# Web Application Commands
install-web:
	@echo "📦 Instalando dependências web..."
	cd web/server && pip install -r requirements.txt
	cd web/client && pnpm install
	@echo "✅ Dependências web instaladas!"

run-backend:
	@echo "🚀 Iniciando backend local..."
	cd web/server && uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "🚀 Iniciando frontend local..."
	cd web/client && pnpm run dev --host 0.0.0.0

start-web: start
	@echo "🚀 Iniciando aplicação web com Docker..."
	$(DOCKER_COMPOSE) --profile web up -d backend frontend

stop-web:
	@echo "🛑 Parando aplicação web..."
	$(DOCKER_COMPOSE) --profile web down
init_db:
	$(SCRAPER_RUN) create_db.py

migrate_db:
	$(SCRAPER_RUN) migrate_db.py

db-shell:
	$(DOCKER_COMPOSE) exec db psql -U postgres -d healthcheck

# =========================================================================
# CI/CD Pipeline
# =========================================================================
ci-setup:
	@echo "🔧 Configurando ambiente de CI..."
	@mkdir -p data/ci-postgres data/ci-minio
	@chmod 755 data/ci-postgres data/ci-minio
	@echo "✅ Ambiente CI configurado!"

ci-test: ci-setup
	@echo "🧪 Executando testes no ambiente CI..."
	$(DOCKER_COMPOSE_CI) up -d --wait
	$(DOCKER_COMPOSE_CI) run --rm scraper pytest tests/ -v --tb=short --strict-markers --disable-warnings
	@echo "✅ Testes CI completados!"

ci-clean:
	@echo "🧹 Limpando ambiente CI..."
	$(DOCKER_COMPOSE_CI) down -v --remove-orphans
	@echo "✅ Ambiente CI limpo!"

# =========================================================================
# Act (GitHub Actions local testing)
# =========================================================================
ci-act-lint:
	@echo "🎭 Executando job de lint com act..."
	@command -v act >/dev/null 2>&1 || { echo "❌ Act não instalado. Instale com: brew install act"; exit 1; }
	act $(ACT_WITH_TOKEN) --job lint

ci-act-build:
	@echo "🎭 Executando job de build com act..."
	@command -v act >/dev/null 2>&1 || { echo "❌ Act não instalado. Instale com: brew install act"; exit 1; }
	act $(ACT_WITH_TOKEN) --job build

ci-act-test:
	@echo "=== 🧪 Executando CI - Test com Act ==="
	@echo ""
	@echo "🎭 Executando job de test-with-compose com act..."
	@echo "Isso simulará localmente o job de testes do CI..."
	act $(ACT_WITH_TOKEN) --job test-with-compose

ci-act-all:
	@echo "🎭 Executando pipeline completo com act..."
	@command -v act >/dev/null 2>&1 || { echo "❌ Act não instalado. Instale com: brew install act"; exit 1; }
	act $(ACT_WITH_TOKEN)

ci-act-local:
	@echo "🎭 Executando workflow local rápido com act..."
	@command -v act >/dev/null 2>&1 || { echo "❌ Act não instalado. Instale com: brew install act"; exit 1; }
	act $(ACT_WITH_TOKEN) --workflows .github/workflows/local-ci.yml

ci-act-local-lint:
	@echo "🎭 Executando lint local rápido com act..."
	@command -v act >/dev/null 2>&1 || { echo "❌ Act não instalado. Instale com: brew install act"; exit 1; }
	act $(ACT_WITH_TOKEN) --workflows .github/workflows/local-ci.yml --job local-lint

ci-act-local-docker:
	@echo "🎭 Executando Docker test local com act..."
	@command -v act >/dev/null 2>&1 || { echo "❌ Act não instalado. Instale com: brew install act"; exit 1; }
	act $(ACT_WITH_TOKEN) --workflows .github/workflows/local-ci.yml --job local-docker

ci-act-list:
	@echo "📋 Listando jobs disponíveis com act..."
	@command -v act >/dev/null 2>&1 || { echo "❌ Act não instalado. Instale com: brew install act"; exit 1; }
	act --list

ci-act-version:
	@echo "📝 Verificando versão do act..."
	@command -v act >/dev/null 2>&1 || { echo "❌ Act não instalado. Instale com: brew install act"; exit 1; }
	act --version

ci-act-setup:
	@echo "🔧 Configurando Act com token automático..."
	@command -v gh >/dev/null 2>&1 || { echo "❌ GitHub CLI não instalado. Instale com: brew install gh"; exit 1; }
	@command -v act >/dev/null 2>&1 || { echo "❌ Act não instalado. Instale com: brew install act"; exit 1; }
	@gh auth status >/dev/null 2>&1 || { echo "❌ GitHub CLI não autenticado. Execute: gh auth login"; exit 1; }
	@echo "✅ Act configurado e pronto para uso!"
	@echo "💡 Use: make ci-act-local para testes rápidos"

# =========================================================================
# Code Quality
# =========================================================================
lint:
	@echo "🔍 Executando análise de código..."
	$(SCRAPER_RUN) flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --max-line-length=150
	$(SCRAPER_RUN) flake8 . --count --exit-zero --max-complexity=15 --max-line-length=150 \
		--extend-ignore=W191,W293,W292,E303,F401,F841,E712,E124,E201 --statistics
	@echo "✅ Análise de código concluída!"

format:
	@echo "📝 Formatando código..."
	$(SCRAPER_RUN) black . --line-length=150 --exclude="/(\.git|\.venv|build|dist)/"
	$(SCRAPER_RUN) isort . --profile black --line-length=150
	@echo "✅ Código formatado!"

security:
	@echo "🔒 Executando análise de segurança..."
	$(SCRAPER_RUN) safety check
	$(SCRAPER_RUN) bandit -r . -x tests/
	@echo "✅ Análise de segurança concluída!"

# =========================================================================
# Testes
# =========================================================================
# Executa todos os testes
test:
	@echo "🧪 Executando todos os testes..."
	$(DOCKER_COMPOSE) run --rm scraper python -m pytest tests/ -v --tb=short

# Testes específicos do RBS (melhorias implementadas)
test_rbs:
	@echo "🧪 Executando testes do RBS..."
	$(DOCKER_COMPOSE) run --rm scraper python -m pytest tests/plays/test_rbs.py -v

# Testes da classe base (otimizações)
test_base:
	@echo "🧪 Executando testes do BasePlay..."
	$(DOCKER_COMPOSE) run --rm scraper python -m pytest tests/plays/test_base.py -v

# Testes de scraping sem OpenAI
test_scrape-no-openai:
	@echo "🧪 Executando testes do scrape_no_openai..."
	$(DOCKER_COMPOSE) run --rm scraper python -m pytest tests/test_scrape_no_openai.py -v

# Testes de integração
test_integration:
	@echo "🧪 Executando testes de integração..."
	$(DOCKER_COMPOSE) run --rm scraper python -m pytest tests/test_integration_improvements.py -v

# Executa testes com cobertura
test_coverage:
	@echo "🧪 Executando testes com relatório detalhado..."
	$(DOCKER_COMPOSE) run --rm scraper python -m pytest tests/ -v --tb=long --cov=. --cov-report=html

# Executa testes sem warnings
test_no-warnings:
	@echo "🚫 Executando testes sem warnings..."
	$(DOCKER_COMPOSE) run --rm scraper python -m pytest tests/ -v --disable-warnings

# Executa testes mostrando todos os warnings
test_warnings:
	@echo "⚠️  Executando testes com todos os warnings visíveis..."
	$(DOCKER_COMPOSE) run --rm scraper python -m pytest tests/ -v -W error::DeprecationWarning --strict-markers

# Executa apenas testes rápidos (unit tests)
test_fast:
	@echo "🧪 Executando testes rápidos..."
	$(DOCKER_COMPOSE) run --rm scraper python -m pytest tests/ -v -m "not slow"

# Teste completo (CI simulation)
test_ci: build ci-test ci-clean
	@echo "✅ Pipeline de testes CI simulado com sucesso!"

# =========================================================================
# Coleta de Dados
# =========================================================================
# Crawling (coleta de URLs)
crawl: check-browsers
	$(SCRAPER_RUN) crawl.py $(if $(SPIDER),$(SPIDER),)

crawl-metropoles: check-browsers
	$(SCRAPER_RUN) crawl.py metropolesspider

crawl-rbs: check-browsers
	$(SCRAPER_RUN) crawl.py rbsspider

# Scraping (coleta de anúncios)
scrape: check-browsers
	$(SCRAPER_RUN) scrape.py

scrape-no-ai: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py $(if $(PLATFORM),--platform $(PLATFORM),) $(if $(TIMEOUT),--timeout $(TIMEOUT),)

scrape-rbs: check-browsers
	$(SCRAPER_RUN) scrape_no_openai.py --platform clicrbs.com.br

# =========================================================================
# Workflows Completos
# =========================================================================
collect-metropoles: crawl-metropoles scrape-no-ai
	@echo "✅ Coleta Metrópoles concluída!"

collect-rbs: crawl-rbs scrape-rbs
	@echo "✅ Coleta RBS concluída!"

# Pipeline completo de desenvolvimento
dev-pipeline: lint test_fast scrape-no-ai
	@echo "✅ Pipeline de desenvolvimento concluído!"

# Pipeline completo de produção
prod-pipeline: lint security test build push
	@echo "✅ Pipeline de produção concluído!"

# =========================================================================
# Monitoramento e Debug
# =========================================================================
stats:
	@echo "📊 Estatísticas dos containers..."
	docker stats --no-stream

ps:
	@echo "📋 Status dos serviços..."
	$(DOCKER_COMPOSE) ps

top:
	@echo "📈 Processos em execução..."
	$(DOCKER_COMPOSE) top

# =========================================================================
# Help e Documentação
# =========================================================================
help:
	@echo "📋 Check-up - Ferramenta de análise de anúncios de saúde"
	@echo ""
	@echo "🚀 Setup e Configuração:"
	@echo "  make setup              - Configura ambiente completo"
	@echo "  make setup-fast         - Setup rápido (reutiliza browsers)"
	@echo "  make env                - Cria arquivo .env"
	@echo "  make data-dirs          - Cria diretórios necessários"
	@echo ""
	@echo "🐳 Docker e Containers:"
	@echo "  make build              - Constrói imagem Docker"
	@echo "  make build-cache        - Constrói com cache otimizado"
	@echo "  make start              - Inicia serviços"
	@echo "  make stop               - Para serviços"
	@echo "  make restart            - Reinicia serviços"
	@echo "  make clean              - Limpa ambiente completo"
	@echo "  make clean-all          - Limpeza profunda (inclui imagens)"
	@echo ""
	@echo "🎭 Playwright:"
	@echo "  make install-browsers   - Instala browsers do Playwright"
	@echo "  make check-browsers     - Verifica se browsers estão instalados"
	@echo ""
	@echo "🗃️  Banco de Dados:"
	@echo "  make init_db            - Inicializa tabelas"
	@echo "  make migrate_db         - Executa migrações"
	@echo "  make db-shell           - Acessa shell do PostgreSQL"
	@echo ""
	@echo "🔍 Qualidade de Código:"
	@echo "  make lint               - Análise de código com flake8"
	@echo "  make format             - Formata código (black + isort)"
	@echo "  make security           - Análise de segurança"
	@echo ""
	@echo "🧪 Testes:"
	@echo "  make test               - Executa todos os testes"
	@echo "  make test_rbs           - Testa melhorias do RBS"
	@echo "  make test_base          - Testa otimizações do BasePlay"
	@echo "  make test_integration   - Testa integração completa"
	@echo "  make test_coverage      - Testa com relatório de cobertura"
	@echo "  make test_fast          - Testa apenas tests rápidos"
	@echo "  make test_ci            - Simula pipeline CI completo"
	@echo ""
	@echo "🔄 CI/CD:"
	@echo "  make ci-setup           - Configura ambiente CI"
	@echo "  make ci-test            - Executa testes no CI"
	@echo "  make ci-clean           - Limpa ambiente CI"
	@echo "  make push               - Envia imagem para registry"
	@echo "  make pull               - Baixa imagem do registry"
	@echo ""
	@echo "🎭 Act (GitHub Actions Local):"
	@echo "  make ci-act-setup       - Configura Act com GitHub CLI"
	@echo "  make ci-act-local       - Workflow local rápido (recomendado)"
	@echo "  make ci-act-local-lint  - Apenas lint local rápido"
	@echo "  make ci-act-local-docker - Apenas Docker test local"
	@echo "  make ci-act-lint        - Executa job de lint completo"
	@echo "  make ci-act-build       - Executa job de build completo"
	@echo "  make ci-act-test        - Executa jobs de teste completos"
	@echo "  make ci-act-all         - Executa pipeline completo"
	@echo "  make ci-act-list        - Lista jobs disponíveis"
	@echo "  make ci-act-version     - Verifica versão do act"
	@echo ""
	@echo "📊 Coleta de Dados:"
	@echo "  make crawl              - Coleta URLs (todos os portais)"
	@echo "  make crawl SPIDER=nome  - Coleta URLs (spider específico)"
	@echo "  make scrape             - Coleta anúncios (com IA)"
	@echo "  make scrape-no-ai       - Coleta anúncios (sem IA)"
	@echo ""
	@echo "📈 Monitoramento:"
	@echo "  make logs               - Visualiza logs dos serviços"
	@echo "  make stats              - Estatísticas dos containers"
	@echo "  make ps                 - Status dos serviços"
	@echo "  make top                - Processos em execução"
	@echo ""
	@echo "🔄 Pipelines Completos:"
	@echo "  make dev-pipeline       - Pipeline de desenvolvimento"
	@echo "  make prod-pipeline      - Pipeline de produção"
	@echo ""
	@echo "Para mais informações, consulte o README.md"


