import sys

from scrapy.crawler import CrawlerProcess

from plog import logger
from spiders.base import BaseSpider
from spiders.polemicaparaiba import PolemicaParaibaSpider

process = CrawlerProcess(
    settings={
        # Disable pipelines to avoid SQLAlchemy import hanging
        "ITEM_PIPELINES": {},
        # Add browser-like headers
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        },
        # Add reasonable delays between requests
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        # Respect robots.txt but with fallback
        "ROBOTSTXT_OBEY": False,
        # Retry on common errors
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 400, 403, 404, 408],
        # Fix for import hanging - force AsyncIO reactor early
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }
)


def run(spider_name=None):
    if spider_name:
        # Find the spider class with matching name
        spider_class = next(
            (cls for cls in BaseSpider.__subclasses__() if cls.name == spider_name),
            None
        )
        if spider_class:
            process.crawl(spider_class)
        else:
            logger.error(f"Spider '{spider_name}' not found")
            return
    else:
        # Run all spiders if no specific spider is specified
        for crawler_class in BaseSpider.__subclasses__():
            process.crawl(crawler_class)

    process.start()


if __name__ == "__main__":
    logger.info("Starting crawlers...")
    # Get spider name from command line argument if provided
    spider_name = sys.argv[1] if len(sys.argv) > 1 else None
    if spider_name:
        logger.info(f"Running spider: {spider_name}")
    run(spider_name)
    logger.info("Done!")
