bash:
	docker compose exec -it scraper bash

start:
	docker compose -f compose.yml up

scrape:
	docker compose run scraper python scrape.py

scrape_no_openai:
	docker compose run scraper python scrape_no_openai.py
	
crawl:
	docker compose run scraper python crawl.py

crawl_metropoles:
	docker compose run scraper python crawl.py metropolesspider

crawl_veja:
	docker compose run scraper python crawl.py vejaspider

crawl_r7:
	docker compose run scraper python crawl.py r7spider

crawl_uol:
	docker compose run scraper python crawl.py uolspider

crawl_ig:
	docker compose run scraper python crawl.py igspider

init_db:
	docker compose run scraper python create_db.py

migrate_db:
	docker compose run scraper python migrate_db.py

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
	docker-compose up server-web

# Rodar frontend (client-web) com Docker
run-frontend-docker:
	docker-compose up client-web

# Construir e rodar backend (server-web) com Docker
build-backend-docker:
	docker-compose up --build server-web

# Construir e rodar frontend (client-web) com Docker
build-frontend-docker:
	docker-compose up --build client-web

# Rodar todos os serviços (backend, frontend, minio, db, scraper)
all:
	docker-compose up -d

# Parar todos os serviços
down:
	docker-compose down

# Parar todos os serviços (alias)
stop:
	docker-compose down
