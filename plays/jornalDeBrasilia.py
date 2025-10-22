from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class JornalDeBrasiliaPlay(BasePlay):
    name = "jornaldebrasilia"

    @classmethod
    def match(cls, url: str) -> bool:
        """Verifica se a URL pertence ao Jornal de Brasília."""
        return "jornaldebrasilia.com.br" in url

    def pre_run(self):
        """Método executado antes do 'run'."""
        logger.info(f"[{self.name}] Preparando para extrair a URL: {self.url}")

    def run(self) -> EntryItem:
        """Executa a extração principal dos dados da página."""
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page(
            )

            page.route(
                "**/*",
                lambda route: route.abort()
                if route.request.resource_type in {"image", "font", "media", "stylesheet"}
                else route.continue_(),
            )
            
            page.set_default_navigation_timeout(60_000)
            page.set_default_timeout(10_000) 

            try:
                page.goto(self.url, wait_until="domcontentloaded", timeout=60_000)
                page.wait_for_timeout(2000) 
            except PlaywrightTimeoutError:
                logger.error(f"[{self.name}] Timeout ao carregar a página: {self.url}")
                browser.close()
                return EntryItem(title="", url=self.url, description="", body="", tags=[])


            # Título
            title = ""
            title_selectors = [
                "h1.tdb-title-text",
                ".wrap-title > h1",
                "h1.title",
                "h1.entry-title",
                ".post-title",
                ".content-head__title",
                "h1" 
            ]
            for selector in title_selectors:
                try:
                    el = page.locator(selector).first
                    if el.is_visible(timeout=1000):
                        title = el.inner_text().strip()
                        if title:
                            logger.info(f"[{self.name}] Título encontrado com o seletor: '{selector}'")
                            break
                except Exception:
                    continue
            
            if not title:
                try:
                    title = page.title().strip().split("|")[0].strip()
                except Exception:
                    title = ""


            # Descrição (Subtítulo)
            description = ""
            description_selectors = [
                ".wrap-title > p:nth-child(2)",
                "p.tdb-post-sub-title",
                ".subtitle h2",
                "p.td-post-sub-title"
            ]
            for selector in description_selectors:
                try:
                    el = page.locator(selector).first
                    if el.is_visible(timeout=1000):
                        description = el.inner_text().strip()
                        if description:
                            logger.info(f"[{self.name}] Descrição encontrada com o seletor: '{selector}'")
                            break
                except Exception:
                    continue

            # Corpo da Notícia
            body = ""
            body_container_selectors = [
                "div.tdb-block-inner.td-fix-index",
                ".the-post-content",
                ".td-post-content"
            ]
            for selector in body_container_selectors:
                try:
                    container = page.locator(selector).first
                    if container.is_visible(timeout=1500):
                        logger.info(f"[{self.name}] Contêiner do corpo encontrado com o seletor: '{selector}'")
                        
                        # Extrai todos os parágrafos <p> de dentro do contêiner
                        paragraphs = container.locator("p")
                        parts = []
                        for i in range(paragraphs.count()):
                            p_text = paragraphs.nth(i).inner_text().strip()
                            # Filtro para remover parágrafos indesejados
                            if p_text and len(p_text) > 40 and not p_text.lower().startswith(("leia mais", ">>", "crédito:", "siga o jornal")):
                                parts.append(p_text)
                        
                        if parts:
                            body = "\n\n".join(parts)
                            logger.info(f"[{self.name}] Corpo extraído com sucesso! Caracteres: {len(body)}")
                            break # Sai do loop principal se o corpo foi extraído
                except Exception:
                    continue

            # Extração de Tags (opcional, pois nem sempre estão presentes)
            tags = []
            tag_selectors = [
                ".tdb-tags a",
                ".entities__list-item a",
                ".entities__list li a"
            ]
            for selector in tag_selectors:
                try:
                    tag_elements = page.locator(selector)
                    if tag_elements.count() > 0:
                        tag_list = [el.inner_text().strip() for el in tag_elements.all()]
                        tags = [t for t in tag_list if t] # Remove tags vazias
                        if tags:
                            logger.info(f"[{self.name}] {len(tags)} tags encontradas com o seletor: '{selector}'")
                            break
                except Exception:
                    continue
                
            browser.close()

            return EntryItem(
                title=title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )

