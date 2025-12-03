import time
from playwright.sync_api import sync_playwright
from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger

  
  

class PolemicaParaibaPlay(BasePlay):
    name = "polemicaparaiba"

    @classmethod
    def match(cls, url):
        """Identifica se a URL é do Polêmica Paraíba"""
        return "polemicaparaiba.com.br" in url

    def pre_run(self):
        """Configurações antes da execução"""
        pass

    def run(self) -> EntryItem:
        """Extrai conteúdo da notícia"""
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()

            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)

            page.wait_for_selector("h1.entry-title", timeout=30000)

            title = self._extract_title(page)

            description = self._extract_description(page)

            body = self._extract_body(page)

            tags = self._extract_tags(page)

            return EntryItem(
                title=title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )

    def _extract_title(self, page):
        """Extrai o título da notícia"""
        selectors = [
            "h1.entry-title",
        ]

        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    title = element.first.inner_text().strip()
                    if title:
                        logger.info(f"[{self.name}] Title extracted: {title[:50]}...")
                        return title
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract title with {selector}: {str(e)}")
                continue

        logger.error(f"[{self.name}] Failed to extract title")
        return ""

    def _extract_description(self, page):
        """Extrai a descrição/subtítulo da notícia"""
        selectors = [
            "h2.entry-subtitle",
        ]

        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    description = element.first.inner_text().strip()
                    if description and len(description) > 10:
                        logger.info(f"[{self.name}] Description extracted: {description[:50]}...")
                        return description
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract description with {selector}: {str(e)}")
                continue

        logger.info(f"[{self.name}] No description found")
        return ""

    def _extract_body(self, page):
        """Extrai o corpo da notícia"""
        selectors = [
            "div.entry-content",
        ]

        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    element.locator("script, style, .ad, .advertisement").evaluate_all("els => els.forEach(el => el.remove())")

                    body = element.inner_text().strip()
                    if body and len(body) > 100: 
                        logger.info(f"[{self.name}] Body extracted ({len(body)} chars)")
                        return body
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract body with {selector}: {str(e)}")
                continue

        logger.error(f"[{self.name}] Failed to extract body")
        return ""

    def _extract_tags(self, page):
        """Extrai as tags da notícia"""
        selectors = [
            "section.tags a",
        ]

        tags = []

        for selector in selectors:
            try:
                elements = page.locator(selector)
                if elements.count() > 0:
                    for i in range(elements.count()):
                        tag_text = elements.nth(i).inner_text().strip()
                        if tag_text and tag_text not in tags:
                            tags.append(tag_text)

                    if tags:
                        logger.info(f"[{self.name}] Tags extracted: {tags}")
                        break
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract tags with {selector}: {str(e)}")
                continue

        return tags