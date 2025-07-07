import hashlib
import shutil
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List
import hashlib
from pathlib import Path

from playwright.sync_api import TimeoutError as PlayWrightTimeoutError
from playwright.sync_api import sync_playwright

from plays.exceptions import ScraperNotFoundError
from plays.items import EntryItem
from plays.timeout import PlayerTimeoutError
from plog import logger


class BasePlay:
    name = "base"

    def __init__(
        self,
        url,
        session_dir=None,
        proxy=None,
        wait_time=3,
        headless=True,
        retries=3,
        allow_remove_session=True,
        timeout_seconds=600,
    ):
        self.url = url
        self.session_dir = session_dir
        self.proxy = proxy
        self.wait_time = wait_time
        self.headless = headless
        self.retries = retries
        self.allow_remove_session = allow_remove_session
        self.timeout_seconds = timeout_seconds

    @classmethod
    def match(cls, url):
        raise NotImplementedError()

    @classmethod
    def extra_kwargs(cls):
        return dict()

    @classmethod
    def get_scraper(cls, url, *args, **kwargs):
        scrapers = cls.__subclasses__()
        for scraper in scrapers:
            if scraper.match(url):
                merged_kwargs = {**kwargs, **scraper.extra_kwargs()}
                return scraper(url, *args, **merged_kwargs)

        raise ScraperNotFoundError(f"No scraper was found for url '{url}'")

    def get_session_dir(self):
        if self.session_dir is None:
            return f"./sessions/{self.name}_session/"

        return self.session_dir

    def scroll_down(self, page, n, amount=300, wait_time=1):
        for _ in range(n):
            page.mouse.wheel(0, amount)
            time.sleep(wait_time)

    def launch_browser(self, playwright_obj, use_proxy=True, *args, **kwargs):
        logger.info(f"[{self.name}] Launching browser...'")
        
        default_args = {
            "viewport": {"width": 1920, "height": 1080},
            "bypass_csp": True, 
            "ignore_https_errors": True,
            "firefox_user_prefs": {
                "javascript.enabled": True,
                "browser.cache.disk.enable": True,
                "browser.cache.memory.capacity": 65536, 
                "browser.sessionhistory.max_entries": 10,
                "dom.max_script_run_time": 60, 
                "media.autoplay.default": 0, 
                "media.autoplay.blocking_policy": 0,
                "network.http.max-connections": 96,
                "dom.webdriver.enabled": False,
                "network.http.rendering-critical-requests.enabled": True,
                "permissions.default.image": 1,
            }
        }
        merged_args = {**default_args, **kwargs}
        
        if self.proxy is not None and use_proxy:
            logger.info(f"[{self.name}] Using proxy")
            return playwright_obj.firefox.launch_persistent_context(
                self.get_session_dir(),
                headless=self.headless,
                proxy=self.proxy,
                *args,
                **merged_args,
            )
        return playwright_obj.firefox.launch_persistent_context(
            self.get_session_dir(),
            headless=self.headless,
            *args,
            **merged_args,
        )
    def take_screenshot(self, page, url: str, goto: bool = True) -> str:
        """
        Tira um screenshot da página atual (ou navega para a URL se `goto=True`)
        e salva com base no hash da URL.
        """
        if goto:
            page.goto(url)

        url_hash = hashlib.md5(url.encode()).hexdigest()
        screenshot_dir = Path("./screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshot_dir / f"{self.name}_{url_hash}.png"
        page.screenshot(path=str(screenshot_path))

        logger.info(f"[{self.name}] Screenshot saved to {screenshot_path}")
        return str(screenshot_path)

    def take_screenshot(self, page, url: str, goto: bool = True) -> str:
        """
        Tira um screenshot da página atual (ou navega para a URL se `goto=True`)
        e salva com base no hash da URL.
        """
        if goto:
            page.goto(url)

        url_hash = hashlib.md5(url.encode()).hexdigest()
        screenshot_dir = Path("./screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshot_dir / f"{self.name}_{url_hash}.png"
        page.screenshot(path=str(screenshot_path))

        logger.info(f"[{self.name}] Screenshot saved to {screenshot_path}")
        return str(screenshot_path)

    def remove_session(self):
        if self.allow_remove_session:
            try:
                logger.info(f"[{self.name}] Removing session...")
                shutil.rmtree(self.get_session_dir())
                logger.info(f"[{self.name}] Done!")
            except Exception:
                logger.error(
                    f"[{self.name}] Error deleting session dir: '{self.get_session_dir()}'"
                )
        else:
            logger.info(f"[{self.name}] Removing session not allowed...")

    def pre_run(self):
        raise NotImplementedError()

    def post_run(self, output):
        return output

    def run(self):
        raise NotImplementedError()

    def execute(self, retries=2):
        entry_item = None
        self.pre_run()
        while entry_item is None and retries >= 0:
            try:
                entry_item = self.run()
                logger.info(f"[{self.name}]: Successfully scraped content.")
            except PlayWrightTimeoutError as exc:
                logger.error(str(exc))
            except PlayerTimeoutError as exc:
                logger.error(str(exc))

            if entry_item is None:
                logger.warning(
                    f"[{self.name}] Failed to scrape content. Trying again. Remaining {retries}"
                )
                self.remove_session()
                retries -= 1

        if entry_item is None:
            raise Exception(
                f"[{self.name}] Failed to scrape content from '{self.url}'")

        entry_item = self.post_run(entry_item)
        return entry_item

    def take_screenshot(self, page, filename, goto=True, timeout=180_000):
        """Captura screenshot da página com nome único e carregamento completo."""
        import hashlib
        import os
        import random
        import time
        
        try:
            os.makedirs("screenshots", exist_ok=True)
            
            if "http" in filename:
                filename_clean = filename.replace("://", "_").replace("/", "_").replace(".", "_")
                url_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
                timestamp = int(time.time())
                file_path = f"screenshots/{filename_clean[:50]}_{url_hash}_{timestamp}.png"
            else:
                file_path = f"screenshots/{filename}" if filename.endswith(".png") else f"screenshots/{filename}.png"

            if goto and "http" in filename:
                page.goto(filename, timeout=timeout)
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=min(timeout, 30000))
                    page.wait_for_load_state("networkidle", timeout=min(timeout, 30000))
                except Exception as e:
                    logger.warning(f"[{self.name}] Timeout ao aguardar carregamento: {str(e)}")
                
                time.sleep(1)
            
            try:
                page_height = page.evaluate("document.body.scrollHeight")
                if page_height < 100:
                    logger.warning(f"[{self.name}] Página com altura muito pequena, aguardando...")
                    time.sleep(2)
            except:
                pass
            
            # Scroll inteligente para anúncios
            try:
                total_height = page.evaluate("document.body.scrollHeight")
                viewport_height = page.viewport_size["height"]
                
                if total_height > viewport_height * 1.5:
                    ad_selectors = [
                        "#taboola-below-article-thumbnails", 
                        "div[id^='taboola']",
                        ".native-ad-container",
                        ".sponsored-content",
                        ".videoCube"
                    ]
                    
                    ad_found = False
                    for selector in ad_selectors:
                        try:
                            elements = page.locator(selector)
                            if elements.count() > 0 and elements.first.is_visible():
                                elements.first.scroll_into_view_if_needed()
                                time.sleep(1)
                                ad_found = True
                                logger.info(f"[{self.name}] Anúncio encontrado, capturando área com anúncios")
                                break
                        except:
                            continue
                    
                    if not ad_found:
                        max_scroll = total_height - viewport_height
                        scroll_positions = [0, random.randint(viewport_height, max(viewport_height, max_scroll - viewport_height)), max_scroll]
                        weights = [0.2, 0.6, 0.2]
                        scroll_position = random.choices(scroll_positions, weights=weights)[0]
                        page.evaluate(f"window.scrollTo(0, {scroll_position})")
                        time.sleep(0.5)
                        
            except Exception as e:
                logger.debug(f"[{self.name}] Erro ao calcular posição de scroll: {str(e)}")
            
            # Captura com validação
            for attempt in range(3):
                try:
                    page.screenshot(path=file_path, timeout=10000)
                    
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        if file_size > 10000:
                            logger.info(f"[{self.name}] Screenshot salvo em {file_path} ({file_size} bytes)")
                            return file_path
                        else:
                            logger.warning(f"[{self.name}] Screenshot muito pequeno, tentativa {attempt + 1}/3")
                            os.remove(file_path)
                            
                            if attempt < 2:
                                time.sleep(2)
                                page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                                time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"[{self.name}] Erro ao capturar screenshot (tentativa {attempt + 1}): {str(e)}")
                    if attempt < 2:
                        time.sleep(1)
            
            logger.error(f"[{self.name}] Falha ao capturar screenshot após 3 tentativas")
            return None
                
        except Exception as e:
            logger.error(f"[{self.name}] Erro geral ao capturar screenshot: {str(e)}")
            return None
