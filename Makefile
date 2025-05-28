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

crawl_ig:
	docker compose exec scraper python crawl.py igspider

scrape_ig:
	docker compose exec scraper python scrape_no_openai.py --platform ig.com.br

init_db:
	docker compose run scraper python create_db.py

migrate_db:
	docker compose run scraper python migrate_db.py

.PHONY: start scrape scrape_no_openai scrape_fixed scrape_working
