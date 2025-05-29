import os
import argparse
import sched
import time
import traceback
import json
from datetime import datetime

from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from minio import Minio
from plays.base import BasePlay
from plog import logger
from models import (
    Advertisement,
    Entry,
    Portal,
    URLQueue,
    create_instance,
)

# ── Parse target platform (domain) via CLI or env ──────────────────────────
parser = argparse.ArgumentParser(
    description="Run scraper against a specific news portal"
)
parser.add_argument(
    "--platform", "-p",
    help="Domain (or slug) of the portal to scrape, e.g. metropoles.com",
    default=None
)
parser.add_argument(
    "--timeout", "-t",
    type=int,
    help="Timeout in seconds for scraper operations (default: from .env or 600)",
    default=None
)
args = parser.parse_args()

# Environment fallback
ENV_PORTAL = config("SCRAPER_PLATFORM", default="metropoles.com")
ENV_TIMEOUT = config("SCRAPER_TIMEOUT", default=600, cast=int)

# CLI flags take precedence
TARGET_DOMAIN = args.platform or ENV_PORTAL
SCRAPER_TIMEOUT = args.timeout or ENV_TIMEOUT

# Prepare folder name for MinIO (replace dots with underscores)
PORTAL_FOLDER = TARGET_DOMAIN.replace('.', '_')
# ────────────────────────────────────────────────────────────────────────

scheduler = sched.scheduler(time.time, time.sleep)

duration = 1  # seconds between runs


def get_minio_client():
    endpoint = config("MINIO_ENDPOINT")
    access_key = config("MINIO_ACCESS_KEY")
    secret_key = config("MINIO_SECRET_KEY")
    secure = config("MINIO_SECURE", cast=bool)
    
    logger.info(f"Initializing MinIO client with endpoint: {endpoint}")
    logger.info(f"MinIO secure mode: {secure}")
    
    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=secure
    )
    
    try:
        client.list_buckets()
        logger.info("Successfully connected to MinIO server")
    except Exception as e:
        logger.error(f"Failed to connect to MinIO server: {e}")
        raise
    
    return client


def save_to_minio(client, data, bucket_name, object_name):
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        from io import BytesIO
        data_stream = BytesIO(json_data)
        client.put_object(
            bucket_name,
            object_name,
            data=data_stream,
            length=len(json_data),
            content_type='application/json'
        )
        logger.info(f"Saved to MinIO: {bucket_name}/{object_name}")
    except Exception as e:
        logger.error(f"Error saving to MinIO: {e}")
        raise


def event_loop():
    main()
    scheduler.enter(duration, 1, event_loop)


def run():
    event_loop()
    scheduler.run()


def main():
    logger.info(f"Starting scraper with timeout: {SCRAPER_TIMEOUT} seconds")
    
    # Setup clients
    minio_client = get_minio_client()
    bucket_name = config("MINIO_BUCKET", default="scraped-articles")
    
    # Setup database connection
    db_url = config("DATABASE_URL")
    if "postgressql" in db_url:
        db_url = db_url.replace("postgressql", "postgresql")
    if "localhost" in db_url:
        db_url = db_url.replace("localhost", "healthcheck_db")
    engine = create_engine(db_url)
    session = Session(engine)

    # Pull URLs matching target domain
    queue_urls = URLQueue.created(session) \
        .filter(URLQueue.url.like(f"%{TARGET_DOMAIN}%")) \
        .all()
    
    if not queue_urls:
        logger.info(f"No pending URLs for '{TARGET_DOMAIN}' in queue")
        session.close()
        return

    logger.info(f"Found {len(queue_urls)} URLs for '{TARGET_DOMAIN}' to process")

    for url_obj in queue_urls:
        logger.info(f"Processing URL '{url_obj.url}' from queue...")
        url_obj.set_as_started(session)

        try:
            scraper = BasePlay.get_scraper(
                url_obj.url, 
                headless=config("HEADLESS", cast=bool),
                timeout_seconds=SCRAPER_TIMEOUT
            )
            entry_item = scraper.execute()
        except Exception as exc:
            logger.error(f"Error scraping '{url_obj.url}': {exc!r}")
            url_obj.set_as_error(session, info=str(traceback.format_exc()))
            continue

        if entry_item is None:
            continue

        portal = session.query(Portal).filter_by(slug=scraper.name).one()
        logger.info(f"Saving entry '{entry_item.title}'")
        
        entry_params = {
            "portal": portal,
            "url": entry_item.url,
            "title": entry_item.title,
            "body": getattr(entry_item, "body", None),
            "tags": getattr(entry_item, "tags", None),
        }
        if hasattr(entry_item, "description"):
            entry_params["description"] = entry_item.description

        entry = create_instance(session, Entry, **entry_params)

        article_data = {
            "portal": scraper.name,
            "url": entry_item.url,
            "title": entry_item.title,
            "body": getattr(entry_item, "body", None),
            "tags": getattr(entry_item, "tags", None),
            "description": getattr(entry_item, "description", None),
            "scraped_at": datetime.utcnow().isoformat(),
            "entry_id": entry.id,
            "ads": [
                {   "title": ad.title,
                    "url": ad.url,
                    "thumbnail": ad.thumbnail_url,
                    "tag": ad.tag,
                    "excerpt": ad.excerpt
                }
                for ad in entry_item.ads if ad.is_valid()
            ]
        }

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        object_name = f"{PORTAL_FOLDER}/{timestamp}_{entry.id}.json"

        try:
            save_to_minio(minio_client, article_data, bucket_name, object_name)
            
            ads = []
            for i, ad_item in enumerate(entry_item.ads, start=1):
                if not ad_item.is_valid():
                    continue
                logger.info(f"Saving AD ({i}/{len(entry_item.ads)}): '{ad_item.title}'")
                ads.append(
                    Advertisement(
                        entry=entry,
                        title=ad_item.title,
                        url=ad_item.url,
                        thumbnail=ad_item.thumbnail_url,
                        tag=ad_item.tag,
                        excerpt=ad_item.excerpt,
                    )
                )
            session.add_all(ads)
            session.commit()

            url_obj.set_as_finished(session)
            session.commit()
            logger.info(f"Finished scraping entry {entry.id}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            url_obj.set_as_error(session, info=str(e))
            session.commit()
            continue

    session.close()
    logger.info(f"Completed processing all '{TARGET_DOMAIN}' URLs")


if __name__ == "__main__":
    main()
