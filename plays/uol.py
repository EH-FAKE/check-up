import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class UOLPlay(BasePlay):
    name = "uol"

    @classmethod
    def match(cls, url):
        return "uol.com.br" in url

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
                title_selectors = [
                    "h1.c-content-head__title",  # Notícias
                    "h1.title",                  # Geral
                    "h1"                        # Fallback
                ]
                for selector in title_selectors:
                    try:
                        title_element = page.locator(selector).first
                        entry_title = title_element.inner_text().strip()
                        if entry_title:
                            break
                    except Exception:
                        continue
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract title: {str(e)}")
            
            # Extract description/subtitle
            description = ""
            try:
                desc_selectors = [
                    ".c-content-head__subtitle",  # Notícias
                    ".content-head__subtitle",   # Alguns artigos
                    ".c-news__subtitle"         # Outros formatos
                ]
                for selector in desc_selectors:
                    try:
                        desc_element = page.locator(selector).first
                        description = desc_element.inner_text().strip()
                        if description:
                            break
                    except Exception:
                        continue
            except Exception:
                logger.warning(f"[{self.name}] Failed to extract description")
            
            # Extract article body
            body = ""
            try:
                body_selectors = [
                    ".c-news__body",          # Notícias principais
                    "article",                # Artigos gerais
                    ".content-text__container" # Outros formatos
                ]
                
                for selector in body_selectors:
                    try:
                        body_element = page.locator(selector).first
                        body = body_element.inner_text().strip()
                        if body:
                            break
                    except Exception:
                        continue
                
                if not body.strip():
                    logger.warning(f"[{self.name}] Failed to extract article body with any selector")
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract article body: {str(e)}")
            
            # Extract tags
            tags = []
            try:
                tag_selectors = [
                    ".c-news-tags a",      # Notícias
                    ".tags-article a",    # Artigos
                    ".tags a"             # Geral
                ]
                
                for selector in tag_selectors:
                    try:
                        tag_elements = page.locator(selector)
                        for i in range(tag_elements.count()):
                            tag_text = tag_elements.nth(i).inner_text().strip()
                            if tag_text and tag_text not in tags:
                                tags.append(tag_text)
                        if tags:
                            break
                    except Exception:
                        continue
            except Exception:
                logger.warning(f"[{self.name}] Failed to extract tags")

            return EntryItem(
                title=entry_title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )
