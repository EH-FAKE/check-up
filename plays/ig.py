from playwright.sync_api import TimeoutError, sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class IGPlay(BasePlay):
    name = "ig"

    @classmethod
    def match(cls, url: str) -> bool:
        return "ig.com.br" in url

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(
                p, viewport={"width": 1920, "height": 1080})
            page = browser.new_page()

            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            try:
                page.goto(self.url, timeout=180_000)
            except TimeoutError:
                logger.error(f"[{self.name}] Timeout loading page {self.url}")
                return EntryItem(title="Timeout", url=self.url)

            # espera pelo título principal da notícia
            page.wait_for_selector("h1", timeout=30000)
            if page.locator("h1"):
                # extrai o título principal da notícia
                entry_title = page.locator("//h1").first.inner_text()
            else:
                # Espera pelo título específico a partir do id do selector
                page.wait_for_selector("#noticia-titulo-h1", timeout=30000)
                if page.locator("#noticia-titulo-h1"):
                    # extrai titulo pelo id do selector
                    entry_title = page.locator(
                        "#noticia-titulo-h1").first.inner_text()

            # Subtítulo / descrição
            description = ""
            try:
                description = page.locator("#noticia-olho").inner_text()
            except Exception:
                logger.warning(f"[{self.name}] Failed to extract description")

            # Corpo da notícia
            body = ""
            try:
                selectors = [
                    "#conteudoNoticia p",
                    "#noticia p",
                    "#noticiaTexto p",
                    ".noticia-body.not-cropped p",
                    "div[itemprop='articleBody'] p",
                    "div.post-content.cf.entry-content.content-spacious p",
                    "article .post-content p",
                ]
                for selector in selectors:
                    try:
                        logger.info(
                            f"[{self.name}] Trying selector: {selector}")

                        # Espera o primeiro parágrafo desse seletor, se possível
                        page.wait_for_selector(selector, timeout=5000)

                        content_elements = page.locator(selector)
                        count = content_elements.count()
                        logger.debug(
                            f"[{self.name}] Found {count} elements for {selector}")

                        if count > 0:
                            paragraphs = []
                            for i in range(count):
                                text = content_elements.nth(
                                    i).inner_text().strip()
                                if text:
                                    paragraphs.append(text)
                            body = "\n\n".join(paragraphs)
                            if body.strip():
                                logger.info(
                                    f"[{self.name}] Extracted body with {selector}")
                                break
                    except Exception as e:
                        logger.debug(
                            f"[{self.name}] Selector {selector} failed: {e}")
                if not body.strip():
                    logger.warning(
                        f"[{self.name}] Could not extract body content")
            except Exception as e:
                logger.warning(f"[{self.name}] Error extracting body: {e}")

            # Tags (caso existam)
            tags = []
            try:
                tag_elements = page.locator(".tags a")
                if tag_elements.count() > 0:
                    for i in range(tag_elements.count()):
                        tag_text = tag_elements.nth(i).inner_text().strip()
                        if tag_text:
                            tags.append(tag_text)
                else:
                    # Fallback: pegar do <meta property="article:tag" content="...">
                    meta_tag = page.locator('meta[property="article:tag"]')
                    if meta_tag.count() > 0:
                        content = meta_tag.first.get_attribute("content")
                        if content:
                            tags = [tag.strip()
                                    for tag in content.split(",") if tag.strip()]
            except Exception as e:
                logger.warning(f"[{self.name}] Failed to extract tags: {e}")

            return EntryItem(
                title=entry_title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )

    def execute(self) -> EntryItem:
        return self.run()
