import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class OTempoPlay(BasePlay):
    name = "otempo"

    @classmethod
    def match(cls, url):
        return "otempo.com.br" in url

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()
            logger.info(f"[{self.name}] Abrindo URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            
            # Aguarda o conteúdo principal ficar visível
            page.wait_for_selector("h1", timeout=30000)
            
            # Extrai o título do artigo
            entry_title = ""
            try:
                entry_title = page.locator("h1.article-title").first.inner_text()
            except Exception as e:
                logger.warning(f"[{self.name}] Falha ao extrair título: {str(e)}")
            
            # Extrai o corpo do artigo
            body = ""
            try:
                body_element = page.locator("div.article-content")
                if body_element.count() > 0:
                    body = body_element.inner_text()
                    if not body.strip():
                        logger.warning(f"[{self.name}] Corpo extraído está vazio")
                else:
                    logger.warning(f"[{self.name}] Não foi possível encontrar o elemento do corpo")
            except Exception as e:
                logger.warning(f"[{self.name}] Falha ao extrair corpo do artigo: {str(e)}")
            
            # Extrai tags
            tags = []
            try:
                tag_elements = page.locator("div.article-tags a")
                for i in range(tag_elements.count()):
                    tag = tag_elements.nth(i).inner_text()
                    if tag:
                        tags.append(tag)
            except Exception as e:
                logger.warning(f"[{self.name}] Falha ao extrair tags: {e}")

            # Captura screenshot da página
            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)

            return EntryItem(
                title=entry_title,
                url=self.url,
                description="",  # Sem descrição disponível
                body=body,
                tags=tags,
                screenshot_path=entry_screenshot_path,
            ) 