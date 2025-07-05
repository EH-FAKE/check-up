import time

from playwright.sync_api import sync_playwright

from plays.base import BasePlay
from plays.items import AdItem, EntryItem
from plays.utils import get_or_none
from plog import logger


class ClicRBSPlay(BasePlay):
    name = "clicrbs"
    n_expected_ads = 8

    @classmethod
    def match(cls, url):
        return "clicrbs.com.br" in url or "gauchazh.clicrbs.com.br" in url

    def find_items(self, html_content) -> AdItem:
        """Extrai informações dos anúncios usando get_or_none."""
        return AdItem(
            title=get_or_none(r'title="([^"]+)"', html_content) or 
                  get_or_none(r'<span class="video-title[^>]*>([^<]+)<', html_content) or
                  get_or_none(r'<div class="video-title[^>]*>([^<]+)<', html_content) or
                  get_or_none(r'<h[1-4][^>]*>([^<]+)<', html_content),
            
            url=get_or_none(r'href="([^"]+)"', html_content) or
                get_or_none(r'data-url="([^"]+)"', html_content) or
                get_or_none(r'data-target-url="([^"]+)"', html_content),
            
            thumbnail_url=get_or_none(r'url\(&quot;([^&]+)&quot;\)', html_content) or
                         get_or_none(r'data-src="([^"]+)"', html_content) or
                         get_or_none(r'src="([^"]+)"', html_content) or
                         get_or_none(r'background-image:\s*url\([\'"]?([^\'"]+)[\'"]?\)', html_content),
            
            tag=get_or_none(r'<span class="branding-inner[^>]*>([^<]+)<', html_content) or
                get_or_none(r'<span class="video-title-text[^>]*>([^<]+)<', html_content) or
                get_or_none(r'<span class="brand[^>]*>([^<]+)<', html_content),
            
            excerpt=get_or_none(r'slot="description" title="([^"]+)"', html_content) or
                   get_or_none(r'<span class="syndicatedItem-description[^>]*>([^<]+)<', html_content) or
                   get_or_none(r'<p class="description[^>]*>([^<]+)<', html_content),
        )

    def pre_run(self):
        """Configurações iniciais antes da execução principal."""
        logger.info(f"[{self.name}] Iniciando processamento para {self.url}")

    def run(self) -> EntryItem:
        """Executa o scraping da página."""
        with sync_playwright() as p:
            browser = self.launch_browser(p)
            page = browser.new_page()
            
            try:
                logger.info(f"[{self.name}] Opening URL '{self.url}'...")
                page.goto(self.url, timeout=180_000)
                
                # Wait for page load
                page.wait_for_load_state("domcontentloaded")
                time.sleep(self.wait_time)
                
                # Extract title
                entry_title = ""
                title_selectors = ["h1.article-title", "h1.content-head__title", "article h1", "h1"]
                
                for selector in title_selectors:
                    try:
                        title_element = page.locator(selector).first
                        if title_element.is_visible():
                            entry_title = title_element.inner_text().strip()
                            break
                    except:
                        continue
                        
                if not entry_title:
                    entry_title = page.locator("head title").inner_text().strip()
                
                logger.info(f"[{self.name}] Searching for ads...")
                
                # Scroll to find ads
                ads_containers = [
                    "#taboola-below-article-thumbnails-new", 
                    "#taboola-below-article-thumbnails",
                    "div[id^='taboola']",
                    ".videoCube",
                    ".trc_spotlight_item"
                ]
                
                ads_found = False
                for container in ads_containers:
                    try:
                        if page.locator(container).count() > 0:
                            page.locator(container).scroll_into_view_if_needed()
                            ads_found = True
                            break
                    except:
                        continue
                
                if not ads_found:
                    # Scroll down to trigger ad loading
                    self.scroll_down(page, 3, amount=400, wait_time=1)
                
                time.sleep(self.wait_time)
                
                # Extract ads
                ad_items = []
                ads_selectors = [
                    ".videoCube", 
                    ".trc_spotlight_item",
                    ".syndicatedItem",
                    "div[id^='taboola'] a"
                ]
                
                for selector in ads_selectors:
                    try:
                        elements = page.locator(selector)
                        for i in range(elements.count()):
                            element = elements.nth(i)
                            if not element.is_visible():
                                continue
                            
                            html_content = element.inner_html()
                            ad_item = self.find_items(html_content)
                            
                            if ad_item and ad_item.is_valid():
                                ad_items.append(ad_item)
                                
                            if len(ad_items) >= self.n_expected_ads:
                                break
                        
                        if len(ad_items) >= self.n_expected_ads:
                            break
                            
                    except Exception as e:
                        logger.debug(f"[{self.name}] Error with selector {selector}: {str(e)}")
                
                # Extract basic metadata
                description = ""
                try:
                    desc_selectors = [
                        'meta[name="description"]',
                        'meta[property="og:description"]'
                    ]
                    for selector in desc_selectors:
                        element = page.locator(selector).first
                        if element:
                            description = element.get_attribute("content") or ""
                            if description:
                                break
                except:
                    pass
                
                # Extract tags
                tags = []
                try:
                    tag_selectors = [
                        ".breadcrumb a", 
                        ".article-tags a", 
                        ".tags a"
                    ]
                    for selector in tag_selectors:
                        elements = page.locator(selector)
                        for i in range(min(elements.count(), 8)):
                            tag_text = elements.nth(i).inner_text().strip()
                            if tag_text and len(tag_text) > 2 and "HOME" not in tag_text.upper():
                                tags.append(tag_text)
                        if tags:
                            break
                except:
                    pass
                
                # Take screenshot
                screenshot_path = self.take_screenshot(page, self.url, goto=False)
                
                logger.info(f"[{self.name}] Found {len(ad_items)} ads")
                
                return EntryItem(
                    title=entry_title,
                    url=self.url,
                    ads=ad_items,
                    screenshot_path=screenshot_path,
                    description=description,
                    tags=tags,
                )
                
            except Exception as e:
                logger.error(f"[{self.name}] Error during scraping: {str(e)}")
                
                # Try to capture error screenshot
                error_screenshot = None
                try:
                    error_screenshot = self.take_screenshot(page, self.url, goto=False)
                except:
                    pass
                
                return EntryItem(
                    title=f"Error: {str(e)}",
                    url=self.url,
                    ads=[],
                    screenshot_path=error_screenshot,
                    tags=[]
                )
            finally:
                browser.close()
