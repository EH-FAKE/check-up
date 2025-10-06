import time
from playwright.sync_api import sync_playwright
from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class ClicRBSPlay(BasePlay):
    name = "clicrbs"

    @classmethod
    def match(cls, url):
        return "clicrbs.com.br" in url

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            
            # Fechar possíveis banners/modals que possam aparecer
            try:
                # Tenta fechar modal de newsletter ou outros overlays
                page.locator("css=div.overlay div.root.page-1.page-last div.container button.close").click()
                logger.info(f"[{self.name}] Closed overlay modal")
            except Exception:
                logger.info(f"[{self.name}] No overlay modal found")
            
            # Aguardar carregamento do conteúdo principal
            page.wait_for_selector("h1", timeout=30000)
            
            # Extrair título da notícia
            entry_title = self._extract_title(page)
            
            # Extrair descrição/subtítulo
            description = self._extract_description(page)
            
            # Extrair corpo da notícia
            body = self._extract_body(page)
            
            # Extrair tags
            tags = self._extract_tags(page)

            return EntryItem(
                title=entry_title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )

    def _extract_title(self, page):
        """Extrai o título da notícia"""
        try:
            # Testar múltiplos seletores para título
            title_selectors = [
                "h1.title",
                "h1",
                ".article-title h1",
                ".post-title h1",
                "[data-testid='title'] h1"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = page.locator(selector).first
                    if title_element.count() > 0:
                        title = title_element.inner_text().strip()
                        if title:
                            logger.info(f"[{self.name}] Title extracted using selector: {selector}")
                            return title
                except Exception:
                    continue
                    
            logger.warning(f"[{self.name}] No title found with any selector")
            return ""
            
        except Exception as e:
            logger.error(f"[{self.name}] Failed to extract title: {str(e)}")
            return ""

    def _extract_description(self, page):
        """Extrai a descrição/subtítulo da notícia"""
        try:
            # Testar múltiplos seletores para descrição
            description_selectors = [
                ".article-subtitle",
                ".post-subtitle",
                ".article-lead",
                ".lead",
                ".summary",
                "h2.subtitle",
                "[data-testid='subtitle']",
                ".article-excerpt"
            ]
            
            for selector in description_selectors:
                try:
                    desc_element = page.locator(selector).first
                    if desc_element.count() > 0:
                        description = desc_element.inner_text().strip()
                        if description:
                            logger.info(f"[{self.name}] Description extracted using selector: {selector}")
                            return description
                except Exception:
                    continue
                    
            logger.info(f"[{self.name}] No description found")
            return ""
            
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to extract description: {str(e)}")
            return ""

    def _extract_body(self, page):
        """Extrai o corpo da notícia"""
        try:
            # Testar múltiplos seletores para o corpo do artigo
            body_selectors = [
                ".article-content",
                ".post-content",
                ".article-body",
                ".content",
                ".text-content",
                "[data-testid='content']",
                ".article-text",
                ".post-body"
            ]
            
            for selector in body_selectors:
                try:
                    body_element = page.locator(selector).first
                    if body_element.count() > 0:
                        body = body_element.inner_text().strip()
                        if body and len(body) > 100:  # Garantir que é conteúdo substancial
                            logger.info(f"[{self.name}] Body extracted using selector: {selector}")
                            return body
                except Exception:
                    continue
            
            # Se não encontrou com seletores específicos, tentar pegar todos os parágrafos
            try:
                paragraphs = page.locator("article p, .article p, .content p").all()
                if paragraphs:
                    body_parts = []
                    for p in paragraphs:
                        text = p.inner_text().strip()
                        if text and len(text) > 20:  # Filtrar parágrafos muito curtos
                            body_parts.append(text)
                    
                    if body_parts:
                        body = "\n\n".join(body_parts)
                        logger.info(f"[{self.name}] Body extracted from paragraphs")
                        return body
            except Exception:
                pass
                
            logger.warning(f"[{self.name}] No body content found")
            return ""
            
        except Exception as e:
            logger.error(f"[{self.name}] Failed to extract body: {str(e)}")
            return ""

    def _extract_tags(self, page):
        """Extrai as tags da notícia"""
        try:
            tags = []
            
            # Testar múltiplos seletores para tags
            tag_selectors = [
                ".article-tags a",
                ".post-tags a", 
                ".tags a",
                ".categories a",
                ".keywords a",
                "[data-testid='tags'] a",
                ".tag-list a"
            ]
            
            for selector in tag_selectors:
                try:
                    tag_elements = page.locator(selector).all()
                    if tag_elements:
                        for tag_element in tag_elements:
                            tag_text = tag_element.inner_text().strip()
                            if tag_text and tag_text not in tags:
                                tags.append(tag_text)
                        
                        if tags:
                            logger.info(f"[{self.name}] Tags extracted using selector: {selector}")
                            break
                except Exception:
                    continue
            
            # Tentar extrair de meta tags se não encontrou tags específicas
            if not tags:
                try:
                    keywords_meta = page.locator('meta[name="keywords"]').first
                    if keywords_meta.count() > 0:
                        keywords = keywords_meta.get_attribute("content")
                        if keywords:
                            tags = [tag.strip() for tag in keywords.split(',') if tag.strip()]
                            logger.info(f"[{self.name}] Tags extracted from meta keywords")
                except Exception:
                    pass
            
            if not tags:
                logger.info(f"[{self.name}] No tags found")
            else:
                logger.info(f"[{self.name}] Found {len(tags)} tags: {tags}")
                
            return tags
            
        except Exception as e:
            logger.warning(f"[{self.name}] Failed to extract tags: {str(e)}")
            return []