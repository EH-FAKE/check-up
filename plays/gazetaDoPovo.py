import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class GazetaDoPovoPlay(BasePlay):
    name = "gazetadopovo"

    @classmethod
    def match(cls, url):
        return "gazetadopovo.com.br" in url

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            
            # Wait for the main content to be visible
            page.wait_for_selector("h1", timeout=30000)
            
            # Extract article title
            entry_title = ""
            try:
                entry_title = page.locator("div.postLayout_post-title__hT_aC h1").first.inner_text()
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract title: {str(e)}")
            
            # Extract article body
            body = ""
            try:
                body_element = page.locator("div.postBody_post-body-container__1KhtH")
                if body_element.count() > 0:
                    body = body_element.inner_text()
                    if not body.strip():
                        logger.warning(f"[{self.name}] Extracted body is empty")
                else:
                    logger.warning(f"[{self.name}] Could not find body element")
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract article body: {str(e)}")
            
            # Extract tags
            tags = []
            try:
                page.wait_for_function(
                    "window.GPSystemContent && Array.isArray(JSON.parse(window.GPSystemContent).tags)",
                    timeout=30_000
                )
                raw = page.evaluate("JSON.parse(window.GPSystemContent).tags")
                tags = [slug.replace("-", " ").title() for slug in raw]
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract tags from JSON: {e}")



            return EntryItem(
                title=entry_title,
                url=self.url,
                description="",  # No description available
                body=body,
                tags=tags,
            )
