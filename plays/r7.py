import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger


class R7Play(BasePlay):
    name = "r7"
    n_expected_ads = 20

    @classmethod
    def match(cls, url):
        return "r7.com" in url

    def find_items(self, html_content) -> AdItem:
        def clean(text):
            return text.strip() if text else None

        return AdItem(
            title=clean(get_or_none(r'title="(.*?)"', html_content)),
            url=clean(get_or_none(r'href="(.*?)"', html_content)),
            thumbnail_url=clean(get_or_none(r'url\(&quot;(.*?)&quot;\)', html_content)),
            tag=clean(get_or_none(r'<span class="branding-inner".*?>(.*?)<\/span>', html_content)),
            excerpt=clean(get_or_none(r'slot="description" title="(.*?)"', html_content)),
        )

    def pre_run(self):
        pass

    def run(self) -> EntryItem:
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            logger.info(f"[{self.name}] Opening URL '{self.url}'...")
            page.goto(self.url, timeout=180_000)
            logger.info(f"[{self.name}] Searching for ads...")

            entry_screenshot_path = self.take_screenshot(page, self.url, goto=False)
            entry_title = page.locator("head title").inner_text()

            self.scroll_down(page, 10, 400, wait_time=1)

            try:
                page.locator("#taboola-below-article-thumbnails").click()
                page.locator("#taboola-below-article-thumbnails").scroll_into_view_if_needed()
            except Exception:
                logger.warning(f"[{self.name}] Timeout or missing 'taboola-below-article-thumbnails'")

            time.sleep(self.wait_time)
            self.scroll_down(page, 30, 400, wait_time=1)

            elements = page.locator(".videoCube")
            ad_items = []
            for i in range(elements.count()):
                try:
                    element = elements.nth(i)
                    if not element.is_visible():
                        continue
                    content = element.inner_html()
                    ad_item = self.find_items(content)
                    if ad_item.title and ad_item.url:
                        ad_items.append(ad_item)
                    if len(ad_items) >= self.n_expected_ads:
                        break
                except Exception as e:
                    logger.warning(f"[{self.name}] Erro ao processar item #{i}: {e}")

            return EntryItem(
                title=entry_title,
                ads=ad_items,
                url=self.url,
                screenshot_path=entry_screenshot_path,
            )
