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
            page.wait_for_selector("h1", timeout=30000)
            title = self._extract_title(page)
            description = self._extract_description(page)
            body = self._extract_body(page)
            tags = self._extract_tags(page)

            logger.info(f"[{self.name}] Extração concluída:")
            logger.info(f"  - Título: {'✓' if title else '✗'}")
            logger.info(f"  - Descrição: {'✓' if description else '✗'}")
            logger.info(f"  - Corpo: {'✓' if body else '✗'} ({len(body) if body else 0} chars)")
            logger.info(f"  - Tags: {'✓' if tags else '✗'} ({len(tags) if tags else 0} tags)")

            return EntryItem(
                title=title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )

    def _extract_title(self, page):
        title_selectors = [
            "h1",
            ".article-title h1",
            ".news-title h1",
            ".post-title h1",
            "header h1"
        ]
        
        for selector in title_selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    title = element.first.inner_text().strip()
                    if title:
                        logger.info(f"[{self.name}] Título extraído com seletor: {selector}")
                        return title
            except Exception as e:
                logger.warning(f"[{self.name}] Erro ao extrair título com {selector}: {str(e)}")
                continue
        
        try:
            title = page.title().strip()
            if " - Imirante" in title:
                title = title.replace(" - Imirante", "").strip()
            if title:
                logger.info(f"[{self.name}] Título extraído do <title>")
                return title
        except Exception as e:
            logger.warning(f"[{self.name}] Erro ao extrair título do <title>: {str(e)}")
        
        logger.error(f"[{self.name}] Falha ao extrair título")
        return ""

    def _extract_description(self, page):
        description_selectors = [
            "h2",
            ".article-subtitle",
            ".news-subtitle", 
            ".post-subtitle",
            ".lead",
            ".summary",
            ".excerpt",
            "header h2",
            "meta[name='description']"
        ]
        
        for selector in description_selectors:
            try:
                if selector == "meta[name='description']":
                    element = page.locator(selector)
                    if element.count() > 0:
                        description = element.get_attribute("content")
                        if description and description.strip() and len(description.strip()) > 10:
                            logger.info(f"[{self.name}] Descrição extraída de meta description")
                            return description.strip()
                else:
                    element = page.locator(selector)
                    if element.count() > 0:
                        description = element.first.inner_text().strip()
                        if description and len(description) > 10:
                            logger.info(f"[{self.name}] Descrição extraída com seletor: {selector}")
                            return description
            except Exception as e:
                logger.warning(f"[{self.name}] Erro ao extrair descrição com {selector}: {str(e)}")
                continue
        
        logger.info(f"[{self.name}] Nenhuma descrição encontrada")
        return ""

    def _extract_body(self, page):
        body_selectors = [
            "article",
            ".article-content",
            ".article-body", 
            ".post-content",
            ".news-content",
            ".content",
            ".text",
            ".story-body",
            "main"
        ]
        
        for selector in body_selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    page.evaluate("""
                        (selector) => {
                            const container = document.querySelector(selector);
                            if (container) {
                                // Remover elementos indesejados
                                const unwanted = container.querySelectorAll(
                                    'script, style, .ad, .advertisement, .ads, ' +
                                    '.social-share, .share, .comments, .related, ' +
                                    '.newsletter, .subscription, .promo, .banner'
                                );
                                unwanted.forEach(el => el.remove());
                            }
                        }
                    """, selector)
                    
                    body = element.first.inner_text().strip()
                    if body and len(body) > 100:
                        logger.info(f"[{self.name}] Corpo extraído com seletor: {selector} ({len(body)} chars)")
                        return body
            except Exception as e:
                logger.warning(f"[{self.name}] Erro ao extrair corpo com {selector}: {str(e)}")
                continue
        
        logger.error(f"[{self.name}] Falha ao extrair corpo da notícia")
        return ""

    def _extract_tags(self, page):
        tag_selectors = [
            ".tags a",
            ".categories a",
            ".post-tags a",
            ".article-tags a", 
            ".keywords a",
            "[rel='tag']",
            ".tag-list a",
            ".breadcrumb a"
        ]
        
        tags = []
        
        for selector in tag_selectors:
            try:
                elements = page.locator(selector)
                if elements.count() > 0:
                    for i in range(min(elements.count(), 10)):
                        try:
                            tag_text = elements.nth(i).inner_text().strip()
                            if tag_text and tag_text not in tags:
                                generic_tags = {"home", "início", "principal", "notícias", "imirante"}
                                if tag_text.lower() not in generic_tags and len(tag_text) > 2:
                                    tags.append(tag_text)
                        except Exception:
                            continue
                    
                    if tags:
                        logger.info(f"[{self.name}] Tags extraídas com seletor {selector}: {tags}")
                        break
            except Exception as e:
                logger.warning(f"[{self.name}] Erro ao extrair tags com {selector}: {str(e)}")
                continue
        
        if not tags:
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(self.url)
                path_parts = [part for part in parsed_url.path.split('/') if part]
                if len(path_parts) >= 2:
                    category = path_parts[1]
                    if category and category not in ["noticias"]:
                        tags.append(category.replace("-", " ").title())
                        logger.info(f"[{self.name}] Tag extraída da URL: {tags}")
            except Exception as e:
                logger.warning(f"[{self.name}] Erro ao extrair tag da URL: {str(e)}")
        
        return tags
