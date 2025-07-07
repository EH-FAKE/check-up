import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class VejaPlay(BasePlay):
    name = "veja"

    @classmethod
    def match(cls, url):
        return "veja.abril.com.br" in url

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(
                p,
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            )
            page = browser.new_page()
            
            # Configurar headers adicionais
            page.set_extra_http_headers({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            })
            
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            
            try:
                # Tentar carregar a página com timeout maior
                response = page.goto(self.url, timeout=180_000, wait_until="networkidle")
                if not response:
                    logger.error(f"[{self.name}] Failed to load page: no response")
                    return EntryItem(url=self.url)
                
                if response.status >= 400:
                    logger.error(f"[{self.name}] Failed to load page: status {response.status}")
                    return EntryItem(url=self.url)
                
                # Esperar pelo conteúdo principal com timeout maior
                selectors = [
                    "h1.title",                  # Título principal
                    "h1.article-title",         # Título alternativo
                    "h1"                        # Fallback
                ]
                
                title_selector = None
                for selector in selectors:
                    if page.locator(selector).count() > 0:
                        title_selector = selector
                        break
                
                if not title_selector:
                    logger.error(f"[{self.name}] No title element found")
                    return EntryItem(url=self.url)
                
                # Extrair título
                entry_title = ""
                try:
                    entry_title = page.locator(title_selector).first.inner_text().strip()
                except Exception as e:
                    logger.warning(f"[{self.name}] Failed to extract title: {str(e)}")
                
                # Extrair corpo do texto
                body = ""
                try:
                    body_selectors = [
                        ".article-content",       # Principal
                        ".content-article",      # Alternativo
                        "article"                # Fallback
                    ]
                    
                    for selector in body_selectors:
                        body_element = page.locator(selector)
                        if body_element.count() > 0:
                            body = body_element.first.inner_text().strip()
                            if body:
                                break
                    
                    if not body:
                        logger.warning(f"[{self.name}] Extracted body is empty")
                except Exception as e:
                    logger.warning(f"[{self.name}] Failed to extract article body: {str(e)}")
                
                # Extrair tags
                tags = []
                try:
                    tag_selectors = [
                        ".article-tags a",      # Principal
                        ".tags a",             # Alternativo
                        ".post-tags a"          # Fallback
                    ]
                    
                    for selector in tag_selectors:
                        tag_elements = page.locator(selector)
                        if tag_elements.count() > 0:
                            for i in range(tag_elements.count()):
                                tag_text = tag_elements.nth(i).inner_text().strip()
                                if tag_text and tag_text not in tags:
                                    tags.append(tag_text)
                            if tags:
                                break
                except Exception as e:
                    logger.warning(f"[{self.name}] Failed to extract tags: {e}")
                
                return EntryItem(
                    title=entry_title,
                    url=self.url,
                    description="",  # No description needed
                    body=body,
                    tags=tags,
                )
                
            except Exception as e:
                logger.error(f"[{self.name}] Failed to process page: {str(e)}")
                return EntryItem(url=self.url)
