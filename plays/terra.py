from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class TerraPlay(BasePlay):
    name = "terra"

    @classmethod
    def match(cls, url):
        return "terra.com.br" in url

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1600, "height": 1000})
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)

            # Título
            title = ""
            for selector in [
                "h1",
                ".article-title",
                ".post-title",
                ".c-news__title",
            ]:
                try:
                    el = page.locator(selector)
                    if el.count() > 0:
                        title = el.first.inner_text().strip()
                        if title:
                            logger.info(f"[{self.name}] Title from '{selector}'")
                            break
                except Exception:
                    continue

            # Descrição
            description = ""
            for selector in [
                "h2",
                ".article-subtitle",
                ".c-news__subtitle",
            ]:
                try:
                    el = page.locator(selector)
                    if el.count() > 0:
                        description = el.first.inner_text().strip()
                        if description:
                            logger.info(f"[{self.name}] Description from '{selector}'")
                            break
                except Exception:
                    continue

            # Corpo da notícia
            body = ""
            for selector in [
                ".article__content--body p, .article__content--body h2",
                ".article__content--body",       
                ".article__content",
                ".content",
                ".c-news__body",
            ]:
                try:
                    els = page.locator(selector)
                    count = els.count()
                    if count > 0:
                        if count > 1:
                            parts = []
                            for i in range(count):
                                t = els.nth(i).inner_text().strip()
                                if t:
                                    parts.append(t)
                            body = "\n\n".join(parts).strip()
                        else:
                            body = els.first.inner_text().strip()
                        if body and len(body) > 100:
                            logger.info(f"[{self.name}] Body from '{selector}' (len={len(body)})")
                            break
                except Exception:
                    continue

            # Tags
            tags = []
            for selector in [
                ".t360-tags__list a",
                ".t360-tags__list"
            ]:
                try:
                    els = page.locator(selector)
                    if els.count() > 0:
                        for i in range(els.count()):
                            t = els.nth(i).inner_text().strip()
                            if t and t not in tags:
                                tags.append(t)
                        if tags:
                            logger.info(f"[{self.name}] {len(tags)} tags from '{selector}'")
                            break
                except Exception:
                    continue

            return EntryItem(
                title=title,
                url=self.url,
                description=description,
                body=body,
                tags=tags,
            )
