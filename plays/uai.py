import time
from playwright.sync_api import sync_playwright
from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger

class UaiPlay(BasePlay):
    name = "uai"

    @classmethod
    def match(cls, url):
        return "uai.com.br" in url or "em.com.br" in url or "vrum.com.br" in url

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
            ".title h1",
            ".article-title h1",
            ".news-title h1",
            ".post-title h1",
            "header h1",
            ".entry-title h1",
            ".headline h1"
        ]
        
        for selector in title_selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    title = element.first.inner_text().strip()
                    if title and len(title) > 5:
                        logger.info(f"[{self.name}] Título extraído usando: {selector}")
                        return title
            except Exception as e:
                logger.warning(f"[{self.name}] Erro ao extrair título com {selector}: {str(e)}")
                continue
        
        try:
            title = page.locator("head title").inner_text().strip()
            if " - " in title:
                title = title.split(" - ")[0].strip()
            if title and len(title) > 5:
                logger.info(f"[{self.name}] Título extraído da tag title")
                return title
        except Exception:
            pass
        
        logger.error(f"[{self.name}] Falha ao extrair título")
        return ""

    def _extract_description(self, page):
        description_selectors = [
            "h2",
            ".subtitle",
            ".article-subtitle",
            ".news-subtitle",
            ".post-subtitle",
            ".lead",
            ".summary",
            ".excerpt",
            "header h2",
            ".entry-subtitle",
            ".deck",
            "meta[name='description']"
        ]
        
        for selector in description_selectors:
            try:
                if selector == "meta[name='description']":
                    element = page.locator(selector)
                    if element.count() > 0:
                        description = element.first.get_attribute("content") 
                        if description and len(description.strip()) > 10:
                            logger.info(f"[{self.name}] Descrição extraída de meta description")
                            return description.strip()
                else:
                    element = page.locator(selector)
                    if element.count() > 0:
                        description = element.first.inner_text().strip()
                        if description and len(description) > 10:
                            logger.info(f"[{self.name}] Descrição extraída usando: {selector}")
                            return description
            except Exception as e:
                logger.warning(f"[{self.name}] Erro ao extrair descrição com {selector}: {str(e)}")
                continue
        
        logger.info(f"[{self.name}] Nenhuma descrição encontrada")
        return ""

    def _extract_body(self, page):
        body_selectors = [
            "[class*='post']",
            "article",
            ".article-content",
            ".article-body", 
            ".post-content",
            ".news-content",
            ".content",
            ".text",
            ".story-body",
            "main",
            ".entry-content",
            ".body-content",
            ".single-content",
            ".post-body", 
            ".news-text",
            ".description",
            "section",
            "[class*='content']",
            "[class*='text']",
            "main article",
            "div.text",
            "p"
        ]
        
        for selector in body_selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    unwanted_selectors = [
                        "script", "style", "noscript", "iframe", "embed",
                        ".ad", ".advertisement", ".ads", ".banner", ".promo",
                        ".social-share", ".share", ".related", ".sidebar",
                        ".comments", ".newsletter", ".subscription"
                    ]
                    
                    for unwanted in unwanted_selectors:
                        try:
                            element.locator(unwanted).evaluate_all("nodes => nodes.forEach(node => node.remove())")
                        except:
                            pass
                    
                    body = element.first.inner_text().strip()
                    
                    body = self._clean_text(body)
                    
                    if body and len(body) > 200:
                        logger.info(f"[{self.name}] Corpo extraído usando: {selector} ({len(body)} chars)")
                        return body
            except Exception as e:
                logger.warning(f"[{self.name}] Erro ao extrair corpo com {selector}: {str(e)}")
                continue
        
        try:
            paragraphs = page.locator("p").all()
            if len(paragraphs) > 3:
                body_parts = []
                for p in paragraphs:
                    try:
                        text = p.inner_text().strip()
                        if text and len(text) > 50:
                            body_parts.append(text)
                    except:
                        continue
                
                if body_parts and len(body_parts) >= 3:
                    body = "\n\n".join(body_parts)
                    body = self._clean_text(body)
                    
                    if len(body) > 200:
                        logger.info(f"[{self.name}] Corpo extraído de parágrafos múltiplos ({len(body)} chars)")
                        return body
        except Exception as e:
            logger.warning(f"[{self.name}] Erro no fallback de parágrafos: {str(e)}")
        
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
                    for i in range(elements.count()):
                        try:
                            tag_text = elements.nth(i).inner_text().strip()
                            if tag_text and tag_text not in tags and len(tag_text) < 50:
                                if not any(skip in tag_text.lower() for skip in ['home', 'início', 'voltar', 'mais']):
                                    tags.append(tag_text)
                        except:
                            continue
                    
                    if tags:
                        logger.info(f"[{self.name}] Tags extraídas usando: {selector}")
                        break
            except Exception as e:
                logger.warning(f"[{self.name}] Erro ao extrair tags com {selector}: {str(e)}")
                continue
        
        if not tags:
            try:
                path_segments = [seg for seg in self.url.split('/') if seg and seg not in ['https:', 'www.uai.com.br', 'noticias']]
                if path_segments:
                    for segment in path_segments[:-1]:
                        if len(segment) > 2 and '-' not in segment:
                            tags.append(segment.replace('-', ' ').title())
                    
                    if tags:
                        logger.info(f"[{self.name}] Tags extraídas da URL: {tags}")
            except:
                pass
        
        return tags

    def _clean_text(self, text):
        if not text:
            return ""
        
        import re
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\r\n\t]+', ' ', text)
        
        lines = text.split('.')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not line.isdigit():
                cleaned_lines.append(line)
        
        return '. '.join(cleaned_lines).strip()
