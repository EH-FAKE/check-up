import shutil
import time
from tempfile import NamedTemporaryFile
from typing import List

from playwright.sync_api import TimeoutError as PlayWrightTimeoutError, sync_playwright

from plays.items import EntryItem
from plays.timeout import PlayerTimeoutError
from plays.exceptions import ScraperNotFoundError
from plog import logger


class BasePlay:
    name = "base"

    def __init__(
        self,
        url,
        session_dir=None,
        proxy=None,
        wait_time=3,
        headless=True,
        retries=3,
        allow_remove_session=True,
        timeout_seconds=600,
    ):
        self.url = url
        self.session_dir = session_dir
        self.proxy = proxy
        self.wait_time = wait_time
        self.headless = headless
        self.retries = retries
        self.allow_remove_session = allow_remove_session
        self.timeout_seconds = timeout_seconds

    @classmethod
    def match(cls, url):
        raise NotImplementedError()

    @classmethod
    def extra_kwargs(cls):
        return dict()

    @classmethod
    def get_scraper(cls, url, *args, **kwargs):
        scrapers = cls.__subclasses__()
        for scraper in scrapers:
            if scraper.match(url):
                return scraper(url, *args, **scraper.extra_kwargs())

        raise ScraperNotFoundError(f"No scraper was found for url '{url}'")

    def get_session_dir(self):
        if self.session_dir is None:
            return f"./sessions/{self.name}_session/"

        return self.session_dir

    def scroll_down(self, page, n, amount=300, wait_time=1):
        for _ in range(n):
            page.mouse.wheel(0, amount)
            time.sleep(wait_time)

    def launch_browser(self, playwright_obj, use_proxy=True, *args, **kwargs):
        logger.info(f"[{self.name}] Launching browser...'")
        if self.proxy is not None and use_proxy:
            logger.info(f"[{self.name}] Using proxy")
            return playwright_obj.firefox.launch_persistent_context(
                self.get_session_dir(),
                headless=self.headless,
                proxy=self.proxy,
                *args,
                **kwargs,
            )
        return playwright_obj.firefox.launch_persistent_context(
            self.get_session_dir(),
            headless=self.headless,
            *args,
            **kwargs,
        )

    def remove_session(self):
        if self.allow_remove_session:
            try:
                logger.info(f"[{self.name}] Removing session...")
                shutil.rmtree(self.get_session_dir())
                logger.info(f"[{self.name}] Done!")
            except Exception:
                logger.error(
                    f"[{self.name}] Error deleting session dir: '{self.get_session_dir()}'"
                )
        else:
            logger.info(f"[{self.name}] Removing session not allowed...")

    def pre_run(self):
        raise NotImplementedError()

    def post_run(self, output):
        return output

    def run(self):
        raise NotImplementedError()

    def execute(self, retries=2):
        entry_item = None
        self.pre_run()
        while entry_item is None and retries >= 0:
            try:
                entry_item = self.run()
                logger.info(f"[{self.name}]: Successfully scraped content.")
            except PlayWrightTimeoutError as exc:
                logger.error(str(exc))
            except PlayerTimeoutError as exc:
                logger.error(str(exc))

            if entry_item is None:
                logger.warning(
                    f"[{self.name}] Failed to scrape content. Trying again. Remaining {retries}"
                )
                # Remove session and login again. It sometimes work
                self.remove_session()
                retries -= 1

        if entry_item is None:
            raise Exception(f"[{self.name}] Failed to scrape content from '{self.url}'")

        entry_item = self.post_run(entry_item)
        return entry_item
