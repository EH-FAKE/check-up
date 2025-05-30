import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class ImirantePlay(BasePlay):
    name = "imirante"

    @classmethod
    def match(cls, url):
        return "imirante.com" in url

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
            entry_title = page.locator("h1").first.inner_text()
            
            # Extract description
            description = ""
            try:
                description = page.locator(".subtitle").inner_text()
            except Exception:
                logger.warning(f"[{self.name}] Failed to extract description")
            
            # Extract article body
            body = ""
            try:
                # Try different possible selectors for the content
                selectors = [
                    "article.artigo",  # Artigo principal
                    ".artigo .content",  # Conteúdo dentro do artigo
                    ".artigo .article-content",  # Conteúdo alternativo
                    ".artigo .materia",  # Conteúdo da matéria
                    ".artigo p",  # Parágrafos do artigo
                ]
                
                for selector in selectors:
                    try:
                        logger.info(f"[{self.name}] Trying to extract body with selector: {selector}")
                        content_element = page.locator(selector)
                        if content_element.count() > 0:
                            # Para seletores que podem retornar múltiplos elementos
                            if selector == ".artigo p":
                                paragraphs = []
                                for i in range(content_element.count()):
                                    paragraph = content_element.nth(i).inner_text().strip()
                                    if paragraph:
                                        paragraphs.append(paragraph)
                                body = "\n\n".join(paragraphs)
                            else:
                                body = content_element.first.inner_text()
                            
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
            
            # Extract tags
            tags = []
            try:
                tag_elements = page.locator(".tags a")
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