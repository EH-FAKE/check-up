from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import EntryItem
from plog import logger


class CidadeVerdePlay(BasePlay):
    name = "cidadeverde"

    @classmethod
    def match(cls, url: str) -> bool:
        return "cidadeverde.com" in url

    def pre_run(self):
        # Não há necessidade de login ou preparação especial conhecida
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p, viewport={"width": 1600, "height": 1000})
            page = browser.new_page()

            # Bloqueia recursos pesados e domínios de anúncios para acelerar
            blocked_domains = (
                "doubleclick.net",
                "googlesyndication.com",
                "google-analytics.com",
                "analytics.google.com",
                "clarity.ms",
                "tailtarget.com",
                "flashtalking.com",
                "googletagmanager.com",
            )

            def block_ads(route, request):
                try:
                    if request.resource_type in {"image", "media", "font", "stylesheet"}:
                        return route.abort()
                    if any(d in request.url for d in blocked_domains):
                        return route.abort()
                except Exception:
                    pass
                return route.continue_()

            page.route("**/*", block_ads)
            page.set_default_navigation_timeout(60_000)
            page.set_default_timeout(20_000)

            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, wait_until="domcontentloaded", timeout=60_000)

            # Espera pelo título principal se possível
            try:
                page.wait_for_selector("h1", timeout=15_000)
            except Exception:
                pass

            # Título
            title = ""
            # Seletores genéricos e alguns comuns em sites de notícias
            for selector in [
                ".post-title",
                "article h1",
                "h1",
                
            ]:
                try:
                    if selector.startswith("meta["):
                        el = page.locator(selector)
                        if el.count() > 0:
                            content = el.first.get_attribute("content") or ""
                            content = content.strip()
                            if content:
                                title = content
                                logger.info(f"[{self.name}] Title from '{selector}'")
                                break
                        continue

                    el = page.locator(selector)
                    if el.count() > 0:
                        title = el.first.inner_text().strip()
                        if title:
                            logger.info(f"[{self.name}] Title from '{selector}'")
                            break
                except Exception:
                    continue

            if not title:
                try:
                    title = page.title().strip()
                except Exception:
                    title = ""

            # Descrição
            description = ""
            for selector in [
                ".post-subtitle"
                "article h2",
                "header h2",
            ]:
                try:
                    if selector.startswith("meta["):
                        el = page.locator(selector)
                        if el.count() > 0:
                            content = el.first.get_attribute("content") or ""
                            content = content.strip()
                            if content:
                                description = content
                                logger.info(f"[{self.name}] Description from '{selector}'")
                                break
                        continue

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
                ".post-body",
                "article .post-body",
                "article .post-body p",
                "article p",
            ]:
                try:
                    els = page.locator(selector)
                    count = els.count()
                    if count == 0:
                        continue

                    if count > 1:
                        parts = []
                        for i in range(count):
                            t = els.nth(i).inner_text().strip()
                            # Ignora parágrafos que começam com "Foto: "
                            if t and not t.startswith("Foto: "):
                                parts.append(t)
                        body = "\n\n".join(parts).strip()
                    else:
                        first_text = els.first.inner_text().strip()
                        if first_text.startswith("Foto: "):
                            first_text = ""
                        body = first_text

                    if body and len(body) > 100:
                        logger.info(
                            f"[{self.name}] Body from '{selector}' (len={len(body)})"
                        )
                        break
                except Exception:
                    continue

            # Tags
            tags = []
            for selector in [
                ".tags a",
                ".tags li a",
                ".tags li",
            ]:
                try:
                    els = page.locator(selector)
                    n = els.count()
                    if n == 0:
                        continue
                    for i in range(n):
                        t = els.nth(i).inner_text().strip()
                        if t and t not in tags:
                            tags.append(t)
                    if tags:
                        logger.info(
                            f"[{self.name}] {len(tags)} tags from '{selector}'"
                        )
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
