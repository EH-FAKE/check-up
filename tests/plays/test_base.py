import pytest
from freezegun import freeze_time
from unittest.mock import Mock, patch, MagicMock

from plays.base import BasePlay
from plays import (
    ClicRBSPlay,
    EstadaoPlay,
    FolhaPlay,
    GloboPlay,
    IGPlay,
    MetropolesPlay,
    R7Play,
    VejaPlay,
    TerraPlay,
    UOLPlay
)
from plays.exceptions import ScraperNotFoundError


class TestBasePlay:
    def test_return_correct_scraper_folha(self):
        url = "https://www1.folha.uol.com.br/mundo/2024/05/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, FolhaPlay)
        assert scraper.url == url

    def test_return_correct_scraper_estadao(self):
        url = "https://www.estadao.com.br/economia/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, EstadaoPlay)
        assert scraper.url == url

    def test_return_correct_scraper_veja(self):
        url = "https://veja.abril.com.br/economia/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, VejaPlay)
        assert scraper.url == url

    def test_return_correct_scraper_uol(self):
        url = "https://noticias.uol.com.br/cotidiano/ultimas-noticias/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, UOLPlay)
        assert scraper.url == url

    def test_return_correct_scraper_globo(self):
        url = "https://oglobo.globo.com/economia/noticia/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, GloboPlay)
        assert scraper.url == url

    def test_return_correct_scraper_terra(self):
        url = "https://www.terra.com.br/esportes/futebol/internacional/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, TerraPlay)
        assert scraper.url == url

    def test_return_correct_scraper_metropoles(self):
        url = "https://www.metropoles.com/brasil/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, MetropolesPlay)
        assert scraper.url == url

    def test_return_correct_scraper_clic_rbs(self):
        url = "https://gauchazh.clicrbs.com.br/ambiente/noticia/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, ClicRBSPlay)
        assert scraper.url == url

    def test_return_correct_scraper_ig(self):
        url = "https://ultimosegundo.ig.com.br/brasil/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, IGPlay)
        assert scraper.url == url

    def test_return_correct_scraper_r7(self):
        url = "https://noticias.r7.com/cidades/entry-slug"

        scraper = BasePlay.get_scraper(url)

        assert isinstance(scraper, R7Play)
        assert scraper.url == url

    def test_raise_error_if_no_scraper_is_found(self):
        url = "https://any.com.br"

        with pytest.raises(ScraperNotFoundError):
            BasePlay.get_scraper(url)

    @freeze_time("2024-05-15 12:00:00")
    def test_get_session(self):
        url = "https://entry-url.com"

        scraper = BasePlay(url, session_dir="/tmp/session")

        assert scraper.get_session_dir() == "/tmp/session"

    @freeze_time("2024-05-15 12:00:00")
    def test_get_session_when_not_given(self):
        url = "https://entry-url.com"

        scraper = BasePlay(url)

        assert scraper.get_session_dir() == "./sessions/base_session/"

    # --- Novos Testes para Otimizações ---

    def test_timeout_seconds_configuration(self):
        """Testa se timeout_seconds é configurado corretamente."""
        # Teste com timeout customizado
        play = BasePlay("https://test.com", timeout_seconds=300)
        assert play.timeout_seconds == 300
        
        # Teste com valor padrão
        play_default = BasePlay("https://test.com")
        assert play_default.timeout_seconds == 600

    def test_wait_time_configuration(self):
        """Testa configuração de wait_time."""
        # Teste com wait_time customizado
        play = BasePlay("https://test.com", wait_time=5)
        assert play.wait_time == 5
        
        # Teste com valor padrão
        play_default = BasePlay("https://test.com")
        assert play_default.wait_time == 3

    def test_firefox_optimized_settings(self):
        """Testa se as configurações otimizadas do Firefox estão sendo aplicadas."""
        play = BasePlay("https://test.com")
        
        with patch('plays.base.sync_playwright') as mock_playwright:
            mock_p = Mock()
            mock_browser = Mock()
            mock_playwright.return_value.__enter__.return_value = mock_p
            mock_p.firefox.launch_persistent_context.return_value = mock_browser
            
            play.launch_browser(mock_p)
            
            # Verifica se foi chamado com argumentos corretos
            call_args = mock_p.firefox.launch_persistent_context.call_args
            
            # Verifica viewport otimizado
            assert call_args[1]['viewport'] == {"width": 1920, "height": 1080}
            
            # Verifica configurações específicas do Firefox
            firefox_prefs = call_args[1]['firefox_user_prefs']
            assert firefox_prefs['javascript.enabled'] is True
            assert firefox_prefs['browser.cache.disk.enable'] is True
            assert firefox_prefs['browser.cache.memory.capacity'] == 65536  # 64MB
            assert firefox_prefs['dom.webdriver.enabled'] is False
            assert firefox_prefs['network.http.max-connections'] == 96

    def test_firefox_cache_optimization(self):
        """Testa configurações específicas de cache do Firefox."""
        play = BasePlay("https://test.com")
        
        with patch('plays.base.sync_playwright') as mock_playwright:
            mock_p = Mock()
            mock_browser = Mock()
            mock_playwright.return_value.__enter__.return_value = mock_p
            mock_p.firefox.launch_persistent_context.return_value = mock_browser
            
            play.launch_browser(mock_p)
            
            firefox_prefs = mock_p.firefox.launch_persistent_context.call_args[1]['firefox_user_prefs']
            
            # Verifica configurações de cache
            assert firefox_prefs['browser.sessionhistory.max_entries'] == 10
            assert firefox_prefs['dom.max_script_run_time'] == 60
            assert firefox_prefs['media.autoplay.default'] == 0

    def test_proxy_configuration(self):
        """Testa configuração de proxy."""
        proxy_config = {
            "server": "http://proxy.example.com:8080",
            "username": "user",
            "password": "pass"
        }
        
        play = BasePlay("https://test.com", proxy=proxy_config)
        
        with patch('plays.base.sync_playwright') as mock_playwright:
            mock_p = Mock()
            mock_browser = Mock()
            mock_playwright.return_value.__enter__.return_value = mock_p
            mock_p.firefox.launch_persistent_context.return_value = mock_browser
            
            play.launch_browser(mock_p)
            
            # Verifica se proxy foi configurado
            call_args = mock_p.firefox.launch_persistent_context.call_args
            assert call_args[1]['proxy'] == proxy_config

    def test_scroll_down_functionality(self):
        """Testa a funcionalidade de scroll otimizada."""
        play = BasePlay("https://test.com")
        mock_page = Mock()
        
        with patch('time.sleep'):
            play.scroll_down(mock_page, n=3, amount=500, wait_time=0.5)
        
        # Verifica se o scroll foi chamado 3 vezes
        assert mock_page.mouse.wheel.call_count == 3
        mock_page.mouse.wheel.assert_called_with(0, 500)

    def test_take_screenshot_with_retry_mechanism(self):
        """Testa o sistema de retry no take_screenshot."""
        play = BasePlay("https://test.com")
        mock_page = Mock()
        
        # Simula falha na primeira tentativa, sucesso na segunda
        mock_page.screenshot.side_effect = [Exception("First fail"), None, None]
        mock_page.evaluate.return_value = 1000
        mock_page.viewport_size = {"height": 800}
        
        with patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=50000), \
             patch('time.sleep'):
            
            result = play.take_screenshot(mock_page, "test.png", goto=False)
            
            # Verifica se tentou retry
            assert mock_page.screenshot.call_count == 2
            assert result is not None

    def test_take_screenshot_file_size_validation(self):
        """Testa validação de tamanho do arquivo de screenshot."""
        play = BasePlay("https://test.com")
        mock_page = Mock()
        mock_page.evaluate.return_value = 1000
        mock_page.viewport_size = {"height": 800}
        
        with patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', side_effect=[5000, 60000]), \
             patch('os.remove') as mock_remove, \
             patch('time.sleep'):
            
            mock_page.screenshot.side_effect = [None, None]
            
            result = play.take_screenshot(mock_page, "test.png", goto=False)
            
            # Verifica se arquivo pequeno foi removido e retry executado
            mock_remove.assert_called()
            assert mock_page.screenshot.call_count == 2

    def test_take_screenshot_intelligent_scrolling(self):
        """Testa scroll inteligente para posicionar anúncios."""
        play = BasePlay("https://test.com")
        mock_page = Mock()
        
        # Configura locators para anúncios
        mock_locator = Mock()
        mock_locator.count.return_value = 1
        mock_locator.first.is_visible.return_value = True
        mock_page.locator.return_value = mock_locator
        mock_page.evaluate.return_value = 2000
        mock_page.viewport_size = {"height": 800}
        
        with patch('os.makedirs'), \
             patch('os.path.exists', return_value=True), \
             patch('os.path.getsize', return_value=50000), \
             patch('time.sleep'):
            
            result = play.take_screenshot(mock_page, "test.png", goto=False)
            
            # Verifica se tentou encontrar seletores de anúncios
            expected_selectors = [
                "#taboola-below-article-thumbnails",
                "div[id^='taboola']",
                ".native-ad-container",
                ".sponsored-content",
                ".videoCube"
            ]
            
            locator_calls = [call[0][0] for call in mock_page.locator.call_args_list]
            assert any(selector in str(locator_calls) for selector in expected_selectors)

    def test_session_removal_when_allowed(self):
        """Testa remoção de sessão quando permitida."""
        play = BasePlay("https://test.com", allow_remove_session=True)
        
        with patch('shutil.rmtree') as mock_rmtree:
            play.remove_session()
            mock_rmtree.assert_called_once()

    def test_session_removal_when_not_allowed(self):
        """Testa que sessão não é removida quando não permitido."""
        play = BasePlay("https://test.com", allow_remove_session=False)
        
        with patch('shutil.rmtree') as mock_rmtree:
            play.remove_session()
            mock_rmtree.assert_not_called()

    def test_timeout_configuration_with_kwargs(self):
        """Testa passagem de timeout_seconds via kwargs do get_scraper."""
        url = "https://gauchazh.clicrbs.com.br/test"
        
        scraper = BasePlay.get_scraper(url, timeout_seconds=300)
        
        assert isinstance(scraper, ClicRBSPlay)
        assert scraper.timeout_seconds == 300

    @pytest.mark.parametrize("headless_mode", [True, False])
    def test_headless_configuration(self, headless_mode):
        """Testa configuração de modo headless parametrizado."""
        play = BasePlay("https://test.com", headless=headless_mode)
        assert play.headless == headless_mode

    def test_retries_configuration(self):
        """Testa configuração de número de retries."""
        play = BasePlay("https://test.com", retries=5)
        assert play.retries == 5
        
        # Valor padrão
        play_default = BasePlay("https://test.com")
        assert play_default.retries == 3

    def test_screenshot_error_handling(self):
        """Testa tratamento de erro no screenshot quando todas as tentativas falham."""
        play = BasePlay("https://test.com")
        mock_page = Mock()
        
        # Simula falha em todas as tentativas
        mock_page.screenshot.side_effect = [Exception("Fail")] * 3
        mock_page.evaluate.return_value = 1000
        mock_page.viewport_size = {"height": 800}
        
        with patch('os.makedirs'), \
             patch('time.sleep'):
            
            result = play.take_screenshot(mock_page, "test.png", goto=False)
            
            # Deve retornar None quando todas as tentativas falham
            assert result is None
            assert mock_page.screenshot.call_count == 3

    def test_extra_kwargs_method(self):
        """Testa método extra_kwargs com implementação padrão."""
        result = BasePlay.extra_kwargs()
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_match_method_not_implemented(self):
        """Testa que método match não implementado levanta NotImplementedError."""
        with pytest.raises(NotImplementedError):
            BasePlay.match("https://test.com")

    def test_pre_run_method_not_implemented(self):
        """Testa que método pre_run não implementado levanta NotImplementedError."""
        play = BasePlay("https://test.com")
        with pytest.raises(NotImplementedError):
            play.pre_run()

    def test_run_method_not_implemented(self):
        """Testa que método run não implementado levanta NotImplementedError."""
        play = BasePlay("https://test.com")
        with pytest.raises(NotImplementedError):
            play.run()
