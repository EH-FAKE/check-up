import pytest
from unittest.mock import Mock
from plays.rbs import ClicRBSPlay
from plays.items import AdItem
from unittest.mock import patch


class TestClicRBSPlay:
    def test_match_valid_urls(self):
        """Testa se URLs válidas do RBS são reconhecidas."""
        valid_urls = [
            "https://www.clicrbs.com.br/",
            "https://gauchazh.clicrbs.com.br/",
            "https://gauchazh.clicrbs.com.br/ambiente/noticia/2024/01/test",
            "https://www.clicrbs.com.br/esportes/news"
        ]
        for url in valid_urls:
            assert ClicRBSPlay.match(url) is True

    def test_match_invalid_urls(self):
        """Testa se URLs inválidas são rejeitadas."""
        invalid_urls = [
            "https://globo.com/news",
            "https://uol.com.br/article", 
            "https://example.com",
            "https://other-site.com"
        ]
        for url in invalid_urls:
            assert ClicRBSPlay.match(url) is False

    def test_n_expected_ads_configuration(self):
        """Testa se o número esperado de anúncios está configurado corretamente."""
        assert ClicRBSPlay.n_expected_ads == 8

    def test_find_items_with_complete_html(self):
        """Testa extração de anúncios com HTML completo e válido."""
        play = ClicRBSPlay("https://test.clicrbs.com.br")
        
        html_content = '''
        <div class="videoCube">
            <a href="https://example.com/ad1" title="Test Ad Title">
                <img src="https://example.com/thumb1.jpg" alt="thumbnail">
                <span class="video-title">Test Ad Title</span>
            </a>
            <span class="branding-inner">Test Brand</span>
            <span slot="description" title="Test description content">Test description</span>
        </div>
        '''
        
        ad_item = play.find_items(html_content)
        
        assert isinstance(ad_item, AdItem)
        assert ad_item.title == "Test Ad Title"
        assert ad_item.url == "https://example.com/ad1"
        assert ad_item.thumbnail_url == "https://example.com/thumb1.jpg"
        assert ad_item.tag == "Test Brand"
        assert ad_item.excerpt == "Test description content"
        assert ad_item.is_valid() is True

    def test_find_items_with_fallback_selectors(self):
        """Testa se os seletores de fallback funcionam quando os primários falham."""
        play = ClicRBSPlay("https://test.clicrbs.com.br")
        
        # HTML que usa seletores alternativos (sem conflitos)
        html_content = '''
        <div>
            <div class="video-title">Fallback Title</div>
            <a data-url="https://fallback.com/ad">Fallback Link</a>
            <img data-src="https://fallback.jpg" alt="fallback thumb">
            <span class="branding-inner">Fallback Brand</span>
            <p class="description">Fallback description</p>
        </div>
        '''
        
        ad_item = play.find_items(html_content)
        
        assert ad_item.title == "Fallback Title"
        assert ad_item.url == "https://fallback.com/ad"
        assert ad_item.thumbnail_url == "https://fallback.jpg"
        assert ad_item.tag == "Fallback Brand"
        assert ad_item.excerpt == "Fallback description"

    def test_find_items_with_background_image_url(self):
        """Testa extração de thumbnail via background-image CSS."""
        play = ClicRBSPlay("https://test.clicrbs.com.br")
        
        html_content = '''
        <div style="background-image: url('https://bg-image.jpg')">
            <h3>Background Image Test</h3>
        </div>
        '''
        
        ad_item = play.find_items(html_content)
        
        assert ad_item.title == "Background Image Test"
        assert ad_item.thumbnail_url == "https://bg-image.jpg"

    def test_find_items_with_empty_html(self):
        """Testa comportamento com HTML vazio ou inválido."""
        play = ClicRBSPlay("https://test.clicrbs.com.br")
        
        ad_item = play.find_items("")
        
        assert isinstance(ad_item, AdItem)
        assert ad_item.title is None
        assert ad_item.url is None
        assert ad_item.thumbnail_url is None
        assert ad_item.tag is None
        assert ad_item.excerpt is None
        assert ad_item.is_valid() is False

    def test_find_items_with_partial_data(self):
        """Testa extração quando apenas alguns campos estão disponíveis."""
        play = ClicRBSPlay("https://test.clicrbs.com.br")
        
        html_content = '''
        <div>
            <h2>Only Title Available</h2>
            <a href="https://only-url.com">Only URL</a>
        </div>
        '''
        
        ad_item = play.find_items(html_content)
        
        assert ad_item.title == "Only Title Available"
        assert ad_item.url == "https://only-url.com"
        assert ad_item.thumbnail_url is None
        assert ad_item.tag is None
        assert ad_item.excerpt is None
        assert ad_item.is_valid() is True  # Válido com title e url

    def test_find_items_with_encoded_urls(self):
        """Testa extração de URLs com codificação HTML."""
        play = ClicRBSPlay("https://test.clicrbs.com.br")
        
        html_content = '''
        <div style="background-image: url(&quot;https://encoded.jpg&quot;)">
            <span>Encoded URL Test</span>
        </div>
        '''
        
        ad_item = play.find_items(html_content)
        
        assert ad_item.thumbnail_url == "https://encoded.jpg"

    def test_pre_run_method_logs_correctly(self):
        """Testa se o método pre_run faz o logging apropriado."""
        url = "https://test.clicrbs.com.br"
        play = ClicRBSPlay(url)
        
        # Mock do logger para capturar as chamadas
        with patch('plays.rbs.logger') as mock_logger:
            play.pre_run()
            
            # Verifica se logger.info foi chamado com a mensagem correta
            mock_logger.info.assert_called_once_with(f"[{play.name}] Iniciando processamento para {url}")

    @pytest.mark.parametrize("html_input,expected_title", [
        ('title="Param Title"', "Param Title"),
        ('<span class="video-title">Span Title</span>', "Span Title"),
        ('<h1>Header Title</h1>', "Header Title"),
        ('', None)
    ])
    def test_title_extraction_patterns(self, html_input, expected_title):
        """Testa diferentes padrões de extração de título usando parametrização."""
        play = ClicRBSPlay("https://test.clicrbs.com.br")
        ad_item = play.find_items(html_input)
        assert ad_item.title == expected_title

    @pytest.mark.parametrize("html_input,expected_url", [
        ('href="https://test1.com"', "https://test1.com"),
        ('data-url="https://test2.com"', "https://test2.com"),
        ('data-target-url="https://test3.com"', "https://test3.com"),
        ('no-url-here', None)
    ])
    def test_url_extraction_patterns(self, html_input, expected_url):
        """Testa diferentes padrões de extração de URL."""
        play = ClicRBSPlay("https://test.clicrbs.com.br")
        ad_item = play.find_items(html_input)
        assert ad_item.url == expected_url

    def test_class_properties(self):
        """Testa propriedades da classe ClicRBSPlay."""
        assert ClicRBSPlay.name == "clicrbs"
        assert hasattr(ClicRBSPlay, 'n_expected_ads')
        assert isinstance(ClicRBSPlay.n_expected_ads, int)
        assert ClicRBSPlay.n_expected_ads > 0

    def test_inheritance_from_base_play(self):
        """Testa se ClicRBSPlay herda corretamente de BasePlay."""
        from plays.base import BasePlay
        
        assert issubclass(ClicRBSPlay, BasePlay)
        
        # Verifica se métodos obrigatórios estão implementados
        play = ClicRBSPlay("https://test.com")
        assert hasattr(play, 'match')
        assert hasattr(play, 'find_items')
        assert hasattr(play, 'pre_run')
        assert callable(getattr(play, 'match'))
        assert callable(getattr(play, 'find_items'))
        assert callable(getattr(play, 'pre_run'))
        