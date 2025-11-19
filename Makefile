.PHONY: start scrape scrape_no_openai crawl crawl_metropoles init_db migrate_db setup bash env stop wait-for-db prune test_playwright

# Configuração do ambiente
env:
	@if [ ! -f .env ]; then \
		echo "Criando arquivo .env a partir do env.example..."; \
		cp env.example .env; \
		echo "Arquivo .env criado. Por favor, verifique e configure as variáveis de ambiente conforme necessário."; \
	else \
		echo "Arquivo .env já existe."; \
	fi

# Configuração completa do projeto
setup: env start wait-for-db init_db migrate_db
	@echo "Ambiente configurado com sucesso!"

# Acesso ao shell do container
bash:
	docker compose exec -it scraper bash

# Iniciar os serviços
start: env
	docker compose -f compose.yml up -d --remove-orphans
	@echo "Serviços iniciados em background. Use 'docker compose logs -f' para ver os logs."

# Parar os serviços
stop:
	docker compose down --remove-orphans
	@echo "Serviços parados."

# Limpar recursos não utilizados
prune:
	docker system prune -f
	@echo "Containers, redes e imagens não utilizadas foram removidos."

# Esperar pelo banco de dados
wait-for-db:
	@echo "Aguardando o banco de dados ficar pronto..."
	@timeout=60; \
	elapsed=0; \
	echo "Aguardando PostgreSQL inicializar..."; \
	until docker compose exec db pg_isready -U postgres -h localhost || [ $$elapsed -eq $$timeout ]; do \
		sleep 1; \
		elapsed=$$((elapsed+1)); \
		echo -n "."; \
	done; \
	if [ $$elapsed -eq $$timeout ]; then \
		echo "\nTimeout ao aguardar pelo PostgreSQL!"; \
		exit 1; \
	else \
		echo "\nPostgreSQL está pronto!"; \
	fi

# Scraping com e sem OpenAI
scrape:
	docker compose run --rm scraper python scrape.py

scrape_no_openai:
	docker compose run --rm scraper python scrape_no_openai.py

# Scraping por plataforma específica (sem OpenAI)
scrape_metropoles:
	docker compose exec scraper python scrape_no_openai.py --platform metropoles.com

# Comando para verificação de instalação do Playwright
test_playwright:
	@echo "Verificando instalação do Playwright..."
	docker compose run --rm scraper python -c "from playwright.sync_api import sync_playwright; print('Iniciando teste do Playwright'); p = sync_playwright().start(); print('Playwright iniciado com sucesso'); browser = p.firefox.launch(); print('Navegador lançado com sucesso'); page = browser.new_page(); print('Nova página criada'); page.goto('https://www.example.com'); print('Página carregada'); browser.close(); p.stop(); print('Teste do Playwright concluído com sucesso')"

scrape_maisgoias:
	docker compose exec scraper python scrape_no_openai.py --platform maisgoias.com.br

scrape_aliadosbrasil:
	docker compose exec scraper python scrape_no_openai.py --platform aliadosbrasiloficial.com.br

scrape_ig:
	docker compose exec scraper python scrape_no_openai.py --platform ig.com.br

scrape_veja:
	docker compose exec scraper python scrape_no_openai.py --platform veja.abril.com.br

scrape_r7:
	docker compose exec scraper python scrape_no_openai.py --platform r7.com

scrape_uol:
	docker compose exec scraper python scrape_no_openai.py --platform uol.com.br

scrape_folha:
	docker compose exec scraper python scrape_no_openai.py --platform folha.uol.com.br

scrape_jornaldaparaiba:
	docker compose exec scraper python scrape_no_openai.py --platform jornaldaparaiba.com.br

scrape_cidadeverde:
	docker compose exec scraper python scrape_no_openai.py --platform cidadeverde.com

	
# Crawler para todos os portais ou específicos
crawl:
	docker compose run --rm scraper python crawl.py

crawl_metropoles:
	docker compose run --rm scraper python crawl.py metropolesspider

# Operações de banco de dados
crawl_veja:
	docker compose run scraper python crawl.py vejaspider

crawl_r7:
	docker compose run scraper python crawl.py r7spider

crawl_uol:
	docker compose run scraper python crawl.py uolspider
  
crawl_maisgoias:
	docker compose run scraper python crawl.py maisgoiasspider

crawl_aliadosBrasil:
	docker compose run scraper python crawl.py aliadosbrasilspider

crawl_ig:
	docker compose run scraper python crawl.py igspider

crawl_folha:
	docker compose run scraper python crawl.py folhaspider

crawl_jornaldaparaiba:
	docker compose run scraper python crawl.py jornaldaparaiba

crawl_cidadeverde:
	docker compose run scraper python crawl.py cidadeverdespider

# Workflow completo de coleta de URLs
crawl_all_working:
	@echo "Executando crawl de todos os portais funcionais..."
	@make crawl_metropoles
	@make crawl_veja
	@make crawl_r7
	@make crawl_uol
	@make crawl_maisgoias
	@make crawl_aliadosBrasil
	@make crawl_ig
	@make crawl_folha
	@make crawl_jornaldaparaiba
	@make crawl_cidadeverde
	@echo "Crawl de todos os portais concluído!"

# Workflow completo de scraping
scrape_all_working:
	@echo "Executando scraping de todos os portais funcionais..."
	@make scrape_metropoles
	@make scrape_maisgoias
	@make scrape_aliadosbrasil
	@make scrape_ig
	@make scrape_veja
	@make scrape_r7
	@make scrape_uol
	@make scrape_folha
	@make scrape_jornaldaparaiba
	@make scrape_cidadeverde
	@echo "Scraping de todos os portais concluído!"

# Pipeline completo: crawl + scrape
pipeline_complete:
	@echo "Executando pipeline completo (crawl + scrape)..."
	@make crawl_all_working
	@echo "Aguardando 10 segundos antes do scraping..."
	@sleep 10
	@make scrape_all_working
	@echo "Pipeline completo concluído!"

init_db:
	docker compose run --rm scraper python create_db.py

migrate_db:
	docker compose run --rm scraper python migrate_db.py

# Workflow completo de coleta (após setup)
collect: crawl_metropoles scrape_no_openai
	@echo "Coleta de dados do Metrópoles concluída!"

# Workflow otimizado para coleta de dados
collect_working: crawl_all_working scrape_all_working
	@echo "Coleta completa de todos os portais funcionais concluída!"


# Exibir ajuda
help:
	@echo "Check-up - Ferramenta de análise de anúncios de saúde"
	@echo ""
	@echo "=== COMANDOS DE CONFIGURAÇÃO ==="
	@echo "  make setup           - Configura o ambiente completo (env + start + init_db + migrate_db)"
	@echo "  make env             - Cria o arquivo .env a partir do env.example se não existir"
	@echo "  make start           - Inicia os serviços Docker em background"
	@echo "  make stop            - Para os serviços Docker"
	@echo "  make bash            - Acessa o shell do container"
	@echo ""
	@echo "=== COMANDOS DE CRAWLING (Coleta de URLs) ==="
	@echo "  make crawl_all_working - Executa crawl de todos os portais funcionais"
	@echo "  make crawl_metropoles  - Coleta URLs do portal Metrópoles"
	@echo "  make crawl_veja        - Coleta URLs do portal Veja"
	@echo "  make crawl_r7          - Coleta URLs do portal R7"
	@echo "  make crawl_uol         - Coleta URLs do portal UOL"
	@echo "  make crawl_maisgoias   - Coleta URLs do portal MaisGoiás"
	@echo "  make crawl_aliadosBrasil - Coleta URLs do portal AliadosBrasil"
	@echo "  make crawl_ig          - Coleta URLs do portal IG"
	@echo "  make crawl_folha       - Coleta URLs do portal Folha"
	@echo ""
	@echo "=== COMANDOS DE SCRAPING (Extração de Anúncios) ==="
	@echo "  make scrape_all_working - Executa scraping de todos os portais funcionais"
	@echo "  make scrape_metropoles  - Scraping do portal Metrópoles"
	@echo "  make scrape_maisgoias   - Scraping do portal MaisGoiás"
	@echo "  make scrape_aliadosbrasil - Scraping do portal AliadosBrasil"
	@echo "  make scrape_ig          - Scraping do portal IG"
	@echo "  make scrape_veja        - Scraping do portal Veja"
	@echo "  make scrape_r7          - Scraping do portal R7"
	@echo "  make scrape_uol         - Scraping do portal UOL"
	@echo "  make scrape_folha       - Scraping do portal Folha"
	@echo ""
	@echo "=== WORKFLOWS COMPLETOS ==="
	@echo "  make pipeline_complete  - Executa crawl + scraping de todos os portais"
	@echo "  make collect_working    - Workflow otimizado para coleta completa"
	@echo ""
	@echo "=== OUTROS COMANDOS ==="
	@echo "  make init_db           - Inicializa as tabelas do banco de dados"
	@echo "  make migrate_db        - Executa as migrações do banco de dados"
	@echo "  make prune             - Remove containers, redes e imagens não utilizadas"
	@echo "  make test_playwright   - Testa se a instalação do Playwright está funcionando"

.PHONY: start scrape scrape_no_openai scrape_fixed scrape_working install run-backend run-frontend docker-run-backend docker-run-frontend docker-build-backend docker-build-frontend all stop down

# Instalar dependências do backend e frontend
install:
	cd web/server && pip install -r requirements.txt && cd ../client && pnpm install

# Rodar backend localmente
run-backend:
	cd web/server && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Rodar frontend localmente
run-frontend:
	cd web/client && pnpm run dev --host 0.0.0.0

# Rodar backend (server-web) com Docker
run-backend-docker:
	docker compose up server-web

# Rodar frontend (client-web) com Docker
run-frontend-docker:
	docker compose up client-web

# Construir e rodar backend (server-web) com Docker
build-backend-docker:
	docker compose up --build server-web

# Construir e rodar frontend (client-web) com Docker
build-frontend-docker:
	docker compose up --build client-web

# Rodar todos os serviços (backend, frontend, minio, db, scraper)
all:
	docker compose up -d

# Parar todos os serviços
down:
	docker compose down
