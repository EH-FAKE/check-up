import time
from playwright.sync_api import sync_playwright
from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger

class MetropolesPlay(BasePlay):
    name = "metropoles"

    @classmethod
    def match(cls, url):
        return "metropoles.com" in url

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            
            # Wait for the main content to be visible
            try:
                page.wait_for_selector("h1", timeout=30000)
            except Exception as e:
                logger.error(f"[{self.name}] Timeout waiting for h1: {str(e)}")
                # Opcional: retornar item vazio ou lançar erro
            
            # Extract article content
            entry_title = ""
            try:
                entry_title = page.locator("//h1").first.inner_text()
            except Exception:
                logger.warning(f"[{self.name}] Failed to extract title")

            # Extract description from noticiaCabecalho__subtitulo
            description = ""
            try:
                description = page.locator(".noticiaCabecalho__subtitulo").inner_text()
            except Exception:
                logger.warning(f"[{self.name}] Failed to extract description")
            
            # --- NOVO: EXTRAÇÃO DE IMAGEM (THUMBNAIL) ---
            image_url = ""
            try:
                # Tentativa 1: Meta tag og:image (Padrão Ouro)
                image_url = page.locator('meta[property="og:image"]').get_attribute("content")
                logger.info(f"[{self.name}] Image found via og:image")
            except Exception:
                pass

            if not image_url:
                try:
                    # Tentativa 2: Tag de link image_src (usada pelo Google)
                    image_url = page.locator('link[rel="image_src"]').get_attribute("href")
                    logger.info(f"[{self.name}] Image found via link rel")
                except Exception:
                    pass
            
            if not image_url:
                try:
                    # Tentativa 3: Primeira imagem dentro do article ou figure
                    # Procura imagens grandes para evitar ícones
                    imgs = page.locator("article img")
                    count = imgs.count()
                    for i in range(count):
                        src = imgs.nth(i).get_attribute("src")
                        if src and ("jpg" in src or "png" in src or "webp" in src):
                             image_url = src
                             logger.info(f"[{self.name}] Image found via article img fallback")
                             break
                except Exception:
                    pass
            # --- FIM DA EXTRAÇÃO DE IMAGEM ---

            # Extract article body with multiple attempts
            body = ""
            try:
                # Try different possible selectors for the content
                selectors = [
                    ".m-content",
                    "article",
                    ".article-content",
                    ".content"
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
                tag_elements = page.locator(".TagsNoticiaWrapper-sc-pr4a71-0 a")
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
                image_url=image_url  
            )