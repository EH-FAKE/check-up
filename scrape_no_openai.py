import os
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

scheduler = sched.scheduler(time.time, time.sleep)

duration = 1


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
        # Test the connection
        client.list_buckets()
        logger.info("Successfully connected to MinIO server")
    except Exception as e:
        logger.error(f"Failed to connect to MinIO server: {str(e)}")
        raise
    
    return client


def save_to_minio(client, data, bucket_name, object_name):
    try:
        # Ensure bucket exists
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        
        # Convert data to JSON
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        # Create a BytesIO object from the JSON data
        from io import BytesIO
        data_stream = BytesIO(json_data)
        
        # Upload to MinIO
        client.put_object(
            bucket_name,
            object_name,
            data=data_stream,
            length=len(json_data),
            content_type='application/json'
        )
        logger.info(f"Successfully saved data to MinIO: {bucket_name}/{object_name}")
    except Exception as e:
        logger.error(f"Error saving to MinIO: {str(e)}")
        raise


def event_loop():
    main()
    scheduler.enter(duration, 1, event_loop)


def run():
    event_loop()
    scheduler.run()


def main():
    # Setup MinIO client
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

    # Get all Metropoles URLs from queue
    metropoles_urls = URLQueue.created(session).filter(URLQueue.url.like("%metropoles.com%")).all()
    
    if not metropoles_urls:
        logger.info("No pending Metropoles URLs in queue")
        session.close()
        return

    logger.info(f"Found {len(metropoles_urls)} Metropoles URLs to process")
    
    for url_obj in metropoles_urls:
        logger.info(f"Processing Metropoles URL '{url_obj.url}' from queue...")
        url_obj.set_as_started(session)

        url = url_obj.url
        entry_item = None
        try:
            scraper = BasePlay.get_scraper(url, headless=config("HEADLESS", cast=bool))
            entry_item = scraper.execute()
        except Exception as exc:
            logger.error(f"Error scraping '{url}': {exc!r}")
            url_obj.set_as_error(session, info=str(traceback.format_exc()))
            continue

        if entry_item is None:
            continue

        portal = session.query(Portal).filter_by(slug=scraper.name).one()

        logger.info(f"Saving entry '{entry_item.title}'")
        
        # Create Entry in database for tracking
        entry_params = {
            "portal": portal,
            "url": entry_item.url,
            "title": entry_item.title,
            "body": getattr(entry_item, "body", None),
            "tags": getattr(entry_item, "tags", None),
        }
        
        if hasattr(entry_item, "description"):
            entry_params["description"] = entry_item.description
        
        entry = create_instance(
            session,
            Entry,
            **entry_params
        )
        
        # Prepare data for MinIO storage
        article_data = {
            "portal": scraper.name,
            "url": entry_item.url,
            "title": entry_item.title,
            "body": getattr(entry_item, "body", None),
            "tags": getattr(entry_item, "tags", None),
            "description": getattr(entry_item, "description", None),
            "scraped_at": datetime.utcnow().isoformat(),
            "entry_id": entry.id,  # Link to database entry
            "ads": [
                {
                    "title": ad.title,
                    "url": ad.url,
                    "thumbnail": ad.thumbnail_url,
                    "tag": ad.tag,
                    "excerpt": ad.excerpt
                }
                for ad in entry_item.ads
                if ad.is_valid()
            ]
        }
        
        # Generate object name using timestamp and entry ID
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        object_name = f"metropoles/{timestamp}_{entry.id}.json"
        
        try:
            # Save to MinIO
            save_to_minio(minio_client, article_data, bucket_name, object_name)
            
            # Save ads to database
            ads = []
            n_ads = len(entry_item.ads)
            for i, ad_item in enumerate(entry_item.ads, start=1):
                if not ad_item.is_valid():
                    logger.warning(f"[{portal.slug}] Ad {ad_item} is not valid")
                    continue

                logger.info(f"[{portal.slug}] Saving AD ({i}/{n_ads}): '{ad_item.title}'")
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

            logger.info(f"[{portal.slug}] Saving {len(ads)} ads to database")
            session.add_all(ads)
            session.commit()
            logger.info(f"[{portal.slug}] Done scraping entry {entry.id}")

            url_obj.set_as_finished(session)
            session.commit()
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            url_obj.set_as_error(session, info=str(e))
            session.commit()
            continue

    session.close()
    logger.info("Finished processing all Metropoles URLs")


if __name__ == "__main__":
    main() 