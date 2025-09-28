import time
from playwright.sync_api import sync_playwright
from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class BrasilDeFatoPlay(BasePlay):
    name = "brasildefato"

    @classmethod
    def match(cls, url):
        """Identifica se a URL é do Brasil de Fato"""
        return "brasildefato.com.br" in url

    def pre_run(self):
        """Configurações antes da execução"""
        pass

    def run(self) -> EntryItem:
        """Extrai conteúdo da notícia do Brasil de Fato"""
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()

            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)

            # Aguardar carregamento do conteúdo principal
            try:
                page.wait_for_selector("h1", timeout=30000)
            except Exception as e:
                logger.warning(f"[{self.name}] Timeout waiting for h1: {str(e)}")

            # Extrair todos os campos
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
            "h1",
            ".post-title h1",
            ".article-title h1",
            ".entry-title h1"
        ]

        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    title = element.first.inner_text().strip()
                    if title:
                        logger.info(f"[{self.name}] Successfully extracted title using: {selector}")
                        return title
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract title with {selector}: {str(e)}")
                continue

        logger.error(f"[{self.name}] Failed to extract title")
        return ""

    def _extract_description(self, page):
        """Extrai a descrição/subtítulo da notícia"""
        selectors = [
            "h1 + h2",  # H2 que vem logo após o H1
            "h2",  # Qualquer H2 como subtítulo
            ".subtitle",
            ".lead",
            ".summary",
            ".article-subtitle",
            ".post-subtitle",
            ".excerpt"
        ]

        for selector in selectors:
            try:
                element = page.locator(selector)
                if element.count() > 0:
                    description = element.first.inner_text().strip()
                    if description and len(description) > 20:  # Evitar textos muito curtos
                        logger.info(f"[{self.name}] Successfully extracted description using: {selector}")
                        return description
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract description with {selector}: {str(e)}")
                continue

        logger.info(f"[{self.name}] No description found")
        return ""

    def _extract_body(self, page):
        """Extrai o corpo da notícia"""
        selectors = [
            ".post-content p",  # Parágrafos do conteúdo
            ".article-content p",
            ".entry-content p",
            ".content p",
            "article p",
            ".text p",
            ".article-body p"
        ]

        for selector in selectors:
            try:
                elements = page.locator(selector)
                if elements.count() > 0:
                    # Extrair todos os parágrafos
                    paragraphs = []
                    for i in range(elements.count()):
                        paragraph = elements.nth(i).inner_text().strip()
                        if paragraph and len(paragraph) > 10:  # Evitar parágrafos muito curtos
                            paragraphs.append(paragraph)

                    if paragraphs:
                        body = '\n\n'.join(paragraphs)
                        logger.info(f"[{self.name}] Successfully extracted body using: {selector}")
                        return body
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract body with {selector}: {str(e)}")
                continue

        # Fallback: tentar extrair todo o texto após os títulos
        try:
            # Extrair texto do corpo principal, excluindo header/footer
            all_text = page.locator("body").inner_text()
            lines = all_text.split('\n')

            # Encontrar onde começa o conteúdo real (após a data/autor)
            content_lines = []
            start_content = False

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Identificar início do conteúdo (geralmente após informações de data/autor)
                if ('27.SET.2025' in line or 'REDAÇÃO' in line or 'Editado por:' in line):
                    start_content = True
                    continue

                if start_content and len(line) > 50:  # Linhas substanciais
                    content_lines.append(line)

            if content_lines:
                body = '\n\n'.join(content_lines[:10])  # Primeiros 10 parágrafos
                logger.info(f"[{self.name}] Extracted body using fallback method")
                return body

        except Exception as e:
            logger.warning(f"[{self.name}] Fallback body extraction failed: {str(e)}")

        logger.error(f"[{self.name}] Failed to extract body")
        return ""

    def _extract_tags(self, page):
        """Extrai as tags/categorias da notícia"""
        selectors = [
            ".tags a",
            ".categories a",
            ".post-tags a",
            ".article-tags a",
            "[rel='tag']",
            ".tag-list a",
            ".category-list a"
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
                        logger.info(f"[{self.name}] Successfully extracted {len(tags)} tags using: {selector}")
                        break
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract tags with {selector}: {str(e)}")
                continue

        # Fallback: extrair seção da notícia (ex: "SUL GLOBAL", "POLÍTICA", etc.)
        if not tags:
            try:
                # Procurar pela seção que aparece antes do título
                section_selectors = [
                    "h1 + *:contains('GLOBAL')",
                    "h1 + *:contains('POLÍTICA')",
                    "h1 + *:contains('INTERNACIONAL')",
                    ".section-name",
                    ".category-name"
                ]

                # Método alternativo: extrair da URL
                url_parts = self.url.split('/')
                if len(url_parts) >= 4:
                    # Pode haver uma seção na URL
                    potential_section = url_parts[-2] if url_parts[-1] == '' else None
                    if potential_section and len(potential_section) > 3:
                        tags.append(potential_section.replace('-', ' ').title())

            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract fallback tags: {str(e)}")

        if not tags:
            logger.info(f"[{self.name}] No tags found")

        return tags