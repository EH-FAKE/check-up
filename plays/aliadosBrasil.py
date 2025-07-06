import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class AliadosBrasilPlay(BasePlay):
    name = "aliadosbrasil"

    @classmethod
    def match(cls, url):
        return "aliadosbrasiloficial.com.br" in url

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            
            # Wait for the main content to be visible
            page.wait_for_selector("h2", timeout=30000)
            
            # Extract article content
            entry_title = page.locator("//h2").first.inner_text()
            
            # Extract description from noticiaCabecalho__subtitulo
            description = ""
            try:
                description = page.locator("h3").first.inner_text()
            except Exception:
                logger.warning(f"[{self.name}] Failed to extract description")
            
            # Extract article body with multiple attempts
            body = ""
            try:
                # Try different possible selectors for the content
                selectors = [
                    ".post_content"
                ]
                
                for selector in selectors:
                    try:
                        logger.info(f"[{self.name}] Trying to extract body with selector: {selector}")
                        content_element = page.locator(selector)
                        if content_element.count() > 0:
                            body = content_element.inner_text()
                            if body.strip():
                                logger.info(f"[{self.name}] Successfully extracted body using selector: {selector}")
                                break
                    except Exception as e:
                        logger.debug(f"[{self.name}] Failed with selector {selector}: {str(e)}")
                        continue
                
                if not body.strip():
                    logger.warning(f"[{self.name}] Failed to extract article body with any selector")
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract article body: {str(e)}")
            
            # Extract tags from the new structure
            tags = []
            try:
                tag_elements = page.locator(".tags .post_tag a")
                for i in range(tag_elements.count()):
                    tag_text = tag_elements.nth(i).inner_text().strip()
                    if tag_text:
                        tags.append(tag_text)
            except Exception:
                logger.warning(f"[{self.name}] Failed to extract tags")

            return EntryItem(
                title=entry_title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )