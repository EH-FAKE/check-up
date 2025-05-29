.PHONY: start scrape scrape_no_openai crawl crawl_metropoles init_db migrate_db setup bash env stop wait-for-db prune

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
	
# Crawler para todos os portais ou específicos
crawl:
	docker compose run --rm scraper python crawl.py

crawl_metropoles:
	docker compose run --rm scraper python crawl.py metropolesspider

# Operações de banco de dados
init_db:
	docker compose run --rm scraper python create_db.py

migrate_db:
	docker compose run --rm scraper python migrate_db.py

# Workflow completo de coleta (após setup)
collect: crawl_metropoles scrape_no_openai
	@echo "Coleta de dados do Metrópoles concluída!"

# Exibir ajuda
help:
	@echo "Check-up - Ferramenta de análise de anúncios de saúde"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make setup           - Configura o ambiente completo (env + start + init_db + migrate_db)"
	@echo "  make env             - Cria o arquivo .env a partir do env.example se não existir"
	@echo "  make start           - Inicia os serviços Docker em background"
	@echo "  make stop            - Para os serviços Docker"
	@echo "  make prune           - Remove containers, redes e imagens não utilizadas"
	@echo "  make wait-for-db     - Aguarda o banco de dados ficar disponível"
	@echo "  make init_db         - Inicializa as tabelas do banco de dados"
	@echo "  make migrate_db      - Executa as migrações do banco de dados"
	@echo "  make crawl           - Coleta URLs de todos os portais"
	@echo "  make crawl_metropoles - Coleta URLs apenas do portal Metrópoles"
	@echo "  make scrape          - Coleta anúncios (com classificação OpenAI)"
	@echo "  make scrape_no_openai - Coleta anúncios (sem classificação OpenAI)"
	@echo "  make collect         - Executa o workflow completo para Metrópoles"
	@echo "  make bash            - Acessa o shell do container"
