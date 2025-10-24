import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class CongressoEmFocoPlay(BasePlay):
    name = "congressoemfoco"

    @classmethod
    def match(cls, url):
        return "congressoemfoco.com.br" in url

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
                entry_title = page.locator("h1").first.inner_text()
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract title: {str(e)}")

            # Extract description/subtitle
            description = ""
            try:
                description = page.locator("h2.asset__summary").first.inner_text()
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract description: {str(e)}")

            # Extract article body
            body = ""
            try:
                body_element = page.locator("div.asset__content div.html-content")
                if body_element.count() > 0:
                    body = body_element.inner_text()
                    if not body.strip():
                        logger.warning(f"[{self.name}] Extracted body is empty")
                else:
                    logger.warning(f"[{self.name}] Could not find body element")
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract body: {str(e)}")

            # Extract tags
            tags = []
            try:
                tag_elements = page.locator("div.asset__tags-links a.asset__tags-link")
                for i in range(tag_elements.count()):
                    tag_text = tag_elements.nth(i).inner_text().strip()
                    if tag_text:
                        tags.append(tag_text)
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract tags: {str(e)}")

            return EntryItem(
                title=entry_title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )

    def post_run(self, output):
        return output
