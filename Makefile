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

init_db:
	docker compose run scraper python create_db.py

.PHONY: start scrape scrape_no_openai scrape_fixed scrape_working
