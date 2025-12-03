from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class CartaCapitalPlay(BasePlay):
    name = "cartacapital"

    @classmethod
    def match(cls, url: str) -> bool:
        return "cartacapital.com.br" in url

    def run(self) -> EntryItem:
        """
        Abre a página da notícia, extrai título, descrição, corpo e tags
        e devolve um EntryItem.
        """
        with sync_playwright() as p:
            browser = self.launch_browser(
                p,
                viewport={"width": 1366, "height": 768},
            )
            page = browser.new_page()

            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000, wait_until="networkidle")

            title = self._extract_title(page)
            description = self._extract_description(page)
            body = self._extract_body(page)
            tags = self._extract_tags(page)

            browser.close()

            return EntryItem(
                title=title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )

    def _extract_title(self, page) -> str:
        """
        CartaCapital tem título principal em <h1>.
        """
        selectors = [
            "article h1",
            "main h1",
            "h1.entry-title",
            "h1",
        ]

        for selector in selectors:
            try:
                locator = page.locator(selector)
                if locator.count() > 0:
                    text = locator.first.inner_text().strip()
                    if text:
                        logger.info(f"[{self.name}] Title extracted: {text[:80]}...")
                        return text
            except Exception as exc:
                logger.warning(
                    f"[{self.name}] Failed to extract title with '{selector}': {exc}"
                )

        logger.error(f"[{self.name}] Failed to extract title")
        return ""

    def _extract_description(self, page) -> str:
        """
        Subtítulo / linha de apoio (se existir).
        Se não achar, cai no primeiro parágrafo do corpo.
        """
        selectors = [
            ".subtitle",
            ".sub-title",
            ".lead",
            ".summary",
            ".excerpt",
        ]

        for selector in selectors:
            try:
                locator = page.locator(selector)
                if locator.count() > 0:
                    text = locator.first.inner_text().strip()
                    if text and len(text) > 20:
                        logger.info(
                            f"[{self.name}] Description extracted: {text[:80]}..."
                        )
                        return text
            except Exception as exc:
                logger.warning(
                    f"[{self.name}] Failed to extract description with '{selector}': {exc}"
                )

        first_paragraph = self._first_paragraph(page)
        if first_paragraph:
            logger.info(
                f"[{self.name}] Description fallback from first paragraph: "
                f"{first_paragraph[:80]}..."
            )
        return first_paragraph

    def _first_paragraph(self, page) -> str:
        """
        Pega o primeiro parágrafo "decente" do artigo.
        """
        try:
            locator = page.locator("article p")
            if locator.count() == 0:
                locator = page.locator("main article p")
            if locator.count() == 0:
                locator = page.locator("main p")

            for i in range(locator.count()):
                text = locator.nth(i).inner_text().strip()
                if text and len(text) > 40:
                    return text
        except Exception:
            pass
        return ""

    def _extract_body(self, page) -> str:
        """
        Extrai o texto completo do corpo da matéria.
        """
        selectors = [
            "article .entry-content",
            "article .post-content",
            "article .content",
            "article",
            "main article",
        ]

        for selector in selectors:
            try:
                locator = page.locator(selector)
                if locator.count() == 0:
                    continue

                root = locator.first

                try:
                    root.locator(
                        "script, style, .ad, .advertisement, nav, footer"
                    ).evaluate_all("els => els.forEach(e => e.remove())")
                except Exception:
                    pass

                text = root.inner_text().strip()
                if text and len(text) > 200:
                    logger.info(
                        f"[{self.name}] Body extracted ({len(text)} chars)"
                    )
                    return text
            except Exception as exc:
                logger.warning(
                    f"[{self.name}] Failed to extract body with '{selector}': {exc}"
                )

        logger.error(f"[{self.name}] Failed to extract body")
        return ""

    def _extract_tags(self, page) -> list[str]:
        """
        Extrai tags/tópicos se houver bloco de tags.
        Na CartaCapital geralmente aparecem como links em blocos de 'ENTENDA MAIS SOBRE', etc.
        """
        selectors = [
            ".tags a",
            ".post-tags a",
            ".article-tags a",
            ".c-tags a",
            "[rel='tag']",
        ]

        tags: list[str] = []

        for selector in selectors:
            try:
                loc = page.locator(selector)
                count = loc.count()
                if count == 0:
                    continue

                for i in range(count):
                    tag_text = loc.nth(i).inner_text().strip()
                    if tag_text and tag_text not in tags:
                        tags.append(tag_text)
            except Exception as exc:
                logger.warning(
                    f"[{self.name}] Failed to extract tags with '{selector}': {exc}"
                )

        return tags
