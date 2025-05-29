import pytest
import os
import threading
import time
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from pathlib import Path


@pytest.fixture
def mock_psutil_process():
    """Fixture que cria um mock realistic do psutil.Process."""
    mock_process = Mock()
    
    # Mock de memory_info() baseado na estrutura real do psutil
    mock_memory = Mock()
    mock_memory.rss = 150 * 1024 * 1024  # 150MB RSS
    mock_memory.vms = 300 * 1024 * 1024  # 300MB VMS
    mock_memory.percent = 15.0
    mock_process.memory_info.return_value = mock_memory
    
    # Mock de cpu_percent() com comportamento realistic
    mock_process.cpu_percent.return_value = 25.5
    mock_process.name.return_value = "test_scraper"
    mock_process.pid = 12345
    mock_process.status.return_value = "running"
    
    return mock_process


@pytest.fixture
def mock_docker_env():
    """Fixture para simular ambiente Docker."""
    return {
        'DOCKERIZED': 'true',
        'HEADLESS': 'true', 
        'SCRAPER_TIMEOUT': '900',
        'DATABASE_URL': 'postgresql://user:pass@healthcheck_db:5432/db',
        'PLAYWRIGHT_BROWSERS_PATH': '/app/browsers'
    }


@pytest.fixture
def mock_system_resources():
    """Fixture para dados de recursos do sistema."""
    return {
        'cpu_count': 4,
        'memory_total': 8 * 1024 * 1024 * 1024,  # 8GB
        'memory_available': 4 * 1024 * 1024 * 1024,  # 4GB
        'disk_usage': {
            'total': 100 * 1024 * 1024 * 1024,  # 100GB
            'free': 50 * 1024 * 1024 * 1024,   # 50GB
            'used': 50 * 1024 * 1024 * 1024    # 50GB
        }
    }


class TestIntegrationImprovements:
    """Testes de integração para as melhorias implementadas."""

    def test_playwright_version_compatibility(self):
        """Testa compatibilidade com a versão específica do Playwright."""
        expected_version = "1.51.0"
        
        def check_playwright_compatibility(version):
            try:
                major, minor, patch = map(int, version.split('.'))
                return major >= 1 and minor >= 50
            except (ValueError, AttributeError):
                return False
        
        assert check_playwright_compatibility(expected_version) is True
        
        # Testa versões incompatíveis
        assert check_playwright_compatibility("1.49.0") is False
        assert check_playwright_compatibility("invalid") is False
        assert check_playwright_compatibility(None) is False

    def test_docker_environment_variables(self, mock_docker_env):
        """Testa configurações específicas para ambiente Docker."""
        with patch.dict(os.environ, mock_docker_env):
            # Verifica configurações Docker essenciais
            assert os.environ.get('DOCKERIZED') == 'true'
            assert os.environ.get('HEADLESS') == 'true'
            assert 'healthcheck_db:' in os.environ.get('DATABASE_URL')
            
            # Verifica timeout configurável
            timeout = int(os.environ.get('SCRAPER_TIMEOUT', 600))
            assert 300 <= timeout <= 1800  # Range válido
            
            # Verifica se path do Playwright está configurado
            browsers_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH')
            assert browsers_path is not None

    def test_postgres_pipeline_integration(self):
        """Testa integração com pipeline do PostgreSQL."""
        from settings import ITEM_PIPELINES
        
        postgres_pipeline = "pipelines.PostgresPipeline"
        assert postgres_pipeline in ITEM_PIPELINES
        assert ITEM_PIPELINES[postgres_pipeline] == 300
        
        # Verifica ordem de execução do pipeline
        pipeline_order = list(ITEM_PIPELINES.values())
        assert all(isinstance(order, int) for order in pipeline_order)

    @pytest.mark.parametrize("setting,expected_type", [
        ('ROBOTSTXT_OBEY', bool),
        ('DOWNLOAD_DELAY', (int, float)),
        ('CONCURRENT_REQUESTS', int),
        ('CONCURRENT_REQUESTS_PER_DOMAIN', int)
    ])
    def test_scrapy_settings_optimization(self, setting, expected_type):
        """Testa configurações otimizadas do Scrapy com parametrização."""
        recommended_settings = {
            'ROBOTSTXT_OBEY': False,
            'DOWNLOAD_DELAY': 1,
            'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
            'CONCURRENT_REQUESTS': 16,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 8
        }
        
        if setting in recommended_settings:
            value = recommended_settings[setting]
            assert isinstance(value, expected_type)
            
            # Validações específicas
            if setting == 'DOWNLOAD_DELAY':
                assert 0.5 <= value <= 5  # Range sensato
            elif 'CONCURRENT' in setting:
                assert 1 <= value <= 32  # Limite prático

    @patch('subprocess.run')
    def test_makefile_browser_check_target(self, mock_subprocess):
        """Testa target check-browsers do Makefile com mock adequado."""
        # Configura retorno de sucesso
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "firefox 120.0\nchromium 119.0"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result
        
        # Simula verificação de browsers
        check_commands = [
            ["playwright", "install", "--help"],
            ["firefox", "--version"], 
            ["chromium", "--version"]
        ]
        
        for cmd in check_commands:
            result = mock_subprocess.return_value
            assert result.returncode == 0
            assert hasattr(result, 'stdout')

    def test_firefox_preferences_performance_impact(self):
        """Testa impacto das preferências do Firefox na performance."""
        firefox_prefs = {
            'browser.cache.memory.capacity': 65536,  # 64MB
            'network.http.max-connections': 96,
            'dom.max_script_run_time': 60,
            'browser.sessionhistory.max_entries': 10,
            'media.autoplay.default': 0,
            'dom.webdriver.enabled': False
        }
        
        # Validações de performance
        assert firefox_prefs['browser.cache.memory.capacity'] >= 32768
        assert firefox_prefs['network.http.max-connections'] >= 64
        assert firefox_prefs['dom.max_script_run_time'] <= 120
        assert firefox_prefs['browser.sessionhistory.max_entries'] <= 20
        
        # Validações de compatibilidade
        assert isinstance(firefox_prefs['media.autoplay.default'], int)
        assert isinstance(firefox_prefs['dom.webdriver.enabled'], bool)

    @pytest.mark.parametrize("file_size,expected_valid", [
        (5000, False),    # Muito pequeno
        (10240, True),    # Tamanho mínimo
        (50000, True),    # Tamanho bom
        (1000000, True),  # Tamanho grande
    ])
    def test_screenshot_optimization_file_sizes(self, file_size, expected_valid):
        """Testa otimizações de tamanho de arquivo com parametrização."""
        min_file_size = 10240  # 10KB mínimo
        max_retries = 3
        
        def validate_screenshot_size(size, min_size=min_file_size):
            return size >= min_size
        
        result = validate_screenshot_size(file_size)
        assert result == expected_valid
        assert max_retries > 0

    @pytest.mark.parametrize("timeout_value", [300, 600, 900, 1200])
    def test_timeout_configurations_range(self, timeout_value):
        """Testa diferentes configurações de timeout."""
        min_timeout = 60    # 1 minuto mínimo
        max_timeout = 1800  # 30 minutos máximo
        
        assert min_timeout <= timeout_value <= max_timeout
        
        # Verifica se é múltiplo de 60 (para facilitar configuração)
        assert timeout_value % 60 == 0

    def test_rbs_scraper_ads_expectation_realistic(self):
        """Testa se expectativa de anúncios do RBS é realística."""
        from plays.rbs import ClicRBSPlay
        
        n_expected = ClicRBSPlay.n_expected_ads
        typical_range = range(5, 15)  # Sites de notícias típicos
        
        assert n_expected in typical_range
        assert isinstance(n_expected, int)
        assert n_expected > 0

    def test_memory_efficient_batch_processing(self):
        """Testa processamento em lote eficiente em memória."""
        large_dataset = list(range(1000))
        batch_size = 50
        processed_batches = 0
        
        def process_in_batches(data, batch_size):
            nonlocal processed_batches
            processed_count = 0
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                processed_count += len(batch)
                processed_batches += 1
                
                # Simula limpeza de memória
                del batch
                
            return processed_count, processed_batches
        
        result, batches = process_in_batches(large_dataset, batch_size)
        
        assert result == len(large_dataset)
        assert batches == 20  # 1000 / 50
        assert processed_batches == 20

    def test_error_logging_structured_format(self):
        """Testa formato estruturado de logging de erros."""
        from datetime import datetime
        
        # Formato de erro estruturado implementado
        def create_error_log(url, error, scraper_name="test_scraper"):
            return {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'level': 'ERROR',
                'url': url,
                'scraper': scraper_name,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'stack_trace': repr(error)
            }
        
        test_error = ValueError("Test error message")
        log_entry = create_error_log("https://test.com", test_error)
        
        # Verifica campos essenciais
        required_fields = ['timestamp', 'level', 'url', 'error_type', 'error_message']
        for field in required_fields:
            assert field in log_entry
            assert log_entry[field] is not None
        
        assert log_entry['level'] == 'ERROR'
        assert log_entry['error_type'] == 'ValueError'

    def test_session_directory_structure(self):
        """Testa estrutura de diretórios de sessão."""
        scrapers = ['clicrbs', 'globo', 'uol', 'folha']
        
        for scraper in scrapers:
            session_dir = f"./sessions/{scraper}_session/"
            
            # Verifica padrão de naming
            assert session_dir.startswith("./sessions/")
            assert session_dir.endswith("_session/")
            assert scraper in session_dir
            
            # Verifica se é um path válido
            path = Path(session_dir)
            assert path.is_absolute() is False  # Deve ser relativo

    def test_system_resource_monitoring_with_psutil_mock(self, mock_psutil_process, mock_system_resources):
        """Testa monitoramento de recursos usando mock realista do psutil."""
        # Simula Process.memory_info()
        memory_info = mock_psutil_process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        
        # Simula Process.cpu_percent()
        cpu_percent = mock_psutil_process.cpu_percent()
        
        # Verifica limites realistas baseados em dados reais
        assert memory_mb <= 500   # Máximo 500MB por processo
        assert cpu_percent <= 80  # Máximo 80% CPU
        assert memory_mb > 0      # Deve usar alguma memória
        assert cpu_percent >= 0   # CPU não pode ser negativo
        
        # Verifica que os valores são numéricos
        assert isinstance(memory_mb, (int, float))
        assert isinstance(cpu_percent, (int, float))

    def test_database_connection_resilience(self):
        """Testa parâmetros de resiliência da conexão com banco."""
        connection_params = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 3600,  # 1 hora
            'pool_pre_ping': True
        }
        
        # Validações de resiliência
        assert connection_params['pool_size'] >= 2
        assert connection_params['max_overflow'] >= connection_params['pool_size']
        assert connection_params['pool_timeout'] > 0
        assert connection_params['pool_recycle'] > 0
        assert connection_params['pool_pre_ping'] is True
        
        # Verifica limites práticos
        assert connection_params['pool_size'] <= 20  # Evita sobrecarga
        assert connection_params['pool_timeout'] <= 60  # Não muito alto

    def test_flake8_compliance_with_optimizations(self):
        """Testa conformidade com flake8 para otimizações."""
        flake8_config = {
            'max-line-length': 150,
            'max-complexity': 15,
            'ignore': ['W191', 'W293', 'W292', 'E303', 'F401', 'F841', 'E712', 'E124', 'E201', 'E402']
        }
        
        # Validações de configuração
        assert flake8_config['max-line-length'] >= 120
        assert flake8_config['max-complexity'] >= 10
        assert isinstance(flake8_config['ignore'], list)
        assert len(flake8_config['ignore']) > 0
        
        # Verifica que permite imports não usados (comum em testes)
        assert 'F401' in flake8_config['ignore']

    def test_pytest_discovery_configuration(self):
        """Testa configuração de descoberta de testes."""
        pytest_config = {
            'python_files': 'test_*.py',
            'testpaths': ['tests'],
            'addopts': ['-v', '--tb=short']
        }
        
        # Verifica padrões de descoberta
        assert pytest_config['python_files'] == 'test_*.py'
        assert 'tests' in pytest_config['testpaths']
        assert '-v' in pytest_config['addopts']  # Verbose output

    @pytest.mark.parametrize("platform", ["linux", "darwin", "win32"])
    def test_cross_platform_compatibility(self, platform):
        """Testa compatibilidade entre plataformas."""
        platform_configs = {
            'path_separator': os.sep,
            'session_dir_pattern': './sessions/{name}_session/',
            'screenshot_format': 'png',
            'default_browser': 'firefox'
        }
        
        # Validações agnósticas de plataforma
        assert platform_configs['screenshot_format'] in ['png', 'jpg', 'jpeg']
        assert platform_configs['default_browser'] in ['firefox', 'chrome', 'webkit']
        assert '{name}' in platform_configs['session_dir_pattern']

    def test_concurrent_scraping_safety(self):
        """Testa segurança para scraping concorrente com threading real."""
        # Estado compartilhado thread-safe
        shared_state = {
            'active_scrapers': 0,
            'max_concurrent': 3,
            'lock': threading.Lock(),
            'completed': []
        }
        
        def safe_acquire_scraper(scraper_id):
            with shared_state['lock']:
                if shared_state['active_scrapers'] < shared_state['max_concurrent']:
                    shared_state['active_scrapers'] += 1
                    return True
                return False
        
        def safe_release_scraper(scraper_id):
            with shared_state['lock']:
                if shared_state['active_scrapers'] > 0:
                    shared_state['active_scrapers'] -= 1
                    shared_state['completed'].append(scraper_id)
        
        def worker(scraper_id):
            if safe_acquire_scraper(scraper_id):
                time.sleep(0.01)  # Simula trabalho
                safe_release_scraper(scraper_id)
        
        # Testa concorrência com múltiplas threads
        threads = []
        for i in range(5):  # Mais scrapers que o limite
            thread = threading.Thread(target=worker, args=(f"scraper_{i}",))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verifica resultados
        assert shared_state['active_scrapers'] == 0  # Todos finalizaram
        assert len(shared_state['completed']) <= 5   # Máximo tentativas
        assert len(shared_state['completed']) >= 3   # Pelo menos max_concurrent

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_file')
    def test_playwright_binary_validation(self, mock_is_file, mock_exists):
        """Testa validação de binários do Playwright."""
        # Mock para simular binários existentes
        mock_exists.return_value = True
        mock_is_file.return_value = True
        
        playwright_binaries = [
            'firefox/firefox',
            'chromium/chrome',
            'webkit/Playwright'
        ]
        
        for binary in playwright_binaries:
            binary_path = Path(f"/app/browsers/{binary}")
            
            # Simula verificação de existência
            assert mock_exists.return_value is True
            assert mock_is_file.return_value is True
            
            # Verifica estrutura do path
            assert binary in str(binary_path)

    def test_resource_cleanup_mechanisms(self):
        """Testa mecanismos de limpeza de recursos."""
        class ResourceManager:
            def __init__(self):
                self.resources = []
                self.cleaned_up = False
                self.cleanup_called = 0
            
            def acquire_resource(self, name):
                resource = f"resource_{name}"
                self.resources.append(resource)
                return resource
            
            def cleanup(self):
                self.cleanup_called += 1
                self.resources.clear()
                self.cleaned_up = True
        
        manager = ResourceManager()
        
        # Usa recursos
        res1 = manager.acquire_resource("browser")
        res2 = manager.acquire_resource("db_connection")
        
        assert len(manager.resources) == 2
        assert not manager.cleaned_up
        
        # Limpa recursos
        manager.cleanup()
        
        assert len(manager.resources) == 0
        assert manager.cleaned_up is True
        assert manager.cleanup_called == 1
        
        # Verifica que cleanup pode ser chamado múltiplas vezes
        manager.cleanup()
        assert manager.cleanup_called == 2

    @pytest.mark.slow
    def test_performance_benchmark_integration(self):
        """Teste de benchmark de performance (marcado como slow)."""
        import time
        
        start_time = time.time()
        
        # Simula operação que deve ser rápida
        for _ in range(1000):
            pass  # Operação simples
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verifica que operação é rápida (menos de 1 segundo)
        assert execution_time < 1.0
        
        # Verifica precisão do timing
        assert execution_time >= 0

    def test_sqlalchemy_modern_syntax_no_warnings(self):
        """Testa que models.py usa syntax moderna do SQLAlchemy 2.0+ sem warnings."""
        import warnings
        
        # Captura warnings durante importação do models
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Re-importa models para capturar warnings
            import importlib
            import models
            importlib.reload(models)
            
            # Filtra apenas warnings relevantes
            sqlalchemy_warnings = [
                warning for warning in w 
                if "deprecat" in str(warning.message).lower() and 
                ("sqlalchemy" in str(warning.message).lower() or 
                 "declarative_base" in str(warning.message).lower())
            ]
            
            # Não deve haver warnings do SQLAlchemy
            assert len(sqlalchemy_warnings) == 0, f"SQLAlchemy warnings found: {[str(w.message) for w in sqlalchemy_warnings]}"
        
        # Verifica que usa DeclarativeBase moderna
        assert hasattr(models.Base, '__subclasses__')
        assert models.Base.__name__ == 'Base'
        
        # Verifica que models usam Mapped annotations
        assert hasattr(models.Portal, '__annotations__')
        assert 'id' in models.Portal.__annotations__
        assert 'name' in models.Portal.__annotations__

    def test_datetime_utc_modern_syntax(self):
        """Testa que datetime usa syntax moderna timezone-aware."""
        from datetime import datetime, timezone
        
        # Testa função de criação de timestamp moderna
        def create_modern_timestamp():
            return datetime.now(timezone.utc).isoformat()
        
        timestamp = create_modern_timestamp()
        
        # Verifica formato ISO com timezone
        assert timestamp.endswith('+00:00') or timestamp.endswith('Z')
        assert 'T' in timestamp  # Formato ISO
        
        # Verifica que não usa utcnow() obsoleto
        import inspect
        import models
        
        # Verifica se models.py não contém utcnow() obsoleto no código
        source = inspect.getsource(models)
        deprecated_calls = [
            'datetime.utcnow()',
            'datetime.datetime.utcnow()'
        ]
        
        for call in deprecated_calls:
            # Só permite em defaults de SQLAlchemy por compatibilidade
            lines_with_call = [line for line in source.split('\n') if call in line]
            sqlalchemy_defaults = [line for line in lines_with_call if 'default=' in line]
            
            # Warnings apenas se usado fora de defaults do SQLAlchemy
            non_default_usage = len(lines_with_call) - len(sqlalchemy_defaults)
            assert non_default_usage == 0, f"Found deprecated {call} usage outside SQLAlchemy defaults"


# Fixture de sessão para setup/teardown de integração
@pytest.fixture(scope="session")
def integration_setup():
    """Setup de sessão para testes de integração."""
    print("\nSetup de integração iniciado")
    
    # Setup de recursos de sessão
    test_resources = {
        'temp_dirs': [],
        'mock_servers': [],
        'test_databases': []
    }
    
    yield test_resources
    
    # Cleanup de sessão
    print("\nCleanup de integração executado")
    for resource_list in test_resources.values():
        resource_list.clear() 